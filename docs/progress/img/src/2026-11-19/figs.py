"""11-19 の報告用の図の下書き（見せて決めるため）。"""
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

# ---- 図 1: 記録の細かさ
fig, ax = plt.subplots(figsize=(9, 3.6))
labels = ["裏で記録（ゲーム中と同じ）", "裏で記録・受け方を変更", "記録する側を前面にする"]
hz = [127, 125, 4335]
y = np.arange(3)[::-1]
ax.barh(y, hz, height=0.5, color=[GRAY, GRAY, INK])
for yi, h in zip(y, hz):
    ax.text(h + 60, yi, f"{h:,} 回/秒（{1000 / h:.2f} ms ごと）", va="center", color=INK)
ax.set_yticks(y, labels)
ax.set_xlim(0, 7600)
ax.axvline(4000, color=LIGHT, lw=1.5, ls="--")
ax.text(4000, 2.55, "マウスの性能 4000 回/秒", color=GRAY, ha="center", fontsize=11)
ax.set_xlabel("マウスの動きが届いた回数 [回/秒]（同じマウス・同じ PC、5 秒ずつ）")
ax.tick_params(axis="y", length=0)
fig.tight_layout()
fig.savefig(OUT / "2026-11-19_1_rate.png", dpi=150)

# ---- 図 2: 倒した時刻とクリック
raw = Path(r"C:\Users\akash\Documents\lab\research2026\data\raw\2026-11-17")
ev = Events.load(raw / "kovaaks_test.csv")
t0 = ev.meta["t0_unix"]
run = parse_stats(next((raw / "kovaaks").glob("*Stats.csv")))
clicks = ev.clicks
kills = run.kills - t0
j = np.searchsorted(clicks, kills + 0.05, side="right") - 1
gap_ms = (kills - clicks[j]) * 1000

fig = plt.figure(figsize=(14, 6.6))
gs = fig.add_gridspec(2, 2, width_ratios=[2.6, 1], hspace=0.65, wspace=0.18)
a1, az, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])
for ax_, (w0, w1), lw in ((a1, (0, float(ev.t[-1])), 1.0), (az, (20, 30), 2.0)):
    c = clicks[(clicks >= w0) & (clicks <= w1)]
    k = kills[(kills >= w0) & (kills <= w1)]
    ax_.vlines(c, 0.1, 0.9, color=GRAY, lw=lw)
    ax_.vlines(k, 1.1, 1.9, color=ACCENT, lw=lw * 1.2)
    ax_.set_yticks([0.5, 1.5], ["記録した\n左クリック", "KovaaK's の\n倒した時刻"])
    ax_.set_xlim(w0, w1)
    ax_.tick_params(axis="y", length=0)
    ax_.spines["left"].set_visible(False)
a1.set_ylim(0, 2.3)
az.set_ylim(0, 2)
a1.axvspan(clicks[0] - 0.3, run.start - t0, color=LIGHT, alpha=0.4, lw=0)
a1.text((run.start - t0 + clicks[0]) / 2, 2.0, "開始前", ha="center", va="bottom", fontsize=10, color=GRAY)
a1.axvspan(20, 30, ymin=0, ymax=0.87, color=LIGHT, alpha=0.5, lw=0)
a1.set_xlabel("記録開始からの時刻 [s]")
a1.set_title(f"記録 70 秒の全体：倒した的 {len(kills)} 体、撃った {run.total_shots} 発、左クリック {len(clicks)} 回"
             "（開始前・終了後を含む）", color=INK, fontsize=12, loc="left")
az.set_xlabel("記録開始からの時刻 [s]")
miss_z = [m_ for m_ in clicks[(clicks >= 20) & (clicks <= 30)] if not np.any(np.abs(kills - m_) < 0.05)]
for m_ in miss_z:
    az.annotate("外した\nクリック", (m_, 0.9), xytext=(m_, 1.25), ha="center", fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8))
az.set_title("拡大（灰色の帯）：クリック 1 回ごとに倒した時刻が 1 つ。外したクリックには対応がない",
             color=INK, fontsize=12, loc="left")

a2.hist(gap_ms, bins=np.arange(0, 8.5, 0.5), color=ACCENT, edgecolor="white")
a2.set_xlabel("倒した時刻 − 直前のクリック [ms]")
a2.set_ylabel("的の数")
a2.set_title(f"時刻のずれ：{len(gap_ms)} 体すべて\n{gap_ms.min():.1f}〜{gap_ms.max():.1f} ms", color=INK, fontsize=12, loc="left")
a2.yaxis.get_major_locator().set_params(integer=True)
fig.savefig(OUT / "2026-11-19_2_align.png", dpi=150, bbox_inches="tight")

# ---- 図 3: マウスの速さと、当たり・外れのクリック（1 回ぶんの見本）
# 倒すまでに撃った数 n のうち、最後の 1 発が当たり、残りが外れ
hit = np.zeros(len(clicks), bool)
hit[j] = True
i0 = j[0] - (int(run.shots_per_kill[0]) - 1)  # 最初の的までに外した分もさかのぼる（開始のクリックは除く）
in_run = (np.arange(len(clicks)) >= i0) & (clicks <= kills[-1] + 0.05)
t = ev.t
spd = np.hypot(ev.dx, ev.dy)
# 8 ms ごとに届くので、50 ms の窓で速さ（カウント/秒）にする
edges = np.arange(0, t[-1], 0.01)
cnt, _ = np.histogram(t, bins=edges, weights=spd)
kern = np.ones(5) / 0.05
v = np.convolve(cnt, kern, mode="same") * 0.07 * float(run.info["Horiz Sens"])  # 度/秒
tc = edges[:-1] + 0.005
fig, (top, ax) = plt.subplots(2, 1, figsize=(13, 6.6), gridspec_kw={"height_ratios": [1, 1.4], "hspace": 0.55})
z0, z1 = 20, 30
for a_, (w0, w1), sz in ((top, (0, float(ev.t[-1])), 14), (ax, (z0, z1), 45)):
    m = (tc >= w0) & (tc <= w1)
    a_.plot(tc[m], v[m], color=INK, lw=0.8 if a_ is top else 1.2)
    ch = clicks[in_run & hit & (clicks >= w0) & (clicks <= w1)]
    cm = clicks[in_run & ~hit & (clicks >= w0) & (clicks <= w1)]
    a_.scatter(ch, np.interp(ch, tc, v), s=sz, color=ACCENT, zorder=3, label="当たったクリック")
    a_.scatter(cm, np.interp(cm, tc, v), s=sz, facecolor="white", edgecolor=INK, lw=1.2, zorder=3,
               label="外したクリック")
    a_.set_xlim(w0, w1)
    a_.set_ylabel("照準が回る速さ\n[度/秒]", fontsize=11)
top.axvspan(z0, z1, color=LIGHT, alpha=0.5, lw=0)
top.set_title("1 回ぶん全体（灰色の帯を下で拡大）", loc="left", fontsize=13)
top.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=11)
ax.set_title("拡大：的ごとに「加速 → 減速 → 止まって撃つ」をくり返している", loc="left", fontsize=13)
ax.set_xlabel("記録開始からの時刻 [s]")
fig.savefig(OUT / "2026-11-19_3_speed_hits.png", dpi=150, bbox_inches="tight")

print("当たり", int((in_run & hit).sum()), "外れ", int((in_run & ~hit).sum()))
print(OUT)
