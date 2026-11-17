"""KovaaK's（FPSAimTrainer）の結果の CSV を、記録のフォルダに取り込み、マウスの記録と時刻を合わせる。

KovaaK's はシナリオが終わるたびに `stats/<シナリオ> - Challenge - YYYY.MM.DD-HH.MM.SS Stats.csv` を書く。
ファイル名の日時はシナリオが終わった時刻。中身は次の 3 つのかたまり（間は空行）:
  1. 倒した的ごとの行: Kill #, Timestamp（HH:MM:SS.mmm、PC の時計。日付なし）, ..., Shots, Hits, ...
  2. 武器ごとの合計: Weapon, Shots, Hits, ...
  3. "名前:,値" の行: Score, Challenge Start, Pause Count, DPI, Horiz Sens など

取り込みの決まり（生データは解析の前に手元に集め、あとから書き換えない）:
  - 記録している間に始まったシナリオの CSV を、セッションの kovaaks/ にコピーする（日時は保つ）
  - 元の CSV には手を付けない。コピー先に同じ名前があれば上書きしない
  - 何をどこからコピーしたかと中身のハッシュ（SHA-256）を kovaaks/<記録名>_import.json に残す
  - マウスの記録の .csv / .json は書き換えない
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

# よくある置き場所。見つからなければ --stats-dir か環境変数 KOVAAKS_STATS で渡す
STATS_DIR_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"),
    Path(r"D:\SteamLibrary\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"),
    Path(r"E:\SteamLibrary\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"),
]


def find_stats_dir(arg: str | None = None) -> Path | None:
    for p in [arg, os.environ.get("KOVAAKS_STATS"), *STATS_DIR_CANDIDATES]:
        if p and Path(p).is_dir():
            return Path(p)
    return None


@dataclass
class Run:
    """KovaaK's の 1 回ぶんの結果。時刻はすべて UNIX 時刻 [s]（PC の時計）。"""
    path: Path
    scenario: str
    end: float                 # ファイル名の日時（シナリオが終わった時刻）
    start: float               # Challenge Start
    kills: np.ndarray          # 倒した時刻
    shots_per_kill: np.ndarray
    total_shots: int
    info: dict = field(default_factory=dict)   # "名前:,値" の行をそのまま

    @property
    def pause_count(self) -> int:
        return int(float(self.info.get("Pause Count", 0) or 0))


def _parse_name(path: Path) -> tuple[str, datetime]:
    stem = path.name.removesuffix(" Stats.csv")
    scenario, _, stamp = stem.rpartition(" - ")
    scenario = scenario.removesuffix(" - Challenge")
    return scenario, datetime.strptime(stamp, "%Y.%m.%d-%H.%M.%S")


def _time_of_day(end: datetime, hms: str) -> datetime:
    """日付のない時刻を、終わった日時より前で最も近い日時にする（夜 0 時をまたいでもよいように）。"""
    t = datetime.strptime(hms, "%H:%M:%S.%f").time()
    d = datetime.combine(end.date(), t)
    if d > end + timedelta(seconds=1):
        d -= timedelta(days=1)
    return d


def parse_stats(path: Path) -> Run:
    path = Path(path)
    scenario, end = _parse_name(path)
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    kills, shots = [], []
    i = 1
    while i < len(rows) and rows[i] and rows[i][0].isdigit():
        kills.append(_time_of_day(end, rows[i][1]).timestamp())
        shots.append(int(rows[i][5]))
        i += 1
    info, total = {}, 0
    in_weapons = False
    for r in rows[i:]:
        if not r or not r[0]:
            in_weapons = False
            continue
        if r[0] == "Weapon":
            in_weapons = True
            continue
        if in_weapons and len(r) > 1 and r[1].isdigit():
            total += int(r[1])
        elif r[0].endswith(":") and len(r) > 1:
            info[r[0][:-1]] = r[1]
    start = _time_of_day(end, info["Challenge Start"]).timestamp() if "Challenge Start" in info else float("nan")
    return Run(path, scenario, end.timestamp(), start, np.array(kills), np.array(shots, dtype=int), total, info)


