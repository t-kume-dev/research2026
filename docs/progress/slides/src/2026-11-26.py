"""2026-11-26 の進捗報告スライドを作る。

    python docs/progress/slides/src/2026-11-26.py

docs/progress/slides/2026-11-26.pptx に書き出す。次の週は、このファイルをコピーして
中身（NOTES と各スライド）を差し替える。
"""
from pptx_kit import *  # noqa: F401,F403

NOTES = {
    "cover": """\n今週は、筋電とマウスを 1 つのコマンドで同時に記録できるようにしました。画面録画も一緒に取り、1 回の来室を 1 つのコマンドで流せる形まで作りました。

流れは、マイルストーン → 目標 → やったこと → わかったこと → 次やること → まとめ、の順で話します。
""",
    "tracker": """\n今月のトラッカーです。今週は M2-2「筋電とマウスを同時に記録」を進め、M2-3「1 回の来室の流れ」も 1 つのコマンドで流す形まで先に作りました。
""",
    "goal": """\n大きな目標は、今のマイルストーンの M2「毎回取れる形になる」です。研究室に 1 回来て、MVC から KovaaK's を 5 回遊ぶまで、筋電・マウス・スコアを同時に記録して止まらずに通ることです。

小さな目標は、その内訳の 2 つ目、M2-2「筋電とマウスを同時に記録」です。先週作ったマウスの記録と、これまでの筋電の記録を、1 つのコマンドで同時に取れるようにします。KovaaK's の結果も取り込みます。
""",
    "done": """\nやったことです。

1 つのコマンドで、筋電とマウスを同時に記録できるようにしました。マウスは裏で取りながら、筋電を取ります。どちらも同じ時計で開始時刻を残すので、マウスの時刻を筋電の時刻にそろえられます。KovaaK's の結果は、先週と同じく記録のあとに自動で取り込みます。

画面録画も一緒に取れるようにしました。録画ソフトの OBS を外から始め・止めて、録画のファイルも記録と同じ名前で同じフォルダに置きます。あとでプレイの様子を見返せるようにするためです。

1 回の記録が終わると、同じ名前で、筋電・マウス・録画・ゲームの結果と、筋電とマウスを並べた図がそろいます。

【確かめた範囲】筋電は疑似信号（実機と同じ形のデータを作るもの）、録画ソフトは代わりの偽物で確かめました。実機をつないだ確認は次の来室で行います。
""",
    "clock": """\nM2-2 への答えです。1 つのコマンドで、筋電とマウスを同じ時計で取れるようになりました。

筋電・マウス・録画の開始時刻を、PC の同じ時計で残します。そこで、筋電の開始を 0 秒として、マウスと録画の時刻をそのずれの分だけ動かせば、すべて筋電の時刻に直せます。始める順番は、録画 → マウス → 筋電で、止めるのはその逆です。筋電を取っている間は、マウスと録画が必ず動いているようにするためです。

ゲームの結果は PC の時計（何時何分何秒）で残るので、先週と同じく、マウスの開始時の PC の時計で合わせます。先週、倒した時刻と直前のクリックが 5 ms 以内でそろうことを確かめています。

今までは筋電の記録に開始時刻を残していなかったので、残すようにしました。

【まだ確かめていないずれ】筋電の開始時刻は記録を始めた直後の値で、センサから PC に届くまでの遅れは入っていません。録画の開始時刻も、OBS が録画中になったと分かった瞬間で、最初のフレームとは数十 ms ずれうると思っています。どちらも実機で、強くクリックしたときの筋電の立ち上がりと、クリックの時刻を比べて確かめます。
""",
    "visit": """\n1 回の来室も、1 つのコマンドで流せるようにしました。M2-3「1 回の来室の流れ」の前半にあたります。

前半はこれまでの研究室の手順そのままで、信号の確認、センサの部位の確認、安静、確認動作、MVC の順に進みます。続けて KovaaK's を 5 回遊びます。1 回ごとに Enter を押すと記録が始まり、終わると筋電・マウス・録画・ゲームの結果がそろいます。

途中で止まったときは、KovaaK's のところから再開できます。

KovaaK's を続けて遊ぶ部分は、Enter → 記録 → 保存が 2 回続けて止まらずに流れることを確かめました。回ごとのスコアと %MVC の一覧を出すところは、まだです。
""",
    "pc": """\n計測をどの PC でやるかも決めました。研究室のデスクトップ 1 台に、筋電・マウス・KovaaK's・録画をまとめます。

理由は 2 つです。1 つ目は、マウスの記録は、マウスをつないでゲームを動かしている PC でしか取れないことです。2 つ目は、筋電も同じ PC で取れば、同じ時計で時刻を合わせられることです。2 台に分けると PC 同士の時計が数十 ms ずれることがあり、別に合わせる仕組みが要ります。

今のノート PC は、ゲームと録画を同時に回すには重いので、デスクトップを使います。

【移すもの】Python とコード、筋電の機器を使うためのライセンスとライブラリ、機器のドライバ、KovaaK's、OBS です。
""",
    "next": """\n次やることです。

研究室のデスクトップで、MVC から KovaaK's までの一通りの流れを、実機で確かめます。筋電とクリックの時刻がそろっているか、録画と筋電の時刻のずれも、ここで見ます。

そのまま、1 回の来室のデータ、KovaaK's 5 回ぶんを取ります。

取ったデータで、回ごとのスコアと 6 か所の %MVC の一覧を出します。これが M2-3「1 回の来室の流れ」の残りです。
""",
    "summary": """\nまとめです。

大きな目標の M2「毎回取れる形になる」は、内訳 4 つのうち 1 つ目が済み、2 つ目と 3 つ目は 1 つのコマンドで流す形までできました。次は実機で通して、データを取ります。

小さな目標の M2-2「筋電とマウスを同時に記録」は、1 つのコマンドで、筋電・マウス・録画・ゲームの結果を、筋電の時刻にそろえて取れるようになりました。実機での確認は次に行います。
""",
}


