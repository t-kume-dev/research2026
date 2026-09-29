"""Trigno Discover が書き出した CSV を Recording に変換する。

Delsys API のキーが届くまでの代わりに、Discover で記録 → CSV 書き出し → ここで .npz にする。
変換後は API で取った記録と同じように recalib / normalize / plot が使える。

CSV の形（Trigno Discover 2.1.0.7 で確認）:
  1〜3 行目  アプリ名、日時、記録の長さ
  4 行目     センサ名（"Avanti Sensor 3 (89563)"）。チャネルごとに 2 列ずつ
  6 行目     列名（"EMG 1 Time Series (s)", "EMG 1 (mV)"）
  7 行目     サンプリング周波数（", 2148.1481 Hz"）
  8 行目     サンプル間隔と、右側にマーカー表の見出し（Type, Name, Label, Time (s), ...）
  9 行目〜   左側: チャネルごとに「時刻, 値」の列ペア / 右側: マーカー（Type = General の行）

マーカーが 2 つ以上あれば、最初と最後のマーカーの間だけを切り出す。
センサ番号と部位の対応は、同じフォルダの sensors.json に書く:
  {"前腕の上（伸筋群）": 3, "前腕の下（屈筋群）": 0}
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np

from .recording import Recording
from .sources import ChannelInfo

SENSOR_TABLE = "sensors.json"


def load_sensor_table(path: Path) -> dict[int, str]:
    """sensors.json（部位 → センサ番号）を読み、センサ番号 → 部位 にして返す。"""
    if not Path(path).exists():
        return {}
    table = json.loads(Path(path).read_text(encoding="utf-8"))
    return {int(num): label for label, num in table.items()}


def _sensor_number(sensor: str) -> int | None:
    m = re.search(r"Sensor\s+(\d+)", sensor)
    return int(m.group(1)) if m else None


def _channel_name(sensor: str, column: str, labels: dict[int, str]) -> tuple[str, str]:
    """(チャネル名, 種類) を返す。例 ("前腕の上（伸筋群）", "EMG") / ("S3_EMG1", "EMG")。"""
    head = column.split("(")[0].strip()          # "EMG 1"
    ctype = head.split()[0] if head else "UNKNOWN"
    token = head.replace(" ", "")                 # "EMG1"
    num = _sensor_number(sensor)
    if num in labels:
        return (labels[num] if token == "EMG1" else f"{labels[num]}_{token}"), ctype
    return (f"S{num}_{token}" if num is not None else token), ctype


def read_discover_csv(path: Path, labels: dict[int, str] | None = None, crop: bool = True) -> Recording:
    path = Path(path)
    labels = labels or {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or not rows[0] or "Trigno Discover" not in ",".join(rows[0]):
        raise ValueError(f"Trigno Discover の CSV ではなさそうです: {path}")

    info = {r[0].strip().rstrip(":"): r[1].strip() for r in rows[:3] if len(r) > 1}
    sensors, columns, fs_row, marker_head = rows[3], rows[5], rows[6], rows[7]
    body = rows[8:]

    # チャネル: 列名が "... Time Series (s)" の列と、その右隣の値の列がペア
    pairs = [k for k in range(0, len(columns) - 1, 2) if "Time Series" in columns[k]]
    channels, data = [], {}
    for k in pairs:
        sensor = sensors[k].strip()
        name, ctype = _channel_name(sensor, columns[k + 1].strip(), labels)
        fs = float(fs_row[k + 1].split()[0])
        t = np.array([float(r[k]) for r in body if len(r) > k + 1 and r[k].strip()])
        x = np.array([float(r[k + 1]) for r in body if len(r) > k + 1 and r[k].strip()])
        channels.append(ChannelInfo(name, ctype, fs, sensor))
        data[name] = (t, x)

    # マーカー: 見出し行の "Type" 列から右がマーカー表
    markers = []
    if "Type" in [c.strip() for c in marker_head]:
        ti = [c.strip() for c in marker_head].index("Type")
        for r in body:
            if len(r) > ti + 3 and r[ti].strip():
                markers.append({"name": r[ti + 1].strip(), "time_s": float(r[ti + 3])})
    markers.sort(key=lambda m: m["time_s"])

    t0, t1 = None, None
    if crop and len(markers) >= 2:
        t0, t1 = markers[0]["time_s"], markers[-1]["time_s"]
    out = {}
    for name, (t, x) in data.items():
        out[name] = x[(t >= t0) & (t <= t1)] if t0 is not None else x

    meta = {
        "source": "TrignoDiscoverCSV",
        "file": path.name,
        "application": info.get("Application", ""),
        "started": info.get("Date/Time", ""),
        "units": "mV",
        "markers": markers,
        "crop_s": [t0, t1] if t0 is not None else None,
    }
    return Recording(channels, out, path.stem, meta)


def import_dir(session_dir: Path, crop: bool = True) -> list[Path]:
    """フォルダ内の *.csv をすべて同じ名前の .npz に変換する。"""
    session_dir = Path(session_dir)
    labels = load_sensor_table(session_dir / SENSOR_TABLE)
    saved = []
    for p in sorted(session_dir.glob("*.csv")):
        rec = read_discover_csv(p, labels, crop)
        saved.append(rec.save(p.with_suffix(".npz")))
        span = rec.meta["crop_s"]
        where = f"{span[0]:.1f}〜{span[1]:.1f} 秒を切り出し" if span else "全体"
        lens = ", ".join(f"{c.name} {rec.data[c.name].size / c.fs:.1f} s" for c in rec.channels)
        print(f"  {p.name} → {p.with_suffix('.npz').name}（{where}）: {lens}")
    if not labels:
        print(f"  メモ: {SENSOR_TABLE} がないので、チャネル名はセンサ番号のまま（S3_EMG1 など）")
    return saved
