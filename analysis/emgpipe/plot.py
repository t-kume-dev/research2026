"""記録ファイルの表示。生データなら生波形と包絡線、正規化済みなら %MVC を描く。"""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from . import processing as proc
from .recording import Recording


# チャネル名（sensors.json の部位名）が日本語でも表示できるよう、あるフォントを前に足す
_JP_FONTS = ["Yu Gothic", "Meiryo", "MS Gothic", "Hiragino Sans", "Noto Sans CJK JP"]
_installed = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = [f for f in _JP_FONTS if f in _installed] + ["DejaVu Sans"]


def plot_file(path: Path, out: Path | None = None) -> None:
    rec = Recording.load(path)
    normalized = any(c.type.startswith("PCT") for c in rec.channels)
    groups = sorted({c.sensor for c in rec.channels}) if normalized else rec.emg_names
    fig, axes = plt.subplots(len(groups), 1, sharex=True, figsize=(10, 2.4 * len(groups)), squeeze=False)

    for ax, g in zip(axes[:, 0], groups):
        if normalized:
            for c in (c for c in rec.channels if c.sensor == g and c.type.startswith("PCT")):
                x = rec.data[c.name]
                ax.plot(np.arange(x.size) / c.fs, x, lw=0.8, label=c.name.split(".")[-1])
            ax.axhline(100, color="0.5", lw=0.8, ls="--")
            ax.set_ylabel(f"{g}\n%MVC")
            ax.legend(loc="upper right", fontsize=8)
        else:
            fs = rec.fs(g)
            x = rec.data[g]
            t = np.arange(x.size) / fs
            ax.plot(t, x, lw=0.4, color="0.6", label="raw")
            ax.plot(t, proc.envelope(x, fs), lw=1.2, label="envelope")
            ax.set_ylabel(g)
            ax.legend(loc="upper right", fontsize=8)
    axes[-1, 0].set_xlabel("time [s]")
    fig.suptitle(f"{path.name}  task={rec.task or '-'}")
    fig.tight_layout()
    if out:
        fig.savefig(out, dpi=120)
        print(f"保存: {out}")
    else:
        plt.show()


def parse_cues(text: str) -> list[tuple[float, str]]:
    """"0:脱力,5:反らす" → [(0.0, "脱力"), (5.0, "反らす")]。記録開始からの秒と指示。"""
    cues = []
    for item in filter(None, (s.strip() for s in text.split(","))):
        sec, _, label = item.partition(":")
        cues.append((float(sec), label.strip()))
    return sorted(cues)


class LiveView:
    """記録中の窓。いまの指示と経過秒を大きく出し、各 EMG チャネルの直近 5 秒の RMS（0.1 秒窓）を描く。"""

    WINDOW_S = 5.0
    RMS_S = 0.1

    def __init__(self, channels, duration: float, cues: list[tuple[float, str]] | None = None):
        self.channels = [c for c in channels if c.type == "EMG"]
        self.duration = duration
        self.cues = cues or []
        plt.ion()
        self.fig, axes = plt.subplots(len(self.channels), 1, sharex=True, squeeze=False,
                                      figsize=(9, 1.6 + 2.2 * len(self.channels)))
        self.axes = axes[:, 0]
        self.lines = []
        for ax, c in zip(self.axes, self.channels):
            (line,) = ax.plot([], [], lw=1.5, color="#1A1A1A")
            ax.set_xlim(-self.WINDOW_S, 0)
            ax.set_ylabel(f"{c.name}\nRMS [μV]")
            self.lines.append(line)
        self.axes[-1].set_xlabel("いまからの時間 [s]")
        self.title = self.fig.suptitle("", fontsize=26, fontweight="bold")
        self.fig.tight_layout(rect=(0, 0, 1, 0.88))
        plt.show(block=False)
        self._bring_to_front()

    def _bring_to_front(self) -> None:
        """ターミナルの裏に隠れないよう、窓を最前面に固定する（Qt のときだけ。ほかは何もしない）。"""
        try:
            from matplotlib.backends.qt_compat import QtCore
            win = self.fig.canvas.manager.window
            win.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
            win.show()
            win.raise_()
            win.activateWindow()
        except Exception:
            pass

    def _cue(self, t: float) -> str:
        label = ""
        for sec, text in self.cues:
            if t >= sec:
                label = text
        return label

    def countdown(self, seconds: int) -> None:
        for k in range(seconds, 0, -1):
            first = self._cue(0.0)
            self.title.set_text(f"あと {k} 秒で開始" + (f"（最初は「{first}」）" if first else ""))
            self._refresh(1.0)

    def phase(self, duration: float, cues: list[tuple[float, str]] | None = None) -> None:
        """同じ窓のまま、次の記録に切り替える（グラフを空にする）。"""
        self.duration = duration
        self.cues = cues or []
        for line in self.lines:
            line.set_data([], [])

    def wait_click(self, text: str) -> None:
        """窓をクリックするかキーを押すまで待つ。ターミナルに戻らなくても進められる。"""
        self.title.set_text(text)
        self._refresh(0.01)
        while self.fig.waitforbuttonpress(timeout=-1) is None:
            pass

    def rest(self, seconds: float, text: str = "休憩") -> None:
        end = time.perf_counter() + seconds
        while (left := end - time.perf_counter()) > 0:
            self.title.set_text(f"{text}　残り {left:3.0f} 秒")
            self._refresh(min(1.0, left))

    def update(self, buf: dict[str, list[np.ndarray]], elapsed: float) -> None:
        for ax, line, c in zip(self.axes, self.lines, self.channels):
            n_win = max(1, int(round(self.RMS_S * c.fs)))
            n_keep = int(self.WINDOW_S * c.fs) // n_win * n_win
            # 長い記録でも重くならないよう、後ろから直近 5 秒ぶんの塊だけつなぐ
            tail, n = [], 0
            for chunk in reversed(buf[c.name]):
                tail.append(chunk)
                n += chunk.size
                if n >= n_keep:
                    break
            x = np.concatenate(tail[::-1]) if tail else np.zeros(0)
            x = x[-n_keep:]
            x = x[: x.size // n_win * n_win]
            if not x.size:
                continue
            rms = 1000 * np.sqrt(((x - x.mean()) ** 2).reshape(-1, n_win).mean(axis=1))  # mV → μV
            t = (np.arange(rms.size) - rms.size + 1) * self.RMS_S
            line.set_data(t, rms)
            ax.set_ylim(0, max(50.0, rms.max() * 1.2))
        cue = self._cue(elapsed)
        self.title.set_text(f"{cue}    {elapsed:4.1f} / {self.duration:.0f} s" if cue
                            else f"{elapsed:4.1f} / {self.duration:.0f} s")
        self._refresh(0.001)

    def finish(self) -> None:
        self.title.set_text("終了")
        self._refresh(1.0)
        plt.close(self.fig)

    def _refresh(self, pause: float) -> None:
        # draw_idle + 短い pause だと、記録中は Qt が描き直さないまま次の更新が来て、表示が止まって見える
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        if pause >= 0.01:
            plt.pause(pause)
