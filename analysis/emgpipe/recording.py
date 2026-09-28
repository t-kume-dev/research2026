"""記録とファイル入出力。

1回の記録は1つの .npz に入れる。チャネルごとにサンプリング周波数が違ってもよいよう、
各チャネルを別の配列として持ち、チャネル情報は meta（JSON 文字列）に入れる。
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np

from .sources import ChannelInfo, Source


@dataclass
class Recording:
    channels: list[ChannelInfo]
    data: dict[str, np.ndarray]
    task: str = ""
    meta: dict = field(default_factory=dict)

    def fs(self, name: str) -> float:
        return next(c.fs for c in self.channels if c.name == name)

    @property
    def emg_names(self) -> list[str]:
        return [c.name for c in self.channels if c.type == "EMG"]

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = {**self.meta, "task": self.task, "channels": [asdict(c) for c in self.channels]}
        np.savez_compressed(path, meta=json.dumps(meta, ensure_ascii=False), **self.data)
        return path

    @classmethod
    def load(cls, path: Path) -> "Recording":
        with np.load(path) as f:
            meta = json.loads(str(f["meta"]))
            chans = [ChannelInfo(**c) for c in meta.pop("channels")]
            data = {c.name: f[c.name] for c in chans}
        return cls(chans, data, meta.pop("task", ""), meta)


def record(source: Source, duration: float, task: str = "", progress: bool = True) -> Recording:
    """duration 秒ぶん記録する。

    終了判定は壁時計ではなくサンプル数で行う（全 EMG チャネルが fs*duration に達するまで）。
    """
    names = [c.name for c in source.channels]
    buf: dict[str, list[np.ndarray]] = {n: [] for n in names}
    got = dict.fromkeys(names, 0)
    target = {c.name: int(round(c.fs * duration)) for c in source.channels}
    watch = [c.name for c in source.emg_channels] or names

    started = datetime.now().isoformat(timespec="seconds")
    source.start(task)
    t0 = time.perf_counter()
    last_print = -1
    try:
        while any(got[n] < target[n] for n in watch):
            for name, x in source.read().items():
                if name in buf and x.size:
                    buf[name].append(x)
                    got[name] += x.size
            if progress:
                sec = int(time.perf_counter() - t0)
                if sec != last_print:
                    last_print = sec
                    print(f"\r  記録中 {sec:>3d} / {duration:.0f} s", end="", flush=True)
            if time.perf_counter() - t0 > duration + 10:
                raise TimeoutError("データが届きません。センサの電源と接続を確認してください。")
    finally:
        source.stop()
        if progress:
            print()

    data = {n: (np.concatenate(buf[n]) if buf[n] else np.zeros(0))[:target[n]] for n in names}
    return Recording(list(source.channels), data, task,
                     {"started": started, "duration_s": duration, "source": type(source).__name__})
