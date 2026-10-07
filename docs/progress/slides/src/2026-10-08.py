"""2026-10-08 の進捗報告スライドを作る。

    python docs/progress/slides/src/2026-10-08.py

docs/progress/slides/2026-10-08.pptx に書き出す。次の週は、このファイルをコピーして
中身（NOTES と各スライド）を差し替える。
"""
from pptx_kit import *  # noqa: F401,F403

NOTES = {
    "cover": """\n今週は、前回うまくいかなかった伸展の MVC の取り方を決めました。文献で取り方を調べ、研究室で候補を同じ日に試しました。結論から言うと、伸展は「腕を机に乗せ、他の人に上から押さえてもらう」やり方で足りました。屈曲はまだ足りていません。

流れは、目標 → やったこと → わかったこと → 次やること → まとめ、の順で話します。
""",
    "goal": """\n大きな目標は先週と同じで、EMG でデータを取り、実際に違いが出ているデータを確認することです。

そのための小さな目標が、伸展の MVC を全力で取れる方法を決めることです。MVC は最大随意収縮、その筋で出せる全力のときの筋活動で、%MVC を出すときの分母になります。

前回（09-29）は、机に固定した手を自分の反対の手で押さえて反らす方法で伸展の MVC を取りました。ところがデモで手首を自由に反らしきっただけで、伸筋側が約 350 %MVC になりました。分母の MVC が小さすぎると %MVC が 100% を超え、日をまたいだ比較の土台になりません。なので、本番データを取る前に MVC の取り方を固めます。
""",
    "done": """\n2 つやりました。

1 つ目は文献です。手持ちの 13 本を読み、MVC の手順が書いてあるかを確認しました。手順を別の論文に任せていたものは、引用をたどって元の手順まで読みました（Forman 2020 の 2 本、Forman 2019、Holmes 2022）。まとめは literature/notes/MVC_protocols.md にあります。

2 つ目は研究室での比較です。10-06 に、前腕 2 か所（伸筋側・屈筋側）にセンサを付け、手伝ってくれる人 1 人と記録しました。9 つの課題を 1 回ずつ（前回のやり方 A だけ 2 回）と、確認動作（手首を自由に反らしきる・曲げきる）を 1 回ずつ取りました。比べるのは mvc-compare というコマンドで、確認動作がそれぞれの課題の MVC の何 % になるかを出します。
""",
    "tasks": """\n10-06 に試した動作の一覧です。

最初に確認動作を取りました。誰も押さえずに、手首を反らしきる・曲げきる動きで、疲れる前の最大を見るためのものです。

伸展は 8 つです。A は前回までのやり方で、自分の反対の手で押さえます。B〜G は手伝う人に抵抗をかけてもらうやり方で、文献の課題（Forman 2019、Lacelle 2025）から選びました。前腕の向き（手のひら下・親指が上）、握るか開くか、小指側・親指側にも押すかを変えています。H は一人でできる方法で、机の天板の裏を押し上げます。

屈曲は 2 つで、どちらも手のひら上です。I は握って曲げる、J は手伝う人の指を握りながら曲げます。

試行は 1 回ずつ（A だけ 2 回）です。D 以降は腕を机から浮かせて取りました。H は CSV を書き出しそこねたので、結果がありません。
""",
    "lit": """\n文献から言えることは 2 つです。

1 つ目、抵抗はどの文献も実験者がかけています。前回の「自分の反対の手で押さえる」やり方はどこにもありませんでした。力センサで測る Forman 2020 も、使わない手は机の上に置かせていて、押さえるのには使わせていません。

2 つ目、伸筋は伸展だけでなく、筋ごとに課題を分けています。握って伸展、伸展＋尺屈（小指側）、手を全力で開きながら伸展、などです。前腕の向きは文献で違い、Forman は親指が上、Lacelle は手のひら下です。また Lacelle は、ほかの全力課題のほうが EMG が大きければそちらで正規化していて、全課題の最大を MVC にする今のコードと同じ考え方です。

【13 本の内訳（聞かれたら）】
・筋ごとの手順まで書いてあった：Lacelle 2025。もう 1 本は、たどって行き着いた Forman 2019
・手順を別の論文に任せている：Forman 2025 の 2 本と Forman 2023（博論）。たどると Forman 2019 の表に行き着く。Forman 2019 は有料だが、著者の博論（2020、Ontario Tech、公開）の 3 章が同じ論文で、表 3.1 に同じ表がある
・Wang 2023：「解剖ガイド（Perotto 2011）に従った」とだけ書いている
・MVC を使っていない 8 本：Park 2021、Prajapati 2024、Kuikkaniemi 2010（別の正規化）、Okinaka & Wada 2023、Jeong 2024（RMS や周波数のみ）、Donovan 2022、Dupuy 2024、Dupuy 2025（EMG を測っていない）
""",
    "method": """\n比べ方です。

確認動作は、誰も押さえずに手首を自由に反らしきる（曲げきる）動きで、09-29 のデモで 350% になったのと同じ動きです。これを記録の最初、疲れる前に取りました。

各課題の MVC で確認動作のピークを割ります。100% 以下なら、その課題で確認動作より大きい力が出せている、つまり全力を出し切れているということです。100% を超えたら、その課題では足りません。

MVC は、包絡線（筋電の大きさを表す線）の 0.5 秒移動平均の最大です。
""",
    "ext": """\n小さな目標への答えです。

手のひら下・握って、腕を机に乗せ、他の人に手の甲を上から押さえてもらうやり方（B）で、確認動作が 56 %MVC に収まりました。前回は 350% だったので、十分な余裕があります。

この結論は疲れがあっても変わりません。確認動作は最初に、疲れる前に取っています。疲れると全力の EMG は小さく出るので、もし B に疲れが入っていたとしても、本当の B の MVC はもっと大きく、%MVC はもっと小さくなるだけです。

前回までのやり方（A、自分の反対の手で押さえる）も、今回は 96 %MVC でぎりぎり 100% を下回りました。09-29 は同じやり方で約 350% だったので、日によって大きく違います。理由は今のデータでは決められません。考察の余地として、センサの位置が日によって安定していない（10-06 は記録中にセンサの上下がわからなくなった）、押さえ方が違った、確認動作の反らし方が違った、などが考えられます。どちらにしても、余裕のある B を使います。

【10-06 の数値（伸筋側、包絡線、mV）】
・B ext_fist_pron　MVC 0.154　確認動作 56%
・A ext_self　　　 MVC 0.090　確認動作 96%
・F ext_radial_pron MVC 0.080　確認動作 108%
・E ext_open_neut　MVC 0.066　確認動作 132%
・G ext_open_pron　MVC 0.054　確認動作 160%
・C ext_fist_neut　MVC 0.051　確認動作 169%
・D ext_ulnar_neut　MVC 0.044　確認動作 198%
ほかの課題との差は、次のページのとおり疲れと分けられないので、課題の良し悪しとしては見ません。
""",
    "short": """\nうまくいかなかったことです。

屈曲は足りませんでした。手首を曲げきる確認動作が、屈曲で一番大きい課題（J、相手の手を握って屈曲）の 416 %MVC になりました。I・J は手のひら上で、腕を机から浮かせて取っています。

課題を、休みを十分とらずに続けて取ったので、疲れを考えに入れそこねました。後に取った課題ほど疲れて小さく出た可能性があり、「ほかの伸展の課題は B の 28〜59%」「A は B の 59%（他の人に押さえてもらうと約 2 倍）」は、課題の差とは言い切れません。疲れを確かめるはずだった B の 3 回目と最後の確認動作も取りそこねました。

D 以降の課題は腕を机から浮かせて取りました。浮かせる取り方はうまくいかなそうなので、次からは腕を机に乗せます。

ほかに、一人でやる方法（H、机の天板の裏を押し上げる）は取ったものの CSV を書き出しそこね、比べられませんでした。試行は 1 回ずつ（A だけ 2 回）なので、ばらつきも見られていません。

【センサの上下】記録中にどちらが伸筋側かわからなくなりました。伸展の 7 試行すべてで、センサ 0 が 40〜140 μV、センサ 3 は安静と同じ 3〜5 μV だったので、センサ 0 を伸筋側としました（09-29 とは逆）。
""",
    "next": """\nMVC の取り方を次の 2 つにします。どちらも腕は机に乗せます。
・伸展：手のひら下・握って、上から押さえてもらう（B）
・屈曲：机に向かって押し下げる

屈曲の新しいやり方はまだ試していないので、次回の記録で確かめます。順番は、確認動作を最初に取り、B と一人用（H）を 2 回ずつ、屈曲、最後に確認動作と B をもう 1 回です。最後の B が最初より小さければ疲れていたとわかります。課題のあいだは十分休みます。

伸展・屈曲とも、確認動作が 100 %MVC 以下に収まれば決定として、calibration.py の DEFAULT_TASKS に入れます。

記録の前に、センサ番号と貼った位置を sensors.json に書き、反らしてどちらが伸筋側か確かめます。今回センサの上下がわからなくなったのを防ぐためです。
""",
    "summary": """\nまとめです。

大きな目標は、前腕 2 か所で新しいデータを取りました。6 か所の本番データは、MVC の取り方を確かめてから取ります。

小さな目標は、伸展の MVC は B（腕を机に乗せ、上から押さえてもらう）に決まりました。屈曲は「机に向かって押し下げる」に決めましたが、足りるかは次回確かめます。一人で取れるかも残っています。

来週は、伸展・屈曲の MVC を確かめて、6 か所で本番データを取ります。
""",
}


