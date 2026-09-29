"""記録ファイルの表示。生データなら生波形と包絡線、正規化済みなら %MVC を描く。"""

from __future__ import annotations

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
