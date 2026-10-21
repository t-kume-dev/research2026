"""2026-10-22 の進捗報告スライドを作る。

    python docs/progress/slides/src/2026-10-22.py

docs/progress/slides/2026-10-22.pptx に書き出す。次の週は、このファイルをコピーして
中身（NOTES と各スライド）を差し替える。
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from pptx_kit import *  # noqa: E402,F401,F403
from pptx_kit import px  # noqa: E402

sys.path.insert(0, str(REPO / "analysis"))
from emgpipe import poses  # noqa: E402

IMG = REPO / "docs/progress/img"

NOTES = {
    "cover": """\n今週は、研究室での計測を、準備から 3 分の記録までコマンド 1 つで流せるようにして、10-20 に研究室で一人で記録しました。結論から言うと、センサ 6 本・3 分の記録まで止まらずに通り、手首の伸展の MVC は一人で取れました。屈曲は確かめられませんでした。画面の指示が足りなかった可能性があるので、指示を直して来週取り直します。

流れは、マイルストーン → 目標 → やったこと → わかったこと → 次やること → まとめ、の順で話します。
""",
    "roadmap": """\n先週、マイルストーンがあるとよいとコメントをもらったので作りました。今は M1、計測系が回るところで、期限は 11/5 です。下が M1 の内訳で、左の 3 つは先週までに済んでいます。今週は M1-4 から M1-6 をやりました。
""",
    "goal": """\n大きな目標は、今のマイルストーンの M1 にそろえました。先週までの『違いが出ているデータを確認する』は、計測系を作る部分と、エイム中の差を確かめる部分が混ざっていたので、後ろの半分は M2 に回しています。10/1 に見た伸筋と屈筋の違いは、センサが筋を分けて拾えているかの確認で、M1 の一部です。

M1 の完了基準は、6 か所の MVC と数分の記録を、API で 1 回の来室で取りきれることです。

そのための小さな目標として、M1 の内訳のうち 3 つをやりました。M1-4 は、研究室での計測を、lab という 1 つのコマンドで最後まで通せるようにすること。M1-5 は、センサ 6 本の同時記録と、数分の長い記録を確かめること。M1-6 は、前腕の MVC を API で、一人で取ることです。順番は、確認動作 → 伸展（H：天板の裏を押し上げる）→ 屈曲です。

【用語】MVC は、全力で力を入れたときの筋電の大きさです。これを 100% として、ほかの記録を割合（%MVC）で表すと、日や人が違っても比べられます。
""",
    "done": """\nやったことです。

まず、修論までのマイルストーン（M1〜M7）と、M1 の内訳（M1-1〜M1-7）を作りました。内訳は M1 の始まりから完了基準までの流れにしていて、先週までに済んだ M1-1〜M1-3 も入っています。

次に、研究室での計測を lab という 1 つのコマンドで流せるようにしました。信号の確認 → 安静 → 確認動作 → MVC → 3 分の記録、を順に流し、最後に MVC を比べます。記録中の窓に指示が出て、クリックで次に進むので、ターミナルに戻らなくてよいです。

センサ 6 本を、シールの番号（1〜6）で基地局に登録し直しました（ペアリング）。そのための pair コマンドも作りました。

10-20 に研究室で一人で記録しました。6 か所に貼り、部位ごとに動かして、番号と部位の対応を確かめました（30 秒）。それから lab を一人用で流しました。伸展は H（天板の裏を押し上げる）、屈曲は机に押し下げる。各 5 秒 × 3、休憩 60 秒です。

使ってみて分かった記録中の窓の使いにくさ（文字があふれる、休憩が長い、動作が分からない）を直しました。

MVC の取り方を決めました。手首は、伸展・屈曲とも「上に全力で曲げ、人に押さえてもらう」を本番にします。一人で試すときは天板の裏を押し上げます。残り 4 か所（三角筋・二頭筋・三頭筋・僧帽筋）は、一人でできるやり方を決めました。来週試します。