def goal_boxes(s, y):
    box(s, 116, y, 740, 250, fill=NAVY, radius=16, pad=(36, 40, 36, 40), paras=[
        P("大きな目標", 30, True, "BFD6EE", after=12),
        P("EMG で、違いが出ている\nデータを確認する", 44, True, "FFFFFF", spacing=1.3)])
    line(s, 1012, y + 130, 876, y + 130, BLUE, 6, head="end")
    box(s, 1032, y, 760, 250, fill=PALE_BLUE, line=BLUE, line_w=3, radius=16, pad=(36, 40, 36, 40), paras=[
        P("小さな目標", 30, True, BLUE, after=12),
        P("伸展の MVC を全力で\n取れる方法を決める", 44, True, spacing=1.3)])


def flow(s, y, steps, w=340, gap=72, h=200, x0=116):
    """左から右へ箱を並べ、矢印でつなぐ。steps は (ラベル, 本文, 強調するか)。"""
    for i, (lab, body, hot) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(s, x, y, w, h, fill=PALE_BLUE if hot else PALE_GRAY, line=BLUE if hot else RULE,
            radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(24, 24, 24, 24), paras=[
                P(lab, 26, True, BLUE if hot else GRAY, after=8), P(body, 32, True, spacing=1.3)])
        if i < len(steps) - 1:
            line(s, x + w + 4, y + h / 2, x + w + gap - 4, y + h / 2, GRAY, 4, head="end")