def runs_during(stats_dir: Path, t_from: float, t_to: float) -> list[Run]:
    """t_from〜t_to の間に始まったシナリオ（開始の 2 秒前まで許す）。古い順。"""
    out = []
    for p in stats_dir.glob("* Stats.csv"):
        try:
            _, end = _parse_name(p)
        except ValueError:
            continue
        if end.timestamp() < t_from:
            continue
        r = parse_stats(p)
        if t_from - 2.0 <= r.start <= t_to:
            out.append(r)
    return sorted(out, key=lambda r: r.start)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def import_runs(events_csv: Path, stats_dir: Path) -> tuple[list[Path], list[str]]:
    """マウスの記録の間に始まったシナリオの CSV を、同じフォルダの kovaaks/ にコピーする。

    戻り値は（コピー先のパス、警告）。すでにコピー済みなら、それを返す（上書きしない）。
    """
    events_csv = Path(events_csv)
    meta = json.loads(events_csv.with_suffix(".json").read_text(encoding="utf-8"))
    t0 = meta["t0_unix"]
    t1 = t0 + float(meta.get("duration_s", 0))
    runs = runs_during(stats_dir, t0, t1)
    warnings = []
    if not runs:
        warnings.append("記録の間に始まった KovaaK's の結果が見つかりません（シナリオを最後まで終えたか確かめてください）")
    dest_dir = events_csv.parent / "kovaaks"
    copied, entries = [], []
    for r in runs:
        dest = dest_dir / r.path.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_hash = _sha256(r.path)
        if dest.exists():
            if _sha256(dest) != src_hash:
                warnings.append(f"コピー先に同じ名前の別の中身があります。上書きしません: {dest.name}")
        else:
            shutil.copy2(r.path, dest)
        copied.append(dest)
        entries.append({"file": dest.name, "source": str(r.path), "sha256": src_hash,
                        "scenario": r.scenario, "challenge_start_s": round(r.start - t0, 3),
                        "pause_count": r.pause_count})
        if r.pause_count:
            warnings.append(f"{r.path.name}: 一時停止が {r.pause_count} 回あります（その間は時刻が飛びます）")
        if r.end > t1:
            warnings.append(f"{r.path.name}: シナリオがマウスの記録より後に終わっています（最後のほうはマウスの記録がありません）")
    if len(runs) > 1:
        warnings.append(f"記録の間に {len(runs)} 回ぶんのシナリオがあります")
    manifest = dest_dir / f"{events_csv.stem}_import.json"
    if copied and not manifest.exists():  # 最初に取り込んだときの記録を残す
        manifest.write_text(json.dumps({"events": events_csv.name, "imported_at": datetime.now().isoformat(timespec="seconds"),
                                        "stats_dir": str(stats_dir), "runs": entries},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
    return copied, warnings


def align(click_times: np.ndarray, run: Run) -> dict:
    """マウスの左クリック（UNIX 時刻）と、KovaaK's の倒した時刻・撃った数を比べる。"""
    if run.kills.size == 0:
        return {"n_kills": 0, "shots_csv": run.total_shots, "clicks_in_run": 0}
    click_times = np.sort(click_times)
    # 最初の的を倒すまでに撃った数（外しを含む）だけ、最初の的のクリックからさかのぼる。
    # シナリオを始めるためのクリックを数えないため、Challenge Start ではなくここを始まりにする
    k = int(run.shots_per_kill[0])
    i_first = np.searchsorted(click_times, run.kills[0] + 0.05, side="right")
    i_last = np.searchsorted(click_times, run.kills[-1] + 0.05, side="right")
    in_run = click_times[max(i_first - k, 0):i_last]
    # 倒した時刻の直前（50 ms 先まで許す）の左クリックとの差
    j = np.searchsorted(click_times, run.kills + 0.05, side="right") - 1
    gaps = (run.kills[j >= 0] - click_times[j[j >= 0]]) * 1000
    return {"n_kills": int(run.kills.size), "shots_csv": int(run.shots_per_kill.sum()),
            "clicks_in_run": int(in_run.size),
            "kill_minus_click_ms": {"median": float(np.median(gaps)), "min": float(gaps.min()),
                                    "max": float(gaps.max())} if gaps.size else None}


def print_alignment(run: Run, t0: float, a: dict) -> None:
    print(f"  {run.scenario}  スコア {float(run.info.get('Score', 'nan')):.1f}  "
          f"開始は記録開始の {run.start - t0:+.2f} s 後  一時停止 {run.pause_count} 回")
    ok = "一致" if a["clicks_in_run"] == a["shots_csv"] else "ずれあり"
    print(f"    撃った数    CSV {a['shots_csv']} 発 / マウスの左クリック {a['clicks_in_run']} 回（{ok}）")
    g = a.get("kill_minus_click_ms")
    if g:
        print(f"    倒した時刻 − 直前の左クリック  中央値 {g['median']:.1f} ms（{g['min']:.1f}〜{g['max']:.1f}）")
    s = run.info
    print(f"    設定        DPI {s.get('DPI', '?')}、感度 {s.get('Horiz Sens', '?')}（{s.get('Sens Scale', '?')}）、"
          f"FOV {s.get('FOV', '?')}")
