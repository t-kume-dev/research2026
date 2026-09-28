"""セッション冒頭のキャリブレーション（安静参照 + MVC）と、それを使った正規化。

手順（毎セッション同じ）:
  1. 安静参照: マウスに手を置いたまま 10 秒静止
  2. MVC: 課題ごとに 5 秒の最大努力 × 3 試行。試行間は休憩（既定 60 秒）

各チャネルの MVC 値は、全課題・全試行を通した「包絡線の 0.5 秒移動平均の最大値」とする。
センサが大きく筋を分離できないため、どの課題で最大になったかはチャネルに任せ、記録だけ残す。

正規化は2通り出す:
  pct_mvc      = env / MVC × 100
  pct_mvc_rest = (env − rest) / (MVC − rest) × 100   … 姿勢による保持活動の床を差し引いた値
静止区間の残余活動を指標にする場合、rest を引くと見たいものまで消えうるため、両方残しておく。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path

import numpy as np

from . import processing as proc
from .recording import Recording, record
from .sources import ChannelInfo, Source

MVC_TASKS = {
    "wrist_extension": "手首の伸展（手の甲を上に反らす）。手の甲を押さえてもらい、全力で押し返す",
    "wrist_flexion": "手首の屈曲（手のひら側に曲げる）。手のひらを押さえてもらい、全力で押し返す",
    "grip": "グリップ。握力計かタオルを全力で握る",
}
DEFAULT_TASKS = ("wrist_extension", "wrist_flexion")


@dataclass
class ProtocolConfig:
    rest_s: float = 10.0
    tasks: tuple[str, ...] = DEFAULT_TASKS
    trials: int = 3
    contraction_s: float = 5.0
    rest_between_s: float = 60.0
    countdown_s: int = 3


@dataclass
class Calibration:
    rest: dict[str, float]
    mvc: dict[str, float]
    mvc_source: dict[str, str]
    created: str = ""
    params: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def save(self, path: Path) -> Path:
        Path(path).write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return Path(path)

    @classmethod
    def load(cls, path: Path) -> "Calibration":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# 値の算出（記録済みファイルから。機材がなくても再計算できる）
# ---------------------------------------------------------------------------

def rest_level(rec: Recording, name: str, trim_s: float = 1.0) -> float:
    fs = rec.fs(name)
    env = proc.envelope(rec.data[name], fs)
    k = int(trim_s * fs)
    core = env[k:-k] if env.size > 4 * k else env
    return float(np.median(core))


def mvc_level(rec: Recording, name: str) -> float:
    fs = rec.fs(name)
    env = proc.envelope(rec.data[name], fs)
    return float(proc.moving_mean(env, fs, proc.MVC_WINDOW_S).max())


def compute_calibration(rest_rec: Recording, mvc_recs: dict[str, Recording]) -> Calibration:
    """mvc_recs は {試行ラベル（例 "wrist_extension_1"）: 記録}。"""
    rest, mvc, src, warns = {}, {}, {}, []
    for name in rest_rec.emg_names:
        rest[name] = rest_level(rest_rec, name)
        best_label, best = "", -np.inf
        for label, rec in mvc_recs.items():
            v = mvc_level(rec, name)
            if v > best:
                best_label, best = label, v
        mvc[name], src[name] = best, best_label
        ratio = best / rest[name] if rest[name] > 0 else np.inf
        if ratio < 5:
            warns.append(f"{name}: MVC が安静の {ratio:.1f} 倍しかない。電極の接触か、収縮が不十分な可能性")
    return Calibration(
        rest, mvc, src, datetime.now().isoformat(timespec="seconds"),
        {"bandpass_hz": proc.BANDPASS_HZ, "envelope_lp_hz": proc.ENVELOPE_LP_HZ,
         "mvc_window_s": proc.MVC_WINDOW_S},
        warns)


def calibration_from_dir(session_dir: Path) -> Calibration:
    session_dir = Path(session_dir)
    rest_rec = Recording.load(session_dir / "rest.npz")
    mvc_recs = {p.stem.removeprefix("mvc_"): Recording.load(p)
                for p in sorted(session_dir.glob("mvc_*.npz"))}
    if not mvc_recs:
        raise FileNotFoundError(f"{session_dir} に mvc_*.npz がありません")
    return compute_calibration(rest_rec, mvc_recs)


# ---------------------------------------------------------------------------
# 手順の実行（対話式）
# ---------------------------------------------------------------------------

def _countdown(n: int) -> None:
    for i in range(n, 0, -1):
        print(f"  {i}...", flush=True)
        time.sleep(1)
    print("  始め！", flush=True)


def _wait(sec: float, msg: str) -> None:
    end = time.perf_counter() + sec
    while (left := end - time.perf_counter()) > 0:
        print(f"\r  {msg} 残り {left:4.0f} s", end="", flush=True)
        time.sleep(min(1.0, left))
    print()


def run_protocol(source: Source, session_dir: Path, cfg: ProtocolConfig = ProtocolConfig(),
                 interactive: bool = True) -> Calibration:
    session_dir = Path(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    ask = input if interactive else (lambda _msg: "")

    print(f"\n[1] 安静参照 {cfg.rest_s:.0f} 秒。マウスに手を置いたまま、力を抜いて静止してください")
    ask("  準備ができたら Enter > ")
    _countdown(cfg.countdown_s if interactive else 0)
    rest_rec = record(source, cfg.rest_s, "rest")
    rest_rec.save(session_dir / "rest.npz")

    mvc_recs = {}
    for ti, task in enumerate(cfg.tasks):
        print(f"\n[{ti + 2}] MVC: {task}: {MVC_TASKS.get(task, '')}")
        for k in range(1, cfg.trials + 1):
            ask(f"  試行 {k}/{cfg.trials}（{cfg.contraction_s:.0f} 秒間、全力で）。準備ができたら Enter > ")
            _countdown(cfg.countdown_s if interactive else 0)
            rec = record(source, cfg.contraction_s, task)
            label = f"{task}_{k}"
            rec.save(session_dir / f"mvc_{label}.npz")
            mvc_recs[label] = rec
            peaks = ", ".join(f"{n}={mvc_level(rec, n):.3g}" for n in rec.emg_names)
            print(f"  ピーク: {peaks}")
            last = ti == len(cfg.tasks) - 1 and k == cfg.trials
            if not last and cfg.rest_between_s > 0:
                _wait(cfg.rest_between_s, "休憩")

    calib = compute_calibration(rest_rec, mvc_recs)
    calib.save(session_dir / "calibration.json")
    print_calibration(calib)
    return calib


def print_calibration(calib: Calibration) -> None:
    print("\nキャリブレーション結果")
    for name in calib.mvc:
        r, m = calib.rest[name], calib.mvc[name]
        print(f"  {name}: rest={r:.4g}  MVC={m:.4g}  (MVC/rest = {m / r:.1f}, 最大は {calib.mvc_source[name]})")
    for w in calib.warnings:
        print(f"  警告: {w}")


# ---------------------------------------------------------------------------
# 正規化
# ---------------------------------------------------------------------------

def normalize(rec: Recording, calib: Calibration) -> Recording:
    """EMG チャネルごとに包絡線・%MVC・安静補正済み %MVC を持つ Recording を返す。"""
    chans, data = [], {}
    for name in rec.emg_names:
        if name not in calib.mvc:
            print(f"  警告: {name} はキャリブレーションに含まれていないので飛ばす")
            continue
        fs = rec.fs(name)
        env = proc.envelope(rec.data[name], fs)
        r, m = calib.rest[name], calib.mvc[name]
        outs = {
            "env": ("ENV", env),
            "pct_mvc": ("PCT_MVC", env / m * 100.0),
            "pct_mvc_rest": ("PCT_MVC_REST", (env - r) / (m - r) * 100.0),
        }
        for suffix, (ctype, x) in outs.items():
            key = f"{name}.{suffix}"
            chans.append(ChannelInfo(key, ctype, fs, name))
            data[key] = x
    meta = {**rec.meta, "normalized_with": {"created": calib.created, "rest": calib.rest, "mvc": calib.mvc}}
    return Recording(chans, data, rec.task, meta)
