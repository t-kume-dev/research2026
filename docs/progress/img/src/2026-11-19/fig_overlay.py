"""撃った 76 発すべてについて、撃つ直前の照準の動きを、撃った場所を原点にそろえて重ねる。"""
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
plt.rcParams.update({"font.family": ["Meiryo", "sans-serif"], "font.size": 13, "text.color": INK,
                     "axes.edgecolor": GRAY, "axes.labelcolor": GRAY, "xtick.color": GRAY, "ytick.color": GRAY,
                     "axes.spines.top": False, "axes.spines.right": False})

raw = Path(r"C:\Users\akash\Documents\lab\research2026\data\raw\2026-11-17")
ev = Events.load(raw / "kovaaks_test.csv")
t0 = ev.meta["t0_unix"]
run = parse_stats(next((raw / "kovaaks").glob("*Stats.csv")))
DEG = 0.07 * float(run.info["Horiz Sens"])
x = np.cumsum(ev.dx) * DEG
y = -np.cumsum(ev.dy) * DEG
clicks = ev.clicks
kills = run.kills - t0
j = np.searchsorted(clicks, kills + 0.05, side="right") - 1
hit = np.zeros(len(clicks), bool)
hit[j] = True
i0 = j[0] - (int(run.shots_per_kill[0]) - 1)
shots = np.where((np.arange(len(clicks)) >= i0) & (clicks <= kills[-1] + 0.05))[0]

PRE = 0.4  # 撃つ前に見る長さ [s]
grid = np.arange(-PRE, 0.0001, 0.008)  # 8 ms ごと（届く間隔に合わせる）


def pos_at(t):
    i = np.clip(np.searchsorted(ev.t, t, side="right") - 1, 0, len(ev.t) - 1)
    return x[i], y[i]


fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
dist = {True: [], False: []}
for order, want in ((0, True), (1, False)):  # 外れを上に重ねる
    for k in shots[hit[shots] == want]:
        tc = clicks[k]
        px, py = pos_at(tc + grid)
        cx, cy = pos_at(tc)
        px, py = px - cx, py - cy
        a1.plot(px, py, color=ACCENT if want else INK, lw=0.8 if want else 1.4, alpha=0.5 if want else 0.9,
                zorder=2 + order)
        dist[want].append(np.hypot(px, py))
a1.scatter([0], [0], marker="+", s=200, color=INK, zorder=5)
a1.set_aspect("equal")
a1.set_xlim(-10, 10)
a1.set_ylim(-10, 10)
a1.set_xlabel("撃った場所からの横のずれ [度]")
a1.set_ylabel("撃った場所からの縦のずれ [度]")
a1.set_title(f"撃つ前 {PRE} 秒の照準の動き（{len(shots)} 発すべて）", loc="left", fontsize=13)
a1.plot([], [], color=ACCENT, label=f"当たり {int(hit[shots].sum())} 発")
a1.plot([], [], color=INK, lw=1.4, label=f"外れ {int((~hit[shots]).sum())} 発")
a1.legend(frameon=False, loc="upper left", fontsize=11)

for want in (True, False):
    d = np.array(dist[want])
    for row in d:
        a2.plot(grid * 1000, row, color=ACCENT if want else INK, lw=0.6, alpha=0.25 if want else 0.5)
    a2.plot(grid * 1000, np.median(d, axis=0), color=ACCENT if want else INK, lw=3,
            label=("当たり" if want else "外れ") + "の中央値")
a2.set_xlabel("撃つまでの時間 [ms]")
a2.set_ylabel("撃った場所までの距離 [度]")
a2.set_title("撃った場所に近づいていく様子", loc="left", fontsize=13)
a2.set_xlim(-PRE * 1000, 0)
a2.set_ylim(0, None)
a2.legend(frameon=False, loc="upper right", fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "2026-11-19_6_overlay.png", dpi=150)

for want in (True, False):
    d = np.array(dist[want])
    i100 = np.argmin(np.abs(grid + 0.1))
    print(("当たり" if want else "外れ"), f"撃つ 100 ms 前の距離 中央値 {np.median(d[:, i100]):.2f} 度")