【用語】
H：一人で取る伸展の MVC。手のひら下で握り、天板の裏に手の甲を当てて押し上げる。10-06 に試したが CSV を書き出しそこね、今回が初めての確認。
コードの場所：計測の手順は analysis/emgpipe/session.py（python -m emgpipe lab、一人用は --solo）。ペアリングは sources.py の DelsysSource.pair（python -m emgpipe pair 1 2 3 4 5 6）。
""",
    "m1_4": """\nM1-4 への答えです。研究室での計測が、最後まで止まらずに通りました。ただし、記録中の窓が使いにくかったです。

lab で 11 ステップが止まらずに通りました。開始から終わりまで約 15 分です。

使ってみて、3 つ困りました。説明の文字が窓からあふれて読めない。休憩の 60 秒が長い。文字だけでは、どういう姿勢で力を入れるのか分からない。

3 つとも直しました。説明を折り返し、見出しと分けました。課題を 1 周ずつ回し、休憩を 10 秒にしました。窓の左に姿勢の図を出すようにしました。

休憩を短くした理由です。同じ課題を 3 回続けると、休憩が短いと 2 回目以降が疲れで小さくなります。6 課題を 1 周ずつ回せば、休憩 10 秒でも同じ筋が次に使われるまで約 1 分空きます。文献の休憩は 30 秒〜1 分（literature/notes/MVC_protocols.md）なので守れます。2 周で、MVC の部分は約 4 分です（クリックの時間を除く）。

直した窓は、まだ実機では使っていません。来週確かめます。

【コードの場所】記録中の窓は analysis/emgpipe/plot.py の LiveView。姿勢の図は analysis/emgpipe/poses.py（emgpipe/img/<課題名>.png を置けば、図の代わりに写真を出す）。
""",
    "m1_5": """\nM1-5 への答えです。6 本とも取れ、3 分の記録も取りこぼしませんでした。

3 分の記録で、6 本とも 386,667 サンプルで、3 分 × 2148 Hz とちょうど同じでした。

グラフは、部位の確認の記録です。脱力のあと、部位ごとに自分で動かしました。6 本とも、貼った部位の動きでいちばん大きく反応し、脱力の 2.4〜8 倍でした。番号と部位の対応は合っています。

【部位の確認（sites_identify）：脱力 → 自分の動き、包絡線の平均、μV】
S1 前腕の上（伸筋群）3.2 → 16.4
S2 前腕の下（屈筋群）2.3 → 19.6
S3 三角筋中部 2.0 → 10.6
S4 上腕二頭筋 2.0 → 14.5
S5 上腕三頭筋 6.4 → 15.3
S6 僧帽筋上部 9.0 → 66.6

【うまくいかなかったこと】最初は 5 本しか見つかりませんでした。基地局はペアになったセンサしか見つけず、6 本目はこの基地局とペアになっていませんでした。ほかの人の登録で番号もばらばら（0・1・3・16・17）だったので、シールの番号 1〜6 に登録し直しました。センサを充電台に載せたまま Enter を押し、すぐ外すとつながりました。研究室のほかの人の番号も変わっています。

【50 Hz の判定】脱力の信号のうち、電源の雑音（50 Hz とその倍数）が占める割合。10-13 に浮いていたときは 97%。10-20 の S2 は 57% だったが、脱力が 2.3 μV と小さいだけで、曲げると 8 倍に上がった。判定の基準を 50% から 80% に上げた。
""",
    "m1_6": """\nM1-6 への答えです。伸展は一人（H）で足りました。屈曲は確かめられませんでした。

確認動作は、誰も押さえずに、自由に全力で曲げきる動きです。これが MVC の何 % になるかで、MVC の課題が全力を捉えているかを判断します。100% 以下なら足りています。疲れる前の最初に取ります。

伸展（H）は、確認動作が H の MVC の 69% に収まりました。一人で全力を取れています。3 回の値は 44・47・46 μV で、ばらつきも小さいです。

屈曲（机に押し下げる）は、確認動作が MVC の約 10% で、数字の上では基準を満たしました。ただし、確認動作で屈筋側は 5.4 μV しか上がっていません。手のひら下のまま曲げていて、手のひら下では重力で手が下がるので、屈筋をほとんど使いません。この確認動作では、屈曲の MVC が全力かは確かめられません。

