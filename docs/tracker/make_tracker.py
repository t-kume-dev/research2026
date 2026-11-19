"""研究室の雛形（template.pptx）に thesis-tracker.md の中身を入れて、thesis-tracker.pptx を作る。

    python docs/tracker/make_tracker.py

- 中身の元は thesis-tracker.md だけ。直すときは Markdown を直して、これを回し直す
- 雛形の飾り・配置・英語のフォントはそのまま使い、文字だけ差し替える。日本語はメイリオで出す
- 雛形の 2 枚目（別のイラストの表紙）と 4 枚目（How to use）は外す
- 年表のカードは、日本語が入るように縦だけ伸ばす

必要なもの: python-pptx（lxml は一緒に入る）
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template.pptx"
SOURCE = HERE / "thesis-tracker.md"
OUT = HERE / "thesis-tracker.pptx"

JP = "Meiryo"
VERSION = "November 2026 version"

# 雛形のページ番号（1 始まり）
COVER, COVER_ALT, TIMELINE, HOWTO, FIRST_MONTH, FINAL = 1, 2, 3, 4, 5, 14
TIMELINE_CARD_EXTRA = Pt(44)  # 年表のカードを縦に伸ばす量

# 雛形は月ごとに赤と青緑が入れ替わるが、1 色にそろえる（本人）。表紙はそのまま
ACCENT, DARK = "228DA5", "0D3B42"
RECOLOR = {"E6191C": ACCENT, "F2A1A6": DARK}


# ---------------------------------------------------------------- Markdown を読む

def parse(md: str) -> dict:
    sections = re.split(r"^## ", md, flags=re.M)[1:]
    out = {"timeline": [], "months": [], "final": {}}
    for sec in sections:
        head, _, body = sec.partition("\n")
        head = head.strip()
        body = body.split("\n---")[0]
        if head.startswith("Research Timeline"):
            for line in body.splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) == 3 and cells[0] not in ("月", "---"):
                    out["timeline"].append(cells)
        elif head.startswith("December 2027"):
            for m in re.finditer(r"^- ([^：]+)：(.*)$", body, flags=re.M):
                out["final"][m.group(1).strip()] = m.group(2).strip()
        elif "Research Objectives" in head or head.startswith("Milestone Checkpoint"):
            month = {"title": head, "objectives": [], "tasks": [], "status": "Not started"}
            for m in re.finditer(r"^\d\. ([a-z ]+)：(.*)$", body, flags=re.M):
                month["objectives"].append((m.group(1).strip(), m.group(2).strip()))
            for line in body.splitlines():
                if m := re.match(r"^- ([✓☐]) (.*)$", line):
                    month["tasks"].append({"done": m.group(1) == "✓", "text": m.group(2).strip(), "notes": []})
                elif (m := re.match(r"^  - (.*)$", line)) and month["tasks"]:
                    month["tasks"][-1]["notes"].append(m.group(1).strip())
            if m := re.search(r"\*\*Status\*\*：(.+)", body):
                month["status"] = m.group(1).strip()
            out["months"].append(month)
    return out


# ---------------------------------------------------------------- 文字の差し替え

def _find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:  # group
            if (hit := _find(sh.shapes, name)) is not None:
                return hit
    return None


def find_text(shapes, start):
    """雛形の文字が start で始まる図形を探す（図形の名前はページごとにずれるので、中身で探す）。"""
    for sh in shapes:
        if sh.shape_type == 6:
            try:
                return find_text(sh.shapes, start)
            except KeyError:
                continue
        elif sh.has_text_frame and sh.text_frame.text.strip().startswith(start):
            return sh
    raise KeyError(start)


def find(shapes, name):
    if (hit := _find(shapes, name)) is None:
        raise KeyError(name)
    return hit


def _run(rpr_tpl, text, size=None, bold=None, color=None):
    r = copy.deepcopy(rpr_tpl.getparent())  # <a:r>
    rpr = r.find(qn("a:rPr"))
    for k in ("b", "strike", "u"):
        rpr.attrib.pop(k, None)
    if size:
        rpr.set("sz", str(int(size * 100)))
    if bold:
        rpr.set("b", "1")
    rpr.set("lang", "ja-JP")
    if color:
        fill = rpr.find(qn("a:solidFill"))
        fill.find(qn("a:srgbClr")).set("val", color)
    ea = rpr.find(qn("a:ea"))
    if ea is not None:
        ea.set("typeface", JP)  # 日本語はメイリオ。英数字は雛形のフォントのまま
    r.find(qn("a:t")).text = text
    return r


def _para(ppr_tpl, runs, line_pt=None, before_pt=None):
    p = ppr_tpl.makeelement(qn("a:p"), {})
    ppr = copy.deepcopy(ppr_tpl)
    if line_pt:
        ln = ppr.find(qn("a:lnSpc"))
        if ln is not None:
            ln.find(qn("a:spcPts")).set("val", str(int(line_pt * 100)))
    if before_pt is not None:
        for old in ppr.findall(qn("a:spcBef")):
            ppr.remove(old)
        sb = ppr.makeelement(qn("a:spcBef"), {})
        sb.append(sb.makeelement(qn("a:spcPts"), {"val": str(int(before_pt * 100))}))
        ln = ppr.find(qn("a:lnSpc"))
        (ln.addnext(sb) if ln is not None else ppr.insert(0, sb))
    p.append(ppr)
    for r in runs:
        p.append(r)
    return p


def _insert_bullet(ppr, bu):
    """箇条書きの記号を、スキーマの順（tabLst・defRPr・extLst より前）に入れる。"""
    for tag in ("a:tabLst", "a:defRPr", "a:extLst"):
        if (after := ppr.find(qn(tag))) is not None:
            after.addprevious(bu)
            return
    ppr.append(bu)


def _templates(shape):
    """雛形の段落ごとの (pPr, rPr)。"""
    out = []
    for p in shape.text_frame._txBody.findall(qn("a:p")):
        ppr = p.find(qn("a:pPr"))
        r = p.find(qn("a:r"))
        out.append((ppr, r.find(qn("a:rPr")) if r is not None else None))
    return out


def _replace(shape, paras):
    body = shape.text_frame._txBody
    for p in body.findall(qn("a:p")):
        body.remove(p)
    for p in paras:
        body.append(p)


def set_simple(shape, lines, size=None, bold_first=False):
    """1 行目の書式で、行を差し替える。"""
    (ppr, rpr), *_ = [t for t in _templates(shape) if t[1] is not None]
    paras = [_para(ppr, [_run(rpr, ln, size, bold_first and i == 0)]) for i, ln in enumerate(lines)]
    _replace(shape, paras)


# ---------------------------------------------------------------- ページごと

def fill_cover(slide):
    set_simple(find_text(slide.shapes, "October 2026 version"), [VERSION])


def fill_timeline(slide, rows):
    # 月の見出し（TextBox）と中身（その下の TextBox）、カード（Group）を位置で対応づける
    heads = {sh.text_frame.text.strip(): sh for sh in slide.shapes
             if sh.has_text_frame and re.match(r"^[A-Z][a-z]+.* 20\d\d$", sh.text_frame.text.strip())}
    for month, objective, milestones in rows:
        head = heads[month]
        body = next(sh for sh in slide.shapes if sh.has_text_frame and sh is not head
                    and abs(sh.left - head.left) < Pt(2) and Pt(0) < sh.top - head.top < Pt(40))
        card = next(sh for sh in slide.shapes if sh.shape_type == 6
                    and sh.left <= head.left <= sh.left + sh.width and sh.top <= head.top <= sh.top + Pt(20))
        card.height += TIMELINE_CARD_EXTRA
        tpl = [t for t in _templates(body) if t[1] is not None][0]
        ppr, rpr = tpl
        if month in ("December 2027", "January 2028"):
            # 雛形の英語の 1 文は残し、下にマイルストーンを足す
            keep = body.text_frame.text.replace("\n", " ").strip()
            items = [keep, "・" + milestones]
        else:
            items = ["・" + objective, "・" + milestones]
        body.width = card.width - (body.left - card.left) * 2
        _replace(body, [_para(ppr, [_run(rpr, t, size=11)], line_pt=15) for t in items])


def fill_month(slide, m, title_shape="TextBox 2"):
    set_simple(find(slide.shapes, title_shape), [m["title"]])

    # Objectives / Milestones
    obj = find_text(slide.shapes, "objective")
    ppr, rpr = _templates(obj)[0]
    labels = {"objective": "Objective", "milestone": "Milestone", "success criteria": "Success criteria"}
    paras = []
    for i, (key, text) in enumerate(m["objectives"]):
        paras.append(_para(ppr, [_run(rpr, labels.get(key, key), 15, bold=True, color="123A40")],
                           line_pt=20, before_pt=0 if i == 0 else 8))
        paras.append(_para(ppr, [_run(rpr, text, 13)], line_pt=18, before_pt=0))
    _replace(obj, paras)
    # 番号は見出しの行だけに付ける（中身の行は番号なし・同じ字下げ）。間に番号なしの行が入るので、番号は明示する
    for k, p in enumerate(obj.text_frame._txBody.findall(qn("a:p"))):
        pp = p.find(qn("a:pPr"))
        for b in pp.findall(qn("a:buAutoNum")) + pp.findall(qn("a:buNone")) + pp.findall(qn("a:buChar")):
            pp.remove(b)
        bu = (pp.makeelement(qn("a:buNone"), {}) if k % 2 == 1 else
              pp.makeelement(qn("a:buAutoNum"), {"type": "arabicPeriod", "startAt": str(k // 2 + 1)}))
        _insert_bullet(pp, bu)
        if k % 2 == 1:
            pp.set("indent", "0")  # 中身の行は、見出しの文字の頭にそろえる（ぶら下げをやめる）

    # Planned Activities
    act = find_text(slide.shapes, "☐ task")
    tpls = _templates(act)
    task_ppr, task_rpr = tpls[0]
    note_ppr, note_rpr = tpls[1]
    paras = []
    for i, t in enumerate(m["tasks"]):
        mark = "✓" if t["done"] else "☐"
        paras.append(_para(task_ppr, [_run(task_rpr, f"{mark} {t['text']}", 14)],
                           line_pt=19, before_pt=0 if i == 0 else 9))
        for n in t["notes"]:
            paras.append(_para(note_ppr, [_run(note_rpr, n, 12)], line_pt=16, before_pt=1))
    _replace(act, paras)

    # Status：今の状態だけ太字
    st = find_text(slide.shapes, "Not started")
    ppr, rpr = _templates(st)[0]
    runs = []
    for i, s in enumerate(("Not started", "In progress", "Complete")):
        if i:
            runs.append(_run(rpr, "  ·  ", 24))
        runs.append(_run(rpr, s, 24, bold=(s == m["status"]), color="123A40" if s == m["status"] else None))
    _replace(st, [_para(ppr, runs)])

    # Supervisor Comments：先生が書くので空ける（行は残す）
    sc = find_text(slide.shapes, "Record feedback")
    ppr, rpr = [t for t in _templates(sc) if t[1] is not None][0]
    _replace(sc, [_para(ppr, [_run(rpr, "")]) for _ in range(14)])


def fill_final(slide, final):
    box = find_text(slide.shapes, "Milestone description")
    tpls = [t for t in _templates(box) if t[1] is not None]
    ppr, rpr = tpls[0]
    paras = []
    for i, (k, v) in enumerate(final.items()):
        runs = [_run(rpr, k, 18, bold=True)]
        paras.append(_para(ppr, runs, line_pt=24, before_pt=0 if i == 0 else 10))
        if v:
            paras.append(_para(ppr, [_run(rpr, v, 14, color="4A6B6E")], line_pt=20, before_pt=0))
    _replace(box, paras)


def unify_colors(slide):
    for clr in slide._element.iter(qn("a:srgbClr")):
        if (new := RECOLOR.get(clr.get("val", "").upper())):
            clr.set("val", new)


def drop_slides(prs, numbers):
    ids = prs.slides._sldIdLst
    for n in sorted(numbers, reverse=True):
        sld = ids[n - 1]
        prs.part.drop_rel(sld.get(qn("r:id")))
        ids.remove(sld)


def main():
    data = parse(SOURCE.read_text(encoding="utf-8"))
    prs = Presentation(TEMPLATE)
    slides = list(prs.slides)

    fill_cover(slides[COVER - 1])
    fill_timeline(slides[TIMELINE - 1], data["timeline"])

    month_slides = slides[FIRST_MONTH - 1:FINAL - 1]
    if len(month_slides) != len(data["months"]):
        raise SystemExit(f"月のページ数が合いません: 雛形 {len(month_slides)} / Markdown {len(data['months'])}")
    for s, m in zip(month_slides, data["months"]):
        tpl_title = find(s.shapes, "TextBox 2").text_frame.text.strip()
        if tpl_title != m["title"]:
            raise SystemExit(f"見出しが雛形と違います: {tpl_title!r} / {m['title']!r}")
        fill_month(s, m)
    fill_final(slides[FINAL - 1], data["final"])

    for i, s in enumerate(slides, 1):
        if i != COVER:
            unify_colors(s)
    drop_slides(prs, [COVER_ALT, HOWTO])
    prs.save(OUT)
    print(f"保存: {OUT}")


if __name__ == "__main__":
    main()