def m2_box(s, y, h, lines):
    box(s, 116, y, 760, h, fill=NAVY, radius=16, pad=(36, 40, 36, 40), paras=[
        P("大きな目標", 28, True, "BFD6EE", after=10),
        P("M2：毎回取れる形になる", 46, True, "FFFFFF", after=16)] + lines)


def chip(s, x, y, w, h, head, sub, hot=True):
    box(s, x, y, w, h, fill=PALE_BLUE if hot else PALE_GRAY, line=BLUE if hot else RULE, radius=12,
        anchor=MSO_ANCHOR.MIDDLE, pad=(8, 20, 8, 20), paras=[
            P(head, 28, True, INK, align=PP_ALIGN.CENTER, after=4),
            P(sub, 20, color=GRAY, align=PP_ALIGN.CENTER, spacing=1.25)])


deck = Deck(SLIDES_DIR / "2026-11-19.pptx")

s = deck.slide(NOTES["cover"])
cover(s, "2026年11月26日")

# 1 今月のトラッカー（番号なし）
s = deck.slide(NOTES["tracker"])
tracker_page(s, "2026-11-26")

# 2 今週の目標
s = deck.slide(NOTES["goal"])
title(s, "今週の目標", 2)
m2_box(s, 230, 500, [P("完了基準", 24, True, "BFD6EE", after=6),
                     P("研究室に 1 回来て、MVC から KovaaK's 5 回まで、筋電・マウス・スコアを同時に記録して止まらずに通る",
                       30, True, "FFFFFF", spacing=1.35)])
line(s, 1012, 480, 896, 480, BLUE, 6, head="end")
textbox(s, 880, 420, 152, 40, [P("そのために", 24, True, BLUE, align=PP_ALIGN.CENTER)])
box(s, 1032, 230, 760, 500, fill=PALE_BLUE, line=BLUE, line_w=3, radius=16)
textbox(s, 1072, 262, 680, 40, [P("小さな目標（M2 の内訳から）", 28, True, BLUE)])
textbox(s, 1072, 340, 680, 360, [dict(runs=[("M2-2　", 30, True, GRAY), ("筋電とマウスを同時に記録", 36, True, INK)], after=16),
                                 P("1 つのコマンドで筋電とマウスを同時に取り、KovaaK's の結果も取り込む", 28, color=INK, spacing=1.4)])

# 3 やったこと：1 コマンド → 4 つがそろう
s = deck.slide(NOTES["done"])
title(s, "やったこと", 3)
bullets(s, 120, 196, 1672, 130, ["筋電とマウスを、1 つのコマンドで同時に記録できるようにした",
                                 "画面録画（OBS）も一緒に始め・止めるようにした"], size=32, gap=2)
box(s, 116, 420, 420, 260, fill=NAVY, radius=16, anchor=MSO_ANCHOR.MIDDLE, pad=(20, 24, 20, 24), paras=[
    P("1 つのコマンド", 36, True, "FFFFFF", align=PP_ALIGN.CENTER, after=8),
    P("1 回ぶんの記録", 24, color="BFD6EE", align=PP_ALIGN.CENTER)])
