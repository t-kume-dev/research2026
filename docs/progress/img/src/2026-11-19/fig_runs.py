"""図 7：同じシナリオ 5 回のスコアと、その内訳（倒した数・精度）。時刻のそろい方も 5 回ぶんで確かめる。"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\akash\Documents\lab\research2026\analysis")
from emgpipe.events import Events  # noqa: E402
from emgpipe.kovaaks import align, parse_stats  # noqa: E402

OUT = Path(__file__).resolve().parents[2]  # docs/progress/img
INK, GRAY, LIGHT, ACCENT = "#1A1A1A", "#6B6B6B", "#C8C8C8", "#D9822B"
plt.rcParams.update({"font.family": ["Meiryo", "sans-serif"], "font.size": 13, "text.color": INK,
                     "axes.edgecolor": GRAY, "axes.labelcolor": GRAY, "xtick.color": GRAY, "ytick.color": GRAY,
                     "axes.spines.top": False, "axes.spines.right": False})

raw = Path(r"C:\Users\akash\Documents\lab\research2026\data\raw\2026-11-17")
runs = [parse_stats(p) for p in sorted((raw / "kovaaks").glob("*Stats.csv"))]
names = ["kovaaks_test", "kovaaks_2", "kovaaks_3", "kovaaks_4", "kovaaks_5"]
rows, gaps = [], []
for name in names:
    ev = Events.load(raw / f"{name}.csv")
    t0 = ev.meta["t0_unix"]
    run = next(r for r in runs if t0 - 2 <= r.start <= t0 + float(ev.t[-1]) + 5)
    clicks = np.sort(t0 + ev.clicks)
    a = align(clicks, run)
    j = np.searchsorted(clicks, run.kills + 0.05, side="right") - 1
    g = (run.kills - clicks[j]) * 1000
    gaps.append(g)
    kills, shots = run.kills.size, run.total_shots
    rows.append(dict(name=name, end=run.path.name.split(" - ")[-1][11:16].replace(".", ":"),
                     score=float(run.info["Score"]), kills=kills, shots=shots, clicks=a["clicks_in_run"],
                     acc=kills / shots, gmin=g.min(), gmax=g.max(), gmed=np.median(g)))
for r in rows:
    print(f"{r['name']:13s} 終了 {r['end']}  スコア {r['score']:6.1f}  倒した {r['kills']}  撃った {r['shots']}"
          f"（クリック {r['clicks']}）  精度 {r['acc']:.3f}  ずれ {r['gmin']:.1f}〜{r['gmax']:.1f} ms（中央値 {r['gmed']:.1f}）")
allg = np.concatenate(gaps)
print(f"全部 {allg.size} 体：{allg.min():.1f}〜{allg.max():.1f} ms、中央値 {np.median(allg):.1f} ms")

x = np.arange(1, 6)
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
panels = [("score", "スコア", "{:.0f}", (500, 820)), ("kills", "倒した数（60 秒）", "{:d}", (60, 86)),
          ("acc", "精度（倒した数 ÷ 撃った数）", "{:.0%}", (0.82, 0.96))]
for ax, (key, title, fmt, ylim) in zip(axes, panels):
    v = [r[key] for r in rows]
    ax.plot(x[1:], v[1:], color=INK, lw=2, zorder=2)
    ax.scatter(x, v, s=70, color=[GRAY] + [INK] * 4, zorder=3, edgecolor="white", linewidth=2)
    for i, (xi, vi) in enumerate(zip(x, v)):
        below = i == 2  # 3 回目は線と重なるので下に置く
        ax.text(xi + (0.12 if below else 0), vi + (ylim[1] - ylim[0]) * (-0.08 if below else 0.04), fmt.format(vi),
                ha="left" if below else "center", color=INK, fontsize=11)
    ax.set_title(title, loc="left", color=INK, fontsize=14)
    ax.set_xticks(x, [f"{i}\n{r['end']}" for i, r in zip(x, rows)])
    ax.set_ylim(*ylim)
    ax.set_xlim(0.5, 5.5)
    ax.grid(axis="y", color=LIGHT, lw=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    if key == "acc":
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
axes[0].annotate("3 回目：倒した数は増えたが\n精度が落ちてスコアが下がった", xy=(3, rows[2]["score"]), xytext=(3.25, 545),
                 fontsize=10.5, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1, shrinkB=6))
axes[2].scatter([3], [rows[2]["acc"]], s=70, color=ACCENT, zorder=4, edgecolor="white", linewidth=2)
axes[0].scatter([3], [rows[2]["score"]], s=70, color=ACCENT, zorder=4, edgecolor="white", linewidth=2)
fig.supxlabel("回（下は終わった時刻。1 回目だけ 4 時間前に単独で、2〜5 回目は続けて遊んだ）", color=GRAY, fontsize=12)
fig.tight_layout()
fig.savefig(OUT / "2026-11-19_7_runs.png", dpi=150, bbox_inches="tight")
