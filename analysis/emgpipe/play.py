"""筋電とマウスを同時に記録する（M2-2「筋電とマウスを同時に記録」）。

マウス（events.record_events）を別スレッドで動かし、そのあいだに筋電（recording.record）を取る。
どちらも time.perf_counter() で開始時刻を残すので、マウスの時刻を筋電の時刻（筋電の開始 = 0 秒）に直せる。
保存は同じ名前で 2 つ：<name>.npz（筋電）と <name>.csv（マウス）。KovaaK's の結果はそのあと取り込む。
obs を渡すと、録画 → マウス → 筋電の順に始め、逆の順に止める。録画は <name>.mp4（OBS の形式の拡張子）になる。
"""

from __future__ import annotations

import threading
from pathlib import Path

import numpy as np

from .events import Events, record_events
from .recording import Recording, record
from .sources import Source


def record_play(source: Source, duration: float, task: str = "play", obs=None,
                video_dest: Path | None = None) -> tuple[Recording, Events]:
    """duration 秒ぶん、筋電とマウスを同時に取る。マウスは筋電より少し前に始め、少しあとに止める。

    obs（obs.ObsRecorder）を渡すと画面録画も一緒に取り、video_dest（拡張子なし）に動かす。
    """
    video_t0 = obs.start() if obs is not None else None
    try:
        rec, ev = _record_emg_mouse(source, duration, task)
    finally:
        video = obs.stop(video_dest) if obs is not None else None
    if obs is not None:
        rec.meta["video"] = video.name if video else None
        rec.meta["video_t0_perf_counter"] = video_t0
        # 録画の時刻 + この値 = 筋電の時刻
        rec.meta["video_offset_s"] = float(video_t0 - rec.meta["t0_perf_counter"])
    return rec, ev


def _record_emg_mouse(source: Source, duration: float, task: str) -> tuple[Recording, Events]:
    stop, ready = threading.Event(), threading.Event()
    box: dict = {}

    def run():
        try:
            box["ev"] = record_events(duration + 60, progress=False, stop=stop, ready=ready)
        except BaseException as e:  # noqa: BLE001  メインに伝える
            box["err"] = e
            ready.set()

    th = threading.Thread(target=run, name="emgpipe-mouse", daemon=True)
    th.start()
    ready.wait(5)
    if "err" in box:
        raise box["err"]
    try:
        rec = record(source, duration, task)
    finally:
        stop.set()
        th.join(5)
    if "err" in box:
        raise box["err"]
    ev = box["ev"]
    rec.meta["mouse_offset_s"] = mouse_offset(rec, ev)
    ev.meta["emg_t0_perf_counter"] = rec.meta["t0_perf_counter"]
    return rec, ev


def mouse_offset(rec: Recording, ev: Events) -> float:
    """マウスの時刻 + この値 = 筋電の時刻（筋電の開始が 0 秒）。"""
    return float(ev.meta["t0_perf_counter"] - rec.meta["t0_perf_counter"])


def save_play(rec: Recording, ev: Events, out_dir: Path, name: str) -> tuple[Path, Path]:
    return rec.save(Path(out_dir) / f"{name}.npz"), ev.save(Path(out_dir) / f"{name}.csv")


def plot_play(rec: Recording, ev: Events, out: Path | None = None) -> None:
    """筋電の包絡線（チャネルごと）とマウスの速さ・左クリックを、筋電の時刻で縦に並べる。"""
    import matplotlib.pyplot as plt
    from . import processing as proc
    plt.rcParams["font.family"] = ["Meiryo", "sans-serif"]

    off = mouse_offset(rec, ev)
    names = rec.emg_names
    fig, axes = plt.subplots(len(names) + 1, 1, figsize=(12, 1.6 * (len(names) + 1) + 0.6), sharex=True)
    axes = np.atleast_1d(axes)
    clicks = ev.clicks + off
    for ax, n in zip(axes, names):
        x, fs = rec.data[n], rec.fs(n)
        t = np.arange(x.size) / fs
        ax.plot(t, proc.envelope(x, fs), color="#1A1A1A", lw=0.8)
        ax.set_ylabel(n, fontsize=8, rotation=0, ha="right", va="center")
        for c in clicks:
            ax.axvline(c, color="#C8C8C8", lw=0.5, zorder=0)
    ax = axes[-1]
    # 10 ms ごとの移動量の合計 → 速さ [counts/s]
    if ev.t.size:
        bins = np.arange(0, rec.meta["duration_s"] + 0.01, 0.01)
        mv = np.hypot(ev.dx, ev.dy)
        speed, _ = np.histogram(ev.t + off, bins=bins, weights=mv)
        ax.plot(bins[:-1], speed / 0.01, color="#6B6B6B", lw=0.8)
    for c in clicks:
        ax.axvline(c, color="#E07B00", lw=0.6)
    ax.set_ylabel("マウスの速さ\n[counts/s]", fontsize=8, rotation=0, ha="right", va="center")
    ax.set_xlabel("筋電の開始からの時間 [s]（縦線 = 左クリック）")
    fig.tight_layout()
    if out:
        fig.savefig(out, dpi=150)
        plt.close(fig)
    else:
        plt.show()
