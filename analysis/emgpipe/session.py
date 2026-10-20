"""研究室での 1 回の記録を、決めた順番で通しで流す（M1：6 か所の MVC と数分の記録を 1 回で取りきる）。

  1. 接続とセンサの本数の確認
  2. 信号の確認（脱力 → 反らす → 脱力）。浮いたセンサ（50 Hz の雑音ばかり）がないか見る
  3. 安静 10 秒
  4. 確認動作（手首を上に反らしきる・手のひら上で上に曲げきる、1 回ずつ）。疲れる前に取る
  5. MVC：課題を 1 周ずつ回す（既定 2 周）。同じ筋が続かないので、休憩は短くてよい（既定 10 秒）
  6. 長い記録（既定 180 秒）。マウスを自由に動かす
  7. MVC の比べ（mvc_compare.csv）と calibration.json を出す

記録中の窓をクリックするかキーを押すと次へ進む。ターミナルに戻らなくてよい。
ファイル名の rest / check_ / mvc_ は calibration.py が見分けに使う。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from .calibration import (MVC_TASKS, TASK_TITLES, calibration_from_dir, compare_tasks, mvc_level,
                          print_calibration, print_comparison, save_comparison)
from .plot import LiveView, parse_cues
from .recording import Recording, record
from .sources import Source

# 手首はどちらも「上に全力で曲げ、人に押さえてもらう」が本番。一人で試すときは天板の裏（10-20 に決めた）
WRIST_TASKS = ("ext_fist_pron", "flex_fist_sup")
WRIST_TASKS_SOLO = ("ext_fixed_solo", "flex_fixed_solo")
# 前腕以外。まず一人でできる形で試す（M1-4）
OTHER_TASKS = ("shoulder_abduction_solo", "elbow_flexion_solo", "elbow_extension_solo", "shoulder_shrug_solo")


@dataclass
class Step:
    name: str          # 保存するファイル名（拡張子なし）
    task: str          # 記録のラベル。姿勢の図もこれで選ぶ
    duration: float
    cues: str          # 記録中に出す指示 "0:脱力,3:反らす"
    title: str         # 始める前に大きく出す見出し
    desc: str = ""     # その下に出す説明
    rest_after: float = 0.0

def hum_fraction(x: np.ndarray, fs: float, mains: float = 50.0, width: float = 1.0) -> float:
    """信号のうち、電源の雑音（50 Hz とその倍数 ±1 Hz）が占める割合。センサが浮くと 1 に近づく。"""
    x = x - x.mean()
    p = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(x.size, 1 / fs)
    m = np.zeros_like(f, dtype=bool)
    for k in range(1, int(f[-1] // mains) + 1):
        m |= np.abs(f - k * mains) <= width
    return float(p[m].sum() / p.sum()) if p.sum() > 0 else 0.0


def build_steps(tasks: list[str], rounds: int, rest_between: float, long_s: float,
                switch_rest: float = 10.0) -> list[Step]:
    steps = [
        Step("signal_check", "", 10, "0:脱力,4:手首を反らす,7:脱力", "信号の確認（10 秒）",
             "脱力 → 手首を反らす → 脱力。浮いたセンサがないかを見る"),
        Step("rest", "rest", 10, "0:脱力", "安静（10 秒）", "マウスに手を置いたまま、力を抜いて動かない",
             rest_after=5),
        Step("check_free_extension_01", "free_extension", 5, "0:反らしきる", "確認動作：伸展（5 秒）",
             "手のひら下。誰も押さえず、手首を上に全力で反らしきる", rest_after=rest_between),
        Step("check_free_flexion_01", "free_flexion", 5, "0:曲げきる", "確認動作：屈曲（5 秒）",
             "手のひら上。誰も押さえず、手首を上に全力で曲げきる", rest_after=switch_rest),
    ]
    for r in range(1, rounds + 1):
        for task in tasks:
            steps.append(Step(f"mvc_{task}_{r:02d}", task, 5, "0:全力",
                              f"MVC：{TASK_TITLES.get(task, task)}（{r}/{rounds} 周目）",
                              re.sub(r"^【一人用】", "", MVC_TASKS.get(task, "")), rest_after=rest_between))
    steps[-1].rest_after = switch_rest
    steps.append(Step("long_free", "", long_s, "0:マウスを自由に動かす", f"長い記録（{long_s:.0f} 秒）",
                      "マウスを自由に動かす（エイム練習でもよい）"))
    return steps


def load_labels(session_dir: Path) -> dict[str, str]:
    """sensors.json（部位 → 番号）から、窓に出す {チャネル名: "S1 部位"} を作る。なければ空。"""
    path = Path(session_dir) / "sensors.json"
    if not path.exists():
        return {}
    table = json.loads(path.read_text(encoding="utf-8"))
    return {f"S{n}_EMG1": f"S{n} {site}" for site, n in table.items() if n is not None}

def run_lab_session(source: Source, session_dir: Path, steps: list[Step], expect: int = 6,
                    lead: int = 3) -> None:
    session_dir = Path(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    log = open(session_dir / "session_log.txt", "a", encoding="utf-8")
    log.write(f"\n# {datetime.now().isoformat(timespec='seconds')}  channels: "
              f"{', '.join(c.name for c in source.emg_channels)}\n")

    n = len(source.emg_channels)
    print(f"\nEMG チャネル: {n} 本（想定 {expect} 本）")
    if n < expect:
        print(f"  警告: {expect - n} 本足りない。センサが眠っていないか（0 本と出たことがある）、"
              "電源が入っているか確認する。このまま続けてもよい")

    view = LiveView(source.channels, steps[0].duration, pose_panel=True, labels=load_labels(session_dir))
    try:
        for i, st in enumerate(steps, 1):
            view.phase(st.duration, parse_cues(st.cues), pose=st.task, desc=st.desc + "\n\nクリックで開始")
            view.wait_click(f"[{i}/{len(steps)}] {st.title}")
            view.countdown(lead)
            rec = record(source, st.duration, st.task, on_update=view.update)
            path = rec.save(session_dir / f"{st.name}.npz")
            short = _check_samples(rec, st.duration)
            print(f"[{i}/{len(steps)}] {path.name}" + (f"  {short}" if short else ""))
            log.write(f"{st.name}\t{st.task}\t{st.duration:g} s\t{short or 'ok'}\n")
            if st.name == "signal_check":
                _report_signal(rec)
            elif st.name.startswith(("mvc_", "check_")):
                print("  ピーク: " + ", ".join(f"{c}={mvc_level(rec, c) * 1000:.0f} μV" for c in rec.emg_names))
            if st.rest_after > 0 and i < len(steps):
                nxt = steps[i]
                view.phase(0, pose=nxt.task, desc="次：" + nxt.title + "\n" + nxt.desc)
                view.rest(st.rest_after, "休憩")
        view.finish()
    finally:
        log.close()

    rows = compare_tasks(session_dir)
    print_comparison(rows)
    save_comparison(rows, session_dir / "mvc_compare.csv")
    calib = calibration_from_dir(session_dir)
    calib.save(session_dir / "calibration.json")
    print_calibration(calib)
    print(f"\n保存先: {session_dir}")


def _check_samples(rec: Recording, duration: float) -> str:
    bad = [f"{c}={rec.data[c].size}" for c in rec.emg_names if rec.data[c].size < round(rec.fs(c) * duration)]
    return ("サンプル不足: " + ", ".join(bad)) if bad else ""


def _rms_uv(x: np.ndarray) -> float:
    return 1000 * float(np.sqrt(np.mean((x - x.mean()) ** 2)))  # mV → μV


def _report_signal(rec: Recording) -> None:
    """脱力（0〜4 秒）と反らす（4〜7 秒）の RMS と、50 Hz の割合をチャネルごとに出す。"""
    print("  チャネル          脱力 RMS   反らす RMS   50 Hz の割合")
    for c in rec.emg_names:
        x, fs = rec.data[c], rec.fs(c)
        relax = x[int(0.5 * fs):int(3.5 * fs)]
        act = x[int(4.5 * fs):int(6.5 * fs)]
        hum = hum_fraction(relax, fs)
        # 脱力の信号が小さいと 50 Hz の割合は大きく出る（10-20 の S2 は 57% でも反応した）。浮いたときは 97%（10-13）
        flag = "  ← 浮いているかも（貼り直す）" if hum > 0.8 else ""
        print(f"  {c:<16}{_rms_uv(relax):8.1f} μV{_rms_uv(act):10.1f} μV{hum * 100:10.0f} %{flag}")
    print("  前腕の伸筋側は、反らすと脱力の数倍になるはず。ほかの部位は変わらなくてよい")