下の段が、その原因と直したことです。10-20 の画面の指示は「誰も押さえず、手首を全力で曲げきる」だけで、手の向きも姿勢の図もありませんでした。指示を読み切れず、手のひら下のまま曲げた可能性があります。そこで指示を「手のひら上。誰も押さえず、手首を上に全力で曲げきる」に直し、窓の左に姿勢の図を出すようにしました。M1-4 で直した窓と同じものです。来週、この指示で取り直します。

本番の取り方は、手首の伸展・屈曲とも「上に全力で曲げ、人に押さえてもらう」としました。伸展は B（手のひら下・握る、こぶしを上から押さえてもらって上に反らす。10-06 で確認動作 56%）、屈曲は I（手のひら上・握る、押さえてもらって上に曲げる）。屈曲を下向きにすると重力が手伝うので、確認動作が成り立ちません。今回の一人のやり方は試すとき用です。

【10-20 の数値（包絡線の 0.5 秒移動平均の最大、μV）】
確認動作・伸展：S1 32.8、S2 6.0
確認動作・屈曲（手のひら下）：S1 27.8、S2 5.4
伸展 H × 3：S1 44.1・47.4・46.3
屈曲（押し下げ）× 3：S2 48.6・44.7・55.6
%MVC は 3 回の最大に対する割合（32.8 / 47.4 = 69%、5.4 / 55.6 = 10%）。

【コードの場所】窓の指示は analysis/emgpipe/session.py の build_steps。
""",
    "next": """\n次やることです。

M1-7 で、残り 4 か所の MVC を、一人でできるやり方で試します。lab にはもう入れてあります。図は記録中の窓に出す姿勢の図です。

三角筋は、壁の横に立ち、腕を下ろしたまま肘の外側で壁を横に押します。二頭筋は、肘 90°・手のひら上で、天板の裏を持ち上げます。三頭筋は、肘 90°・こぶしの小指側を机に置いて押し下げます。僧帽筋は、座面の端を下から握り、肩をすくめます。

同じ日に、M1-6 の手首の屈曲を、直した指示で取り直します。確認動作は手のひら上で上に曲げきる、課題は天板の裏を押し上げる、です。

あわせて、直した窓（図・折り返し・休憩 10 秒）を実機で使って確かめます。

【コードの場所】課題の説明は analysis/emgpipe/calibration.py の MVC_TASKS。
""",
    "summary": """\nまとめです。

大きな目標の M1 は、完了基準のうち「API で 1 回の来室で取りきる」「数分の記録」はできました。残りは前腕以外 4 か所の MVC と、手首の屈曲の確かめです。

小さな目標は、M1-4 が済です。計測が最後まで通り、窓の使いにくさは直しました。実機での確認は来週です。M1-5 も済で、6 本・3 分で取りこぼしはありませんでした。M1-6 は、伸展は済（一人で 69%）、屈曲は指示を直したので来週取り直します。

来週は、M1-6 の屈曲と M1-7 をやります。
""",
    "records": """\n（予備）10-20 の数値です。包絡線の 0.5 秒移動平均の最大で、単位は μV です。

前腕以外（S3〜S6）の MVC は、手首の課題だけで取ったので、値は使いません。