def pct_bars(s, rows, y0, rh, scale, x0=700, color=BLUE):
    """%MVC の横棒と 100% の点線。rows は (ラベル, 補足, 値, 濃い色か)。"""
    for i, (lab, sub, v, hot) in enumerate(rows):
        y = y0 + i * rh
        textbox(s, 116, y, 560, rh, [P(lab, 34, True), P(sub, 24, color=GRAY)], anchor=MSO_ANCHOR.MIDDLE)
        w = v * scale
        box(s, x0, y + rh / 2 - 30, w, 60, fill=color if hot else "9DB8D3" if color == BLUE else "F2C39A",
            radius=4)
        textbox(s, x0 + w + 16, y, 300, rh, [P(f"{v} %", 34, True)], anchor=MSO_ANCHOR.MIDDLE)
    x100 = x0 + 100 * scale
    line(s, x100, y0 - 20, x100, y0 + len(rows) * rh + 4, INK, 3, dash=True)
    textbox(s, x100 - 100, y0 - 64, 200, 40, [P("100 %", 26, True, align=PP_ALIGN.CENTER)])


def task_card(s, x, y, w, h, key, pose, act, col, pale, hot=False, floated=False, note=None):
    box(s, x, y, w, h, fill=pale if hot else "FFFFFF", line=col if hot else RULE, line_w=4 if hot else 2,
        radius=10, pad=(12, 10, 12, 12), paras=[
            P(key, 30, True, col, after=2), P(pose, 21, color=GRAY, after=4), P(act, 22, True, spacing=1.2)])
    tags = [t for t in ("腕を浮かせた" if floated else None, note) if t]
    for i, t in enumerate(tags):
        textbox(s, x + 12, y + h - 34 - 28 * (len(tags) - 1 - i), w - 22, 28, [P(t, 19, color=GRAY)])