outs = [("筋電", "6 か所の筋肉の信号"), ("マウス", "動きとクリック"), ("画面録画", "プレイの様子"),
        ("ゲームの結果", "倒した時刻・スコア")]
for i, (head, sub) in enumerate(outs):
    y = 350 + i * 108
    chip(s, 700, y, 520, 92, head, sub)
    line(s, 540, 550, 696, y + 46, GRAY, 3, head="end")
line(s, 1224, 550, 1340, 550, GRAY, 4, head="end")
box(s, 1344, 420, 448, 260, fill=PALE_GRAY, line=RULE, radius=16, anchor=MSO_ANCHOR.MIDDLE, pad=(20, 24, 20, 24), paras=[
    P("同じ名前で、同じフォルダに", 28, True, align=PP_ALIGN.CENTER, after=10),
    P("筋電とマウスを並べた図もできる", 22, color=GRAY, align=PP_ALIGN.CENTER, spacing=1.3)])
takeaway(s, "1 回遊ぶと、筋電・マウス・録画・ゲームの結果がそろう", BLUE)

# 4 わかったこと：同じ時計でそろえる
s = deck.slide(NOTES["clock"])
title(s, "3 つの記録を同じ時計でそろえる", 4)
x0, x1, t0x = 380, 1760, 700          # 時間軸の左端・右端・筋電の開始（0 秒）
rows = [("画面録画", 520, "1 番目に始める"), ("マウス", 610, "2 番目"), ("筋電", t0x, "最後に始める（ここを 0 秒）")]
for i, (name, start, note) in enumerate(rows):
    y = 230 + i * 125
    textbox(s, 116, y, 240, 70, [P(name, 30, True)], anchor=MSO_ANCHOR.MIDDLE)
    line(s, x0, y + 35, x1, y + 35, RULE, 2)
    box(s, start, y + 10, x1 - 20 - i * 20 - start, 50, fill=BLUE if name == "筋電" else PALE_BLUE,
        line=None if name == "筋電" else BLUE, radius=8)
    textbox(s, start + 16, y + 10, 600, 50, [P(note, 20, True, "FFFFFF" if name == "筋電" else BLUE)],
            anchor=MSO_ANCHOR.MIDDLE)
line(s, t0x, 230, t0x, 640, ORANGE_TXT, 3, dash=True)
textbox(s, t0x - 120, 640, 240, 40, [P("筋電の開始 = 0 秒", 22, True, ORANGE_TXT, align=PP_ALIGN.CENTER)])
bullets(s, 120, 700, 1672, 110, ["どれも開始時刻を PC の同じ時計で残し、そのずれの分だけ動かして筋電の時刻に直す",
                                 "ゲームの結果は、先週どおり PC の時計で合わせる（倒した時刻とクリックが 5 ms 以内）"], size=26, gap=2)
takeaway(s, "マウス・録画・ゲームの結果を、すべて筋電の時刻で並べられる", BLUE)

# 5 1 回の来室を 1 コマンドで
s = deck.slide(NOTES["visit"])
title(s, "1 回の来室を 1 つのコマンドで流せる", 5)
steps5 = [("信号の確認", False), ("部位の確認", False), ("安静", False), ("確認動作", False), ("MVC", False),
          ("KovaaK's\n× 5 回", True)]
w, gap, y = 236, 52, 300
for i, (lab, hot) in enumerate(steps5):
    x = 116 + i * (w + gap)
    box(s, x, y, w, 170, fill=PALE_BLUE if hot else PALE_GRAY, line=BLUE if hot else RULE, line_w=3 if hot else 2,
        radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(8, 12, 8, 12),
        paras=[P(lab, 28, True, align=PP_ALIGN.CENTER, spacing=1.2)])
    if i < len(steps5) - 1:
        line(s, x + w + 4, y + 85, x + w + gap - 4, y + 85, GRAY, 4, head="end")
textbox(s, 116, 220, 1400, 50, [P("これまでの研究室の手順", 24, True, GRAY)])
line(s, 116, 270, 116 + 5 * (w + gap) - gap, 270, RULE, 2)
textbox(s, 116 + 5 * (w + gap), 220, w, 50, [P("今週足した", 24, True, BLUE, align=PP_ALIGN.CENTER)])
box(s, 116, 540, 1676, 150, fill="FFFFFF", line=RULE, radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(16, 32, 16, 32), paras=[
    P("KovaaK's は 1 回ごとに Enter で記録が始まり、終わると筋電・マウス・録画・ゲームの結果がそろう", 26, True, after=8),
    P("途中で止まったときは、KovaaK's から再開できる", 24, color=GRAY)])
