"""横・縦それぞれの、向き付きの速さ（右・上が +）。上に 1 回ぶん全体、下に 20〜30 秒の拡大。"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\akash\Documents\lab\research2026\analysis")
from emgpipe.events import Events  # noqa: E402
from emgpipe.kovaaks import parse_stats  # noqa: E402

OUT = Path(__file__).resolve().parents[2]  # docs/progress/img
INK, GRAY, LIGHT, ACCENT = "#1A1A1A", "#6B6B6B", "#C8C8C8", "#D9822B"
plt.rcParams.update({"font.family": ["Meiryo", "sans-serif"], "font.size": 12, "text.color": INK,
                     "axes.edgecolor": GRAY, "axes.labelcolor": GRAY, "xtick.color": GRAY, "ytick.color": GRAY,
                     "axes.spines.top": False, "axes.spines.right": False})

raw = Path(r"C:\Users\akash\Documents\lab\research2026\data\raw\2026-11-17")
ev = Events.load(raw / "kovaaks_test.csv")
t0 = ev.meta["t0_unix"]
run = parse_stats(next((raw / "kovaaks").glob("*Stats.csv")))
DEG = 0.07 * float(run.info["Horiz Sens"])
clicks = ev.clicks
kills = run.kills - t0
j = np.searchsorted(clicks, kills + 0.05, side="right") - 1
hit = np.zeros(len(clicks), bool)
hit[j] = True
i0 = j[0] - (int(run.shots_per_kill[0]) - 1)
in_run = (np.arange(len(clicks)) >= i0) & (clicks <= kills[-1] + 0.05)

edges = np.arange(0, ev.t[-1], 0.01)
tc = edges[:-1] + 0.005
vel = {}
for name, d in (("横", ev.dx * DEG), ("縦", -ev.dy * DEG)):
    s, _ = np.histogram(ev.t, bins=edges, weights=d)
    vel[name] = np.convolve(s, np.ones(5) / 0.05, mode="same")  # 50 ms の窓で 度/秒

z0, z1 = 20, 30
fig, axes = plt.subplots(4, 1, figsize=(13, 9.5), gridspec_kw={"height_ratios": [1, 1, 1.3, 1.3], "hspace": 0.75})
for row, (ax, name, (w0, w1)) in enumerate(zip(axes, ["横", "縦", "横", "縦"],
                                                [(0, ev.t[-1])] * 2 + [(z0, z1)] * 2)):
    m = (tc >= w0) & (tc <= w1)
    v = vel[name]
    ax.axhline(0, color=LIGHT, lw=1)
    ax.plot(tc[m], v[m], color=INK, lw=0.7 if row < 2 else 1.2)
    sel = in_run & (clicks >= w0) & (clicks <= w1)
    vc = np.interp(clicks, tc, v)
    sz = 10 if row < 2 else 40
    ax.scatter(clicks[sel & hit], vc[sel & hit], s=sz, color=ACCENT, zorder=3, label="当たったクリック")
    ax.scatter(clicks[sel & ~hit], vc[sel & ~hit], s=sz, facecolor="white", edgecolor=INK, lw=1.1, zorder=3,
               label="外したクリック")
    ax.set_xlim(w0, w1)
    ax.set_ylim(-150, 150)
    ax.set_ylabel(f"{name}の速さ [度/秒]\n" + ("（右が +）" if name == "横" else "（上が +）"), fontsize=10)
    if row < 2:
        ax.axvspan(z0, z1, color=LIGHT, alpha=0.5, lw=0)
axes[0].set_title("1 回ぶん全体（灰色の帯を下で拡大）", loc="left", fontsize=13)
axes[0].legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=10)
axes[2].set_title("拡大：的ごとに、横と縦それぞれ向きと大きさの違う動きを組み合わせている", loc="left", fontsize=13)
axes[1].set_xlabel("記録開始からの時刻 [s]")
axes[3].set_xlabel("記録開始からの時刻 [s]")
fig.savefig(OUT / "2026-11-19_4_xy_speed.png", dpi=150, bbox_inches="tight")
print("ok")