deck = Deck(SLIDES_DIR / "2026-10-01.pptx")

s = deck.slide(NOTES["cover"])
cover(s, "2026年10月8日")

# 1 今週の目標
s = deck.slide(NOTES["goal"])
title(s, "今週の目標", 1)
goal_boxes(s, 270)
textbox(s, 868, 318, 152, 40, [P("そのために", 26, True, BLUE, align=PP_ALIGN.CENTER)])
bullets(s, 120, 620, 1672, 200, ["前回：手首を反らしきると約 350 %MVC　→　MVC が小さすぎた",
                                 "本番データの前に、MVC の取り方を固める"], gap=24)

# 2 やったこと
s = deck.slide(NOTES["done"])
title(s, "やったこと", 2)
bullets(s, 120, 250, 1672, 170, ["MVC の取り方を文献で調べた",
                                 "候補の取り方を、研究室で同じ日に試した（10-06）"])
flow(s, 500, [("① 文献", "13 本を読み\n手順をたどる", True), ("② 研究室で試す", "9 課題 ＋\n確認動作", True),
              ("③ 比べる", "確認動作は\nMVC の何 %", False)], w=500, gap=88)

# 3 文献でわかったこと
s = deck.slide(NOTES["lit"])
title(s, "文献でわかったこと", 3)
bullets(s, 120, 250, 1672, 170, ["抵抗は、どの文献も実験者がかけている",
                                 "伸筋は、筋ごとに課題を分けている（握る・開く・小指側）"], gap=16)
rows = [("筋ごとの手順あり", "Lacelle 2025", True),
        ("別の論文に任せる", "Forman 2025 ×2・博論　→　たどると Forman 2019 の表", True),
        ("一言だけ", "Wang 2023（解剖ガイドに従った）", False),
        ("MVC を使っていない", "8 本", False)]