takeaway(s, "回ごとのスコアと %MVC の一覧を出すところは、まだ", ORANGE_TXT)

# 6 計測は 1 台の PC で
s = deck.slide(NOTES["pc"])
title(s, "計測はデスクトップ 1 台にまとめる", 6)
box(s, 116, 220, 820, 470, fill=PALE_BLUE, line=BLUE, line_w=3, radius=16)
textbox(s, 156, 248, 740, 50, [P("研究室のデスクトップ", 32, True, BLUE)])
for i, (head, sub) in enumerate([("筋電", "センサの受信機"), ("マウス", "ゲームと同じ PC"),
                                 ("KovaaK's", "エイム練習ソフト"), ("画面録画", "OBS")]):
    chip(s, 156 + (i % 2) * 370, 330 + (i // 2) * 170, 340, 140, head, sub, hot=False)
textbox(s, 1000, 230, 792, 460, [
    P("理由", 28, True, GRAY, after=12),
    P("・マウスの記録は、ゲームを動かしている PC でしか取れない", 28, spacing=1.35, after=14),
    P("・同じ PC なら、筋電と同じ時計で時刻を合わせられる", 28, spacing=1.35, after=14),
    P("・2 台に分けると、PC 同士の時計が数十 ms ずれうる", 28, color=GRAY, spacing=1.35, after=14),
    P("・今のノート PC は、ゲームと録画を同時に回すには重い", 28, color=GRAY, spacing=1.35)])
takeaway(s, "1 台にまとめれば、時刻を合わせる仕組みを足さずに済む", BLUE)

# 7 次やること
s = deck.slide(NOTES["next"])
title(s, "次やること", 7)
for i, (k, head, sub) in enumerate([
        ("1", "実機で一通り流す", "研究室のデスクトップで、MVC から KovaaK's まで。筋電とクリック・録画の時刻のずれも見る"),
        ("2", "データを取る", "そのまま 1 回の来室ぶん（KovaaK's 5 回）を取る"),
        ("3", "一覧を出す", "回ごとのスコアと 6 か所の %MVC を並べる（M2-3 の残り）")]):
    x = 116 + i * 572
    box(s, x, 210, 532, 440, fill=PALE_BLUE if i == 0 else PALE_GRAY, line=BLUE if i == 0 else None, line_w=2,
        radius=12, pad=(28, 28, 28, 28), paras=[
            P(k, 24, True, BLUE if i == 0 else GRAY, after=6), P(head, 32, True, after=18),
            P(sub, 26, color=INK, spacing=1.4)])
    if i < 2:
        line(s, x + 536, 430, x + 568, 430, GRAY, 4, head="end")
box(s, 116, 680, 1676, 110, fill="FFFFFF", line=RULE, radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(0, 32, 0, 32), paras=[
    P("そのあと：M2-4「最初の本番」で、プレイ中に 6 か所とも 100 %MVC を超えないか、センサが邪魔にならないかを見る", 26, True)])

# 8 まとめ
s = deck.slide(NOTES["summary"])
title(s, "まとめ", 8)
m2_box(s, 230, 560, [P("済：マウスとゲームの記録", 30, True, "FFFFFF", spacing=1.35, after=10),
                     P("今週：筋電とマウスの同時記録、1 回の来室を 1 つのコマンドで流す形", 30, True, "FFFFFF", spacing=1.35, after=14),
                     P("次：実機で通して、データを取る", 30, True, "BFD6EE", spacing=1.35)])
box(s, 1032, 230, 760, 560, fill=PALE_GRAY, radius=12)
textbox(s, 1062, 254, 700, 60, [dict(runs=[("M2-2　", 28, True, GRAY), ("筋電とマウスを同時に記録", 32, True, INK)])],
        anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 1062, 350, 700, 420, [P("・1 つのコマンドで、筋電・マウス・録画・ゲームの結果を取れる", 28, spacing=1.35, after=14),
                                 P("・すべて筋電の時刻にそろえて並べられる", 28, spacing=1.35, after=14),
                                 P("・実機での確認は次に行う", 28, color=GRAY, spacing=1.35)])
takeaway(s, "次は、研究室のデスクトップで実機を通し、データを取る")

deck.save(SLIDES_DIR / "2026-11-26.pptx")