記録は data/raw/2026-10-20/ にあります（Git 管理外）。sites_identify.npz はもとの名前が check_sites で、確認動作（check_）として数えられてしまったので名前を変えました。センサと部位の対応は sensors.json にあります。
""",
}


def render_pose(task):
    """記録中の窓と同じ姿勢の図を png にする。"""
    out = IMG / f"2026-10-22_pose_{task}.png"
    plt.rcParams["font.family"] = ["Meiryo", "Yu Gothic", "DejaVu Sans"]
    fig = plt.figure(figsize=(5, 3.5), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    poses.draw(ax, task)
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def flow(s, y, steps, w=340, gap=72, h=200, x0=116, size=32):
    """左から右へ箱を並べ、矢印でつなぐ。steps は (ラベル, 本文, 強調するか)。"""
    for i, (lab, body, hot) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(s, x, y, w, h, fill=PALE_BLUE if hot else PALE_GRAY, line=BLUE if hot else RULE,
            radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(16, 12, 16, 12), paras=[
                P(lab, 22, True, BLUE if hot else GRAY, align=PP_ALIGN.CENTER, after=6),
                P(body, size, True, align=PP_ALIGN.CENTER, spacing=1.2)])
        if i < len(steps) - 1:
            line(s, x + w + 4, y + h / 2, x + w + gap - 4, y + h / 2, GRAY, 4, head="end")


def fix_rows(s, y0, rows, rh=110, gap=30, left="困ったこと", right="直したこと", size=30):
    """左に困ったこと（灰）、右に直したこと（青）を矢印でつなぐ。"""
    textbox(s, 116, y0 - 50, 760, 40, [P(left, 26, True, GRAY)])
    textbox(s, 1000, y0 - 50, 792, 40, [P(right, 26, True, BLUE)])
    for i, (bad, fix) in enumerate(rows):
        y = y0 + i * (rh + gap)
        box(s, 116, y, 760, rh, fill=PALE_GRAY, line=RULE, radius=12, anchor=MSO_ANCHOR.MIDDLE,
            pad=(0, 28, 0, 28), paras=[P(bad, size, True, GRAY, spacing=1.25)])
        line(s, 896, y + rh / 2, 980, y + rh / 2, GRAY, 4, head="end")
        box(s, 1000, y, 792, rh, fill=PALE_BLUE, line=BLUE, line_w=2, radius=12, anchor=MSO_ANCHOR.MIDDLE,
            pad=(0, 28, 0, 28), paras=[P(fix, size, True, spacing=1.25)])


def pill(s, x, y, w, state):
    fill, edge, ink = {"済": (BLUE, None, "FFFFFF"), "一部済": (PALE_BLUE, BLUE, BLUE)}.get(
        state, ("FFFFFF", RULE, GRAY))
    box(s, x, y, w, 48, fill=fill, line=edge, line_w=2, radius=24, anchor=MSO_ANCHOR.MIDDLE,
        paras=[P(state, 24, True, ink, align=PP_ALIGN.CENTER)])


def m1_box(s, y, h, lines):
    box(s, 116, y, 760, h, fill=NAVY, radius=16, pad=(36, 40, 36, 40), paras=[
        P("大きな目標", 28, True, "BFD6EE", after=10),
        P("M1：計測系が回る", 48, True, "FFFFFF", after=16)] + lines)


# docs/milestones.md の内訳と同じもの（目安は発表に出さない）
STEPS = [("M1-1", "筋電を\nMVC で正規化", "10/1", "済"),
         ("M1-2", "伸展の MVC の\n取り方", "10/8", "済"),
         ("M1-3", "API で\n記録する", "10/15", "済"),
         ("M1-4", "計測を\n最後まで通す", "10/20", "済"),
         ("M1-5", "6 本・3 分の\n記録", "10/20", "済"),
         ("M1-6", "前腕の MVC が\n足りている", "10/29", "一部済"),
         ("M1-7", "残り 4 か所の\nMVC", "10/29", "未")]
THIS_WEEK = ("M1-4", "M1-5", "M1-6")

deck = Deck(SLIDES_DIR / "2026-10-15.pptx")

s = deck.slide(NOTES["cover"])
cover(s, "2026年10月22日")

# 1 マイルストーン
s = deck.slide(NOTES["roadmap"])
roadmap(s, 0, 1, steps=STEPS, this_week=THIS_WEEK)

# 2 今週の目標
s = deck.slide(NOTES["goal"])
title(s, "今週の目標", 2)
m1_box(s, 230, 500, [P("完了基準", 24, True, "BFD6EE", after=6),
                     P("6 か所の MVC と数分の記録を、API で、研究室に 1 回来るだけで取りきれる", 32, True, "FFFFFF",
                       spacing=1.35)])
line(s, 1012, 480, 896, 480, BLUE, 6, head="end")
textbox(s, 880, 420, 152, 40, [P("そのために", 24, True, BLUE, align=PP_ALIGN.CENTER)])
box(s, 1032, 230, 760, 500, fill=PALE_BLUE, line=BLUE, line_w=3, radius=16)
textbox(s, 1072, 262, 680, 40, [P("小さな目標（M1 の内訳から）", 28, True, BLUE)])
for i, (k, head, sub) in enumerate([("M1-4", "計測を最後まで通す", "準備から記録まで、コマンド 1 つで流す"),
                                    ("M1-5", "6 本・3 分の記録", "センサ 6 本を同時に、取りこぼしなく"),
                                    ("M1-6", "前腕の MVC", "手首の伸展・屈曲の MVC を一人で取る")]):
    y = 326 + i * 132
    if i:
        line(s, 1072, y - 12, 1752, y - 12, "BFD6EE", 1.5)
    textbox(s, 1072, y, 680, 120, [dict(runs=[(k + "　", 30, True, GRAY), (head, 36, True, INK)], after=6),
                                   P(sub, 26, color=GRAY)])
textbox(s, 116, 760, 1676, 80, [P("MVC：全力で力を入れたときの筋電。これを 100% として、ほかの記録を割合（%MVC）で表す",
                                  24, color=GRAY)])

# 3 やったこと
s = deck.slide(NOTES["done"])
title(s, "やったこと", 3)
bullets(s, 120, 220, 1672, 300, ["修論までのマイルストーンと、M1 の内訳を作った",
                                 "研究室での計測を、コマンド 1 つで流せるようにした",
                                 "センサ 6 本を、シールの番号 1〜6 で基地局に登録し直した",
                                 "研究室で一人で記録し（10-20）、MVC の取り方を決めた"], size=38, gap=8)
textbox(s, 116, 548, 1676, 40, [P("コマンド 1 つで流れる計測（記録中の窓に指示が出て、クリックで進む）", 26, True, GRAY)])
flow(s, 600, [("1", "センサの\n確認", False), ("2", "安静", False), ("3", "確認動作\n（自由に全力）", True),
              ("4", "MVC\n（押さえて全力）", True), ("5", "3 分の\n記録", False), ("6", "MVC を\n比べる", False)],
     w=250, gap=35, h=180, size=26)

# 4 M1-4
s = deck.slide(NOTES["m1_4"])
title(s, "M1-4：計測が最後まで止まらず通った", 4)
bullets(s, 120, 210, 1672, 80, ["センサの確認から 3 分の記録まで、11 ステップ・約 15 分"], size=38)
fix_rows(s, 370, [("指示の文字が、窓からあふれて読めない", "文字を折り返し、見出しと分けた"),
                  ("課題ごとの休憩 60 秒が長い", "課題を 1 周ずつ回し、休憩を 10 秒に"),
                  ("どの姿勢で力を入れるか、文字では分からない", "窓の左に姿勢の図を出した")],
         left="記録中の窓で困ったこと")
takeaway(s, "計測は通る。直した窓は来週、実機で確かめる", BLUE)

# 5 M1-5
s = deck.slide(NOTES["m1_5"])
title(s, "M1-5：6 本・3 分を取りこぼしなく記録", 5)
bullets(s, 120, 200, 1672, 80, ["3 分の記録で、6 本とも 3 分 × 2148 Hz とちょうど同じ数"], size=38)
textbox(s, 116, 290, 1100, 40, [P("部位の確認（包絡線の平均、μV）", 24, True, GRAY)])
box(s, 620, 298, 28, 20, fill=RULE)
textbox(s, 656, 290, 120, 40, [P("脱力", 22, color=GRAY)])
box(s, 760, 298, 28, 20, fill=BLUE)
textbox(s, 796, 290, 400, 40, [P("貼った部位を動かす", 22, color=GRAY)])
sites = [("S1", "前腕の上", 3.2, 16.4), ("S2", "前腕の下", 2.3, 19.6), ("S3", "三角筋", 2.0, 10.6),
         ("S4", "二頭筋", 2.0, 14.5), ("S5", "三頭筋", 6.4, 15.3), ("S6", "僧帽筋", 9.0, 66.6)]
x0, k, rh = 380, 11, 76  # 棒の始まり、1 μV あたりの px、行の高さ
for i, (sn, site, rest, move) in enumerate(sites):
    y = 340 + i * rh
    textbox(s, 116, y, 260, rh, [dict(runs=[(sn + " ", 26, True, GRAY), (site, 26, True, INK)])],
            anchor=MSO_ANCHOR.MIDDLE)
    box(s, x0, y + 12, max(rest * k, 4), 22, fill=RULE)
    box(s, x0, y + 38, move * k, 26, fill=BLUE)
    textbox(s, x0 + move * k + 12, y + 30, 160, 40, [P(f"{move:g}", 22, True, BLUE)])
line(s, x0, 336, x0, 340 + 6 * rh, GRAY, 1.5)
box(s, 1290, 340, 502, 150, fill=PALE_GRAY, radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(24, 28, 24, 28), paras=[
    P("3 分の記録", 24, True, GRAY, after=4), P("386,667 サンプル", 44, True, BLUE), P("6 本とも", 24, color=GRAY)])
box(s, 1290, 510, 502, 290, fill="FFFFFF", line=RULE, radius=12, pad=(24, 28, 24, 28), paras=[
    P("最初は 5 本だけ見つかった", 26, True, after=8),
    P("6 本目がこの基地局に登録されていなかった。シールの番号 1〜6 で登録し直した", 24, color=GRAY,
      spacing=1.35)])
takeaway(s, "6 本とも、貼った部位の動きでいちばん大きく反応した", BLUE)

# 6 M1-6
s = deck.slide(NOTES["m1_6"])
title(s, "M1-6：伸展は足りた。屈曲は取り直す", 6)
textbox(s, 116, 196, 1676, 50, [P("確認動作（誰も押さえず、自由に全力）が MVC の 100% 以下なら、MVC は全力を取れている",
                                  26, color=GRAY)])
k = 10  # 1 μV あたりの px
for c, (head, col, pale, txt, check, mvc, pct, note) in enumerate([
        ("伸展（一人：天板の裏を押し上げる）", BLUE, PALE_BLUE, NAVY, 32.8, 47.4, "69%", "全力を取れている"),
        ("屈曲（一人：机に押し下げる）", ORANGE, PALE_ORANGE, ORANGE_TXT, 5.4, 55.6, "10%",
         "確認動作で屈筋が動いていない")]):
    x = 116 + c * 856
    box(s, x, 250, 820, 300, fill=pale, radius=16)
    textbox(s, x + 32, 266, 760, 44, [P(head, 28, True, txt)])
    for j, (lab, v, f) in enumerate([("確認動作", check, "FFFFFF"), ("MVC（3 回の最大）", mvc, col)]):
        y = 314 + j * 74
        textbox(s, x + 32, y, 400, 30, [P(lab, 20, True, GRAY)])
        box(s, x + 32, y + 32, v * k, 34, fill=f, line=col, line_w=2)
        textbox(s, x + 44 + v * k, y + 32, 160, 34, [P(f"{v:g} μV", 22, True, txt)], anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, x + 32, 470, 760, 64, [dict(runs=[("確認動作 = MVC の ", 26, True, INK), (pct, 44, True, txt),
                                                  ("　" + note, 24, True, INK if c == 0 else ORANGE_TXT)])],
            anchor=MSO_ANCHOR.MIDDLE)
fix_rows(s, 640, [("画面の指示に手の向きも図もなく、手のひら下のまま曲げた可能性",
                   "指示を「手のひら上で、上に曲げきる」にし、姿勢の図を出した")],
         rh=140, left="屈曲の確認動作でうまくいかなかったこと", size=28)
takeaway(s, "屈曲は、直した指示で来週取り直す", ORANGE_TXT)

# 7 次やること
s = deck.slide(NOTES["next"])
title(s, "次やること", 7)
textbox(s, 116, 200, 1676, 44, [P("M1-7：残り 4 か所の MVC を、一人でできるやり方で試す", 32, True)])
cw, cg = 395, 32
for i, (task, head, sub) in enumerate([("shoulder_abduction_solo", "三角筋（肩）", "肘の外側で壁を横に押す"),
                                       ("elbow_flexion_solo", "二頭筋（上腕）", "肘 90°、天板の裏を持ち上げる"),
                                       ("elbow_extension_solo", "三頭筋（上腕）", "肘 90°、こぶしで机を押す"),
                                       ("shoulder_shrug_solo", "僧帽筋（首の付け根）", "座面の端を握り、肩をすくめる")]):
    x = 116 + i * (cw + cg)
    box(s, x, 264, cw, 420, fill="FFFFFF", line=RULE, radius=12)
    s.shapes.add_picture(str(render_pose(task)), px(x + 20), px(280), width=px(cw - 40))
    textbox(s, x + 20, 540, cw - 40, 130, [P(head, 30, True, after=6), P(sub, 24, color=GRAY, spacing=1.3)])
textbox(s, 116, 706, 1676, 40, [P("同じ日に", 26, True, GRAY)])
for i, text in enumerate(["M1-6：手首の屈曲を、直した指示で取り直す", "直した窓（図・休憩 10 秒）を実機で使う"]):
    box(s, 116 + i * 856, 756, 820, 80, fill=PALE_GRAY, radius=12, anchor=MSO_ANCHOR.MIDDLE,
        pad=(0, 28, 0, 28), paras=[P(text, 28, True)])

# 8 まとめ
s = deck.slide(NOTES["summary"])
title(s, "まとめ", 8)
m1_box(s, 230, 560, [P("済：API で、研究室に 1 回来るだけで、数分の記録まで取れる", 30, True, "FFFFFF",
                       spacing=1.35, after=14),
                     P("残り：肩・上腕など 4 か所の MVC、手首の屈曲の確かめ", 30, True, "BFD6EE", spacing=1.35)])
for i, (k_, head, sub, state) in enumerate([("M1-4", "計測を最後まで通す", "通った。窓は直し、実機は来週", "済"),
                                            ("M1-5", "6 本・3 分の記録", "取りこぼしなし", "済"),
                                            ("M1-6", "前腕の MVC", "伸展は 69%。屈曲は指示を直して取り直す", "一部済")]):
    y = 230 + i * 190
    box(s, 1032, y, 760, 170, fill=PALE_GRAY, radius=12)
    pill(s, 1062, y + 26, 128, state)
    textbox(s, 1214, y + 20, 560, 60, [dict(runs=[(k_ + "　", 28, True, GRAY), (head, 32, True, INK)])],
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 1062, y + 92, 700, 60, [P(sub, 28, color=INK)], anchor=MSO_ANCHOR.MIDDLE)
takeaway(s, "来週：手首の屈曲の取り直し（M1-6）と、残り 4 か所の MVC（M1-7）")

# 9 予備：10-20 の数値
s = deck.slide(NOTES["records"])
title(s, "予備：10-20 の数値", 9)
cols = [(116, 700, "記録"), (840, 470, "前腕の上（S1、伸筋側）"), (1330, 462, "前腕の下（S2、屈筋側）")]
y0, rh = 280, 110
for x, w, head in cols:
    textbox(s, x, y0 - 50, w, 40, [P(head, 24, True, BLUE if "S1" in head else ORANGE_TXT if "S2" in head else GRAY)])
rows = [("確認動作・伸展", "32.8", "6.0"), ("確認動作・屈曲（手のひら下）", "27.8", "5.4"),
        ("伸展（天板の裏を押し上げる）× 3", "44.1・47.4・46.3", "22.2・5.8・5.0"),
        ("屈曲（机に押し下げる）× 3", "6.3・7.1・5.8", "48.6・44.7・55.6")]
for i, row in enumerate(rows):
    y = y0 + i * rh
    line(s, 116, y, 1792, y, "DDDDDD", 1.5)
    for (x, w, _), v in zip(cols, row):
        textbox(s, x, y, w - 12, rh, [P(v, 30, x == 116)], anchor=MSO_ANCHOR.MIDDLE)
line(s, 116, y0 + len(rows) * rh, 1792, y0 + len(rows) * rh, "DDDDDD", 1.5)
textbox(s, 116, 760, 1676, 80, [P("包絡線の 0.5 秒移動平均の最大（μV）。前腕以外（S3〜S6）の MVC は値を使わない", 22, color=GRAY),
                                P("data/raw/2026-10-20/（Git 管理外）", 22, color=GRAY)])

deck.save(SLIDES_DIR / "2026-10-22.pptx")