y0, rh = 470, 80
for i, (lab, body, hot) in enumerate(rows):
    y = y0 + i * rh
    line(s, 116, y, 1792, y, "DDDDDD", 1.5)
    textbox(s, 116, y, 460, rh, [P(lab, 32, True, INK if hot else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 600, y, 1192, rh, [P(body, 32, color=INK if hot else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
line(s, 116, y0 + 4 * rh, 1792, y0 + 4 * rh, "DDDDDD", 1.5)
takeaway(s, "自分の手で押さえるやり方は、どの文献にもない", ORANGE_TXT)

# 4 試した動作
s = deck.slide(NOTES["tasks"])
title(s, "試した動作（10-06）", 4)
bullets(s, 120, 220, 1672, 70, ["伸展 8 つ・屈曲 2 つを 1 回ずつ（A だけ 2 回）。最初に確認動作"], size=40)
cw, gap = 195, 16
textbox(s, 116, 310, 1676, 40, [P("確認動作（誰も押さえない・最初に取った）", 26, True, GRAY)])
for i, (k, act, col) in enumerate([("伸展", "手首を反らしきる", BLUE), ("屈曲", "手首を曲げきる", ORANGE_TXT)]):
    box(s, 116 + i * (4 * cw + 4 * gap), 352, 4 * cw + 3 * gap, 64, line=RULE, radius=10,
        anchor=MSO_ANCHOR.MIDDLE, pad=(0, 16, 0, 16), paras=[dict(runs=[
            (k + "　", 26, True, col), (act, 26, True, INK)])])
textbox(s, 116, 436, 600, 40, [P("伸展", 26, True, BLUE)])
ext = [("A", "手のひら下", "自分の手で\n押さえる", False, None),
       ("B", "手のひら下", "握って上から\n押さえて\nもらう", False, None),
       ("C", "親指が上", "握って\n手の甲側へ", False, None),
       ("D", "親指が上", "握って\n＋小指側", True, None),
       ("E", "親指が上", "手を開き\nながら反らす", True, None),
       ("F", "手のひら下", "握って\n＋親指側", True, None),
       ("G", "手のひら下", "指を伸ばして\n反らす", True, None),
       ("H", "手のひら下", "一人で天板の\n裏を押す", True, "CSV なし")]
for i, (k, pose, act, fl, note) in enumerate(ext):
    task_card(s, 116 + i * (cw + gap), 478, cw, 250, k, pose, act, BLUE, PALE_BLUE, hot=k == "B",
              floated=fl, note=note)
textbox(s, 116, 748, 600, 40, [P("屈曲", 26, True, ORANGE_TXT)])
flex = [("I", "手のひら上", "握って曲げる"), ("J", "手のひら上", "相手の指を握って曲げる")]
for i, (k, pose, act) in enumerate(flex):
    task_card(s, 116 + i * (2 * cw + 2 * gap), 790, 2 * cw + gap, 170, k, pose, act, ORANGE_TXT, PALE_ORANGE,
              floated=True)
textbox(s, 116 + 4 * (cw + gap), 790, 4 * cw + 3 * gap, 170, [
    P("抵抗は H 以外、手伝う人がかけた", 24, color=GRAY, spacing=1.4),
    P("B〜G は文献の課題（Forman 2019、Lacelle 2025）", 24, color=GRAY, spacing=1.4)],
    anchor=MSO_ANCHOR.MIDDLE)

# 5 どう比べたか
s = deck.slide(NOTES["method"])
title(s, "どう比べたか", 5)
bullets(s, 120, 250, 1672, 170, ["確認動作 ＝ 誰も押さえず、手首を反らしきる（疲れる前の最初に取る）",
                                 "確認動作 ÷ 課題の MVC が 100% 以下なら、全力を出し切れている"], size=40, gap=16)
textbox(s, 116, 500, 500, 90, [P("課題の MVC", 34, True)], anchor=MSO_ANCHOR.MIDDLE)
box(s, 640, 513, 700, 64, fill=BLUE, radius=4)
textbox(s, 1360, 500, 432, 90, [P("＝ 100 %MVC", 32, True, NAVY)], anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 116, 610, 500, 90, [P("確認動作", 34, True)], anchor=MSO_ANCHOR.MIDDLE)
box(s, 640, 623, 400, 64, fill="9DB8D3", radius=4)
textbox(s, 1060, 610, 732, 90, [P("100% 以下　→　足りている", 32, True, BLUE)], anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 116, 710, 500, 90, [P("確認動作（足りない例）", 30, color=GRAY)], anchor=MSO_ANCHOR.MIDDLE)
box(s, 640, 723, 900, 64, fill=PALE_GRAY, line=GRAY, dash=True, radius=4)
textbox(s, 1560, 710, 232, 90, [P("超える\n→ 足りない", 24, True, ORANGE_TXT)], anchor=MSO_ANCHOR.MIDDLE)
line(s, 1340, 490, 1340, 800, INK, 3, dash=True)

# 6 伸展の結果
s = deck.slide(NOTES["ext"])
title(s, "伸展：B で足りた", 6)
bullets(s, 120, 250, 1672, 170, ["腕を机に乗せ、上から押さえてもらう（B）で 56 %MVC",
                                 "確認動作は疲れる前に取った　→　疲れがあっても結論は同じ"], size=42, gap=16)
textbox(s, 116, 450, 1676, 40, [P("伸筋側：確認動作は MVC の何 %か", 28, True, GRAY)])
pct_bars(s, [("09-29　A", "自分の反対の手で押さえる", 350, False),
             ("10-06　A", "同じやり方", 96, False),
             ("10-06　B", "他の人に上から押さえてもらう", 56, True)], 520, 92, 2.6)
textbox(s, 1100, 450, 692, 40, [P("A が日で違う理由は未確定（センサの位置？押さえ方？）", 24, color=GRAY,
                                  align=PP_ALIGN.RIGHT)])
takeaway(s, "伸展の MVC は B に決める", BLUE)

# 7 足りなかったこと
s = deck.slide(NOTES["short"])
title(s, "足りなかったこと", 7)
bullets(s, 120, 250, 1672, 260, ["屈曲は、確認動作が 416 %MVC で足りない",
                                 "続けて取ったので、ほかの課題の差は疲れと分けられない",
                                 "D 以降（屈曲の I・J も）は腕を浮かせた　→　うまくいかなそう"], size=42, gap=12)
textbox(s, 116, 560, 1676, 40, [P("屈筋側：確認動作は MVC の何 %か", 28, True, GRAY)])
pct_bars(s, [("J　相手の手を握る", "屈曲で一番大きい課題", 416, True)], 660, 100, 2.4, color=ORANGE)
takeaway(s, "腕を浮かせず、休みをとって取り直す", ORANGE_TXT)

# 8 次やること
s = deck.slide(NOTES["next"])
title(s, "次やること", 8)
bullets(s, 120, 250, 1672, 80, ["腕は机に乗せる。疲れる前と後に確認動作を取る"])
box(s, 116, 370, 820, 170, fill=PALE_BLUE, line=BLUE, line_w=3, radius=12, anchor=MSO_ANCHOR.MIDDLE,
    pad=(24, 32, 24, 32), paras=[P("伸展（決定）", 28, True, BLUE, after=8),
                                 P("手のひら下・握って、上から押さえてもらう", 32, True)])
box(s, 972, 370, 820, 170, fill=PALE_ORANGE, line=ORANGE, line_w=3, radius=12, anchor=MSO_ANCHOR.MIDDLE,
    pad=(24, 32, 24, 32), paras=[P("屈曲（次回確かめる）", 28, True, ORANGE_TXT, after=8),
                                 P("机に向かって押し下げる", 32, True)])
textbox(s, 116, 590, 1676, 40, [P("次回の記録の順番", 28, True, GRAY)])
flow(s, 650, [("1 最初", "確認動作", False), ("2", "B・H\n2 回ずつ", True), ("3", "屈曲", True),
              ("4 最後", "確認動作\n＋ B", False)], w=370, gap=65, h=160)
textbox(s, 116, 850, 1676, 50, [P("記録の前に、センサの番号と位置を sensors.json に書く", 30, color=GRAY)])

# 9 まとめ
s = deck.slide(NOTES["summary"])
title(s, "まとめ", 9)
goal_boxes(s, 250)
box(s, 116, 560, 440, 56, fill=PALE_GRAY, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("前腕 2 か所で新しく取った", 30, True, GRAY, align=PP_ALIGN.CENTER)])
bullets(s, 116, 640, 740, 150, ["6 か所は、MVC を確かめてから"], size=36, gap=10)
box(s, 1032, 560, 440, 56, fill=PALE_BLUE, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("伸展は B に決定", 30, True, NAVY, align=PP_ALIGN.CENTER)])
bullets(s, 1032, 640, 760, 150, ["屈曲は次回確かめる", "一人で取れるかも残った"], size=36, gap=10)
takeaway(s, "来週：MVC を確かめて、6 か所で本番データを取る")

deck.save(SLIDES_DIR / "2026-10-08.pptx")
