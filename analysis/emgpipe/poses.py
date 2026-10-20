"""記録中の窓に出す、課題ごとの姿勢の模式図。

draw(ax, task) で ax に描く。emgpipe/img/<task>.png（写真など）があれば、図の代わりにそれを出す。
色はスライドと同じ（伸筋側は青、屈筋側は橙）。座標は横 10 × 縦 7。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
from matplotlib.patches import Circle, FancyArrow, FancyBboxPatch, Rectangle

IMG_DIR = Path(__file__).with_name("img")

INK, GRAY, BLUE, ORANGE = "#1A1A1A", "#6B6B6B", "#1F6FB4", "#E07B1A"
SKIN, SKIN_LINE, DESK, RESIST, BOARD = "#F1E3D6", "#8A7A6C", "#DDDDDD", "#A6A6A6", "#8A7A6C"


def _rect(ax, x, y, w, h, color, edge=None, r=0.0, rot=0.0):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=color,
                       ec=edge or "none", lw=1.5)
    if rot:
        from matplotlib.transforms import Affine2D
        p.set_transform(Affine2D().rotate_deg_around(x, y + h / 2, rot) + ax.transData)
    ax.add_patch(p)


def _arrow(ax, x, y, dx, dy, color):
    ax.add_patch(FancyArrow(x, y, dx, dy, width=0.18, head_width=0.55, head_length=0.45,
                            length_includes_head=True, color=color))


def _label(ax, x, y, text, color=GRAY, size=13, ha="left", bold=True):
    ax.text(x, y, text, color=color, fontsize=size, ha=ha, va="center", fontweight="bold" if bold else "normal")


def _forearm(ax, y, palm, fist=True):
    """横から見た前腕と手。palm は "下" か "上"。"""
    _rect(ax, 0.6, y, 5.6, 1.0, SKIN, SKIN_LINE, 0.25)
    if fist:
        _rect(ax, 6.1, y - 0.2, 1.4, 1.4, SKIN, SKIN_LINE, 0.3)
    _label(ax, 0.8, y + 1.45, f"手のひら{palm}", INK, 13)


def _desk(ax, y=1.6, label="机"):
    ax.add_patch(Rectangle((0.3, y - 0.8), 9.4, 0.8, fc=DESK, ec="none"))
    _label(ax, 0.5, y - 0.4, label, GRAY, 11, bold=False)


def _press(ax, x, y, who="他の人"):
    """上から押さえる手（灰色）と下向きの矢印。"""
    ax.add_patch(Rectangle((x - 0.6, y), 1.2, 0.35, fc=RESIST, ec="none"))
    _arrow(ax, x, y + 1.5, 0, -1.05, RESIST)
    _label(ax, x - 0.9, y + 1.0, who, GRAY, 12, ha="right")


def _board(ax, x, y):
    """天板の裏（上から押さえる板）。"""
    ax.add_patch(Rectangle((x - 1.6, y), 3.2, 0.3, fc=BOARD, ec="none"))
    _label(ax, x - 1.6, y + 0.65, "天板の裏", GRAY, 12)


def _bend(ax, palm, col, note="誰も押さえない"):
    _desk(ax)
    _rect(ax, 0.6, 1.6, 5.6, 1.0, SKIN, SKIN_LINE, 0.25)
    _rect(ax, 6.0, 2.3, 1.7, 0.85, SKIN, SKIN_LINE, 0.3, rot=50)
    _label(ax, 0.8, 3.05, f"手のひら{palm}", INK, 13)
    _arrow(ax, 8.6, 2.4, 0, 2.2, col)
    _label(ax, 4.6, 5.6, note, col, 13)
    _label(ax, 4.6, 5.0, "上に曲げきる", col, 13)


def _wrist_press(ax, palm, col, who):
    if who != "天板":  # 一人用は前腕を浮かせて天板の裏に差し込むので、机は描かない
        _desk(ax)
    _forearm(ax, 1.6, palm)
    if who == "天板":
        _board(ax, 6.8, 2.85)
    else:
        _press(ax, 6.8, 3.0, who)
    _arrow(ax, 8.4, 2.0, 0, 2.4, col)
    _label(ax, 8.9, 4.6, "全力で上へ", col, 13, ha="right")


def _person_side(ax, seated=True):
    """横から見た上半身（右向き）。肩の位置を返す。"""
    ax.add_patch(Circle((2.0, 6.0), 0.45, fc=SKIN, ec=SKIN_LINE, lw=1.5))
    ax.plot([2.0, 2.0], [5.5, 2.6], color=SKIN_LINE, lw=6, solid_capstyle="round")
    if seated:
        ax.plot([2.0, 3.6, 3.6], [2.6, 2.6, 0.6], color=SKIN_LINE, lw=6, solid_capstyle="round")
        ax.add_patch(Rectangle((1.0, 2.0), 2.4, 0.3, fc=DESK, ec="none"))
    return 2.0, 5.2


def _elbow(ax, mode):
    sx, sy = _person_side(ax)
    ex, ey = sx + 0.2, sy - 2.0
    ax.plot([sx, ex], [sy, ey], color=SKIN_LINE, lw=6, solid_capstyle="round")         # 上腕
    ax.plot([ex, ex + 3.2], [ey, ey], color=SKIN_LINE, lw=6, solid_capstyle="round")  # 前腕
    ax.add_patch(Circle((ex + 3.4, ey), 0.35, fc=SKIN, ec=SKIN_LINE, lw=1.5))
    _label(ax, ex + 0.2, ey - 0.5, "肘 90°", INK, 12)
    if mode == "flex":
        _board(ax, ex + 3.4, ey + 0.45)
        _arrow(ax, ex + 4.4, ey - 0.3, 0, 1.6, BLUE)
        _label(ax, ex + 0.6, ey + 1.6, "手のひら上", INK, 13)
    else:
        ax.add_patch(Rectangle((ex + 2.4, ey - 0.75), 4.0, 0.4, fc=DESK, ec="none"))
        _label(ax, ex + 5.0, ey - 1.05, "机", GRAY, 11, bold=False)
        _arrow(ax, ex + 4.4, ey + 1.4, 0, -1.4, BLUE)
        _label(ax, ex + 0.6, ey + 1.6, "こぶしの小指側を机に", INK, 13)


def _person_front(ax, y0=0.6, seated=False):
    """正面から見た上半身。左右の肩の位置を返す。"""
    cx = 5.0
    ax.add_patch(Circle((cx, y0 + 5.4), 0.5, fc=SKIN, ec=SKIN_LINE, lw=1.5))
    ax.plot([cx - 1.2, cx + 1.2], [y0 + 4.5, y0 + 4.5], color=SKIN_LINE, lw=6, solid_capstyle="round")
    ax.plot([cx, cx], [y0 + 4.9, y0 + 1.8], color=SKIN_LINE, lw=6, solid_capstyle="round")
    if seated:
        ax.add_patch(Rectangle((cx - 2.2, y0 + 1.2), 4.4, 0.4, fc=DESK, ec="none"))
        _label(ax, cx + 2.4, y0 + 1.4, "座面", GRAY, 11, bold=False)
    return (cx - 1.2, y0 + 4.5), (cx + 1.2, y0 + 4.5)


def _abduction(ax):
    (lx, ly), (rx, ry) = _person_front(ax)
    ax.plot([lx, lx - 0.3, lx - 0.3], [ly, ly - 1.7, ly - 3.2], color=SKIN_LINE, lw=6, solid_capstyle="round")
    ax.plot([rx, rx + 0.3, rx + 0.3], [ry, ry - 1.7, ry - 3.2], color=SKIN_LINE, lw=6, solid_capstyle="round")
    ax.add_patch(Rectangle((rx + 0.75, 0.3), 0.4, 6.4, fc=BOARD, ec="none"))
    _label(ax, rx + 1.35, 6.4, "壁", GRAY, 12)
    _arrow(ax, rx - 0.5, ry - 1.7, 1.15, 0, BLUE)


def _shrug(ax):
    (lx, ly), (rx, ry) = _person_front(ax, seated=True)
    for x, s in ((lx, -1), (rx, 1)):
        ax.plot([x, x + 0.3 * s, x + 0.9 * s], [ly, ly - 2.0, ly - 3.3], color=SKIN_LINE, lw=6,
                solid_capstyle="round")
        _arrow(ax, x - 0.6 * s, ly, 0, 1.2, BLUE)


def _rest(ax):
    _desk(ax)
    _forearm(ax, 1.6, "下", fist=False)
    _rect(ax, 6.0, 1.6, 2.0, 0.8, "#FFFFFF", GRAY, 0.4)
    _label(ax, 7.0, 3.0, "マウス", GRAY, 12, ha="center")
    _label(ax, 0.8, 5.0, "力を抜いて、動かない", INK, 14)


DRAW = {
    "rest": _rest,
    "free_extension": lambda ax: _bend(ax, "下", BLUE),
    "free_flexion": lambda ax: _bend(ax, "上", ORANGE),
    "ext_fist_pron": lambda ax: _wrist_press(ax, "下", BLUE, "他の人"),
    "flex_fist_sup": lambda ax: _wrist_press(ax, "上", ORANGE, "他の人"),
    "ext_fixed_solo": lambda ax: _wrist_press(ax, "下", BLUE, "天板"),
    "flex_fixed_solo": lambda ax: _wrist_press(ax, "上", ORANGE, "天板"),
    "shoulder_abduction_solo": _abduction,
    "elbow_flexion_solo": lambda ax: _elbow(ax, "flex"),
    "elbow_extension_solo": lambda ax: _elbow(ax, "ext"),
    "shoulder_shrug_solo": _shrug,
}


def draw(ax, task: str) -> None:
    ax.clear()
    ax.set_axis_off()
    photo = IMG_DIR / f"{task}.png"
    if photo.exists():
        ax.imshow(mpimg.imread(photo))
        return
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    if task in DRAW:
        DRAW[task](ax)
