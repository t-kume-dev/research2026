"""マウスの生の移動量（符号付き dx, dy）を足し合わせ、照準の向きの軌道とクリックの場所を描く。"""
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
sens = float(run.info["Horiz Sens"])
DEG = 0.07 * sens  # Valorant 換算の感度: 1 カウントあたり 0.07 × 感度 [度]

# 照準の向き [度]。右が +x、上が +y（マウスの dy は下向きが +）
x = np.cumsum(ev.dx) * DEG
y = -np.cumsum(ev.dy) * DEG
clicks = ev.clicks
kills = run.kills - t0
j = np.searchsorted(clicks, kills + 0.05, side="right") - 1
hit = np.zeros(len(clicks), bool)
hit[j] = True
i0 = j[0] - (int(run.shots_per_kill[0]) - 1)
in_run = (np.arange(len(clicks)) >= i0) & (clicks <= kills[-1] + 0.05)
ci = np.searchsorted(ev.t, clicks, side="right") - 1  # クリックの時点の向き
cx, cy = x[ci], y[ci]

# シナリオ開始（Challenge Start）の瞬間の向きを原点にする
ox, oy = pos0 = (x[np.searchsorted(ev.t, run.start - t0, side="right") - 1],
                 y[np.searchsorted(ev.t, run.start - t0, side="right") - 1])
x, y, cx, cy = x - ox, y - oy, cx - ox, cy - oy

# ---- 図 5: 1 回ぶん全部のクリックの場所
fig, ax = plt.subplots(figsize=(7, 5.2))
mr = (ev.t >= clicks[i0] - 0.5) & (ev.t <= kills[-1])
ax.plot(x[mr], y[mr], color=LIGHT, lw=0.6)
ax.scatter(cx[in_run & hit], cy[in_run & hit], s=35, color=ACCENT, zorder=3, label=f"当たり {int((in_run & hit).sum())}")
ax.scatter(cx[in_run & ~hit], cy[in_run & ~hit], s=45, facecolor="white", edgecolor=INK, lw=1.5, zorder=3,
           label=f"外れ {int((in_run & ~hit).sum())}")
ax.set_aspect("equal")
ax.set_xlabel("横の向き [度]（右が +）")
ax.set_ylabel("縦の向き [度]（上が +）")
ax.set_title("1 回ぶん（約 60 秒）の撃った場所（原点＝シナリオ開始の向き）", loc="left", fontsize=13)
ax.scatter([0], [0], marker="+", s=200, color=INK, zorder=5)
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=11)
fig.savefig(OUT / "2026-11-19_5_path_all.png", dpi=150, bbox_inches="tight")
print(f"1 カウント = {DEG:.4f} 度、全体の幅 横 {np.ptp(cx[in_run]):.1f} 度・縦 {np.ptp(cy[in_run]):.1f} 度")
print(f"撃った場所の範囲（開始の向きが原点） 横 {cx[in_run].min():.1f}〜{cx[in_run].max():.1f}、"
      f"縦 {cy[in_run].min():.1f}〜{cy[in_run].max():.1f}、中心 ({(cx[in_run].min() + cx[in_run].max()) / 2:.1f}, "
      f"{(cy[in_run].min() + cy[in_run].max()) / 2:.1f})")
mv = (ev.t >= clicks[0]) & (ev.t <= run.start - t0)
print(f"開始のクリックから開始までの動き: {np.abs(ev.dx[mv]).sum()} / {np.abs(ev.dy[mv]).sum()} カウント")
