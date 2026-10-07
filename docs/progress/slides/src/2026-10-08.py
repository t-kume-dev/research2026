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
    "tasks_base": """\n10-06 に試した動作です。3 枚に分けて見せます。図は模式図で、手のひら下・手のひら上は横から、親指が上は上から見ています。

まず確認動作。誰も押さえずに、手首を自由に反らしきる動きです。09-29 のデモで 350 %MVC になったのと同じ動きで、疲れる前の最大を見るため、記録の最初に取りました。

A は前回までのやり方で、握って、自分の反対の手で手の甲を押さえて反らします。比べるための基準として 2 回取りました。

B は、同じ姿勢で、手伝う人に手の甲を上から押さえてもらいます。A と B は押さえる人だけが違うので、差を見れば「他の人に押さえてもらう」効果がわかる、という組み方です。ここまでの 3 つは腕を机に乗せて取りました。
""",
    "tasks_ext": """\n伸展のほかの候補です。文献の課題（Forman 2019、Lacelle 2025）から選びました。

上の段は親指が上（Forman 2019）。C は握って手の甲側へ押す（ECR、橈側手根伸筋）、D はそれに小指側（机の方向）も加える（ECU、尺側手根伸筋）、E は手伝う人に両手で包んでもらい、手を開きながら反らす（ED、総指伸筋）。

下の段は手のひら下。F は反らしながら親指側にも押す（Lacelle の ECR）、G は指を伸ばしたまま反らす（Lacelle の ED）、H は一人でできる方法として、机の天板の裏に手の甲を当てて押し上げる。

D 以降は腕を机から浮かせて取りました。H は CSV を書き出しそこねたので、結果がありません。試行は 1 回ずつです。
""",
    "tasks_flex": """\n屈曲です。

確認動作は、誰も押さえずに手のひら側に曲げきる動きです。手首から先を机の端から出して取りました。

課題は 2 つで、どちらも手のひら上（Forman 2019）。I は握って、こぶしを上から押さえてもらい、手のひら側に曲げる。J は手伝う人の指 2〜3 本を全力で握りながら曲げる。どちらも腕を机から浮かせて取りました。
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


SKIN, SKIN_LINE, DESK, RESIST, THUMB = "F1E3D6", "8A7A6C", "DDDDDD", "A6A6A6", "E2C8B0"


def motion(s, ox, oy, k, view, hand="fist", act="push", resist=None, rlabel="", float_=False, col=BLUE,
           extra=None):
    """動作の模式図。基準の大きさ 500×220 を k 倍して (ox, oy) に置く。
    view="side" は横から、"top" は上から（親指が上の向き）。
    act は push（固定して押す）、bend_up / bend_down（自由に反らす・曲げる）。"""
    def X(v): return ox + v * k
    def Y(v): return oy + v * k
    def L(v): return v * k
    fy = 80 if float_ else 120          # 前腕の上端
    if view == "side":
        box(s, X(0), Y(170), L(300), L(50), fill=DESK)
        textbox(s, X(8), Y(176), L(200), L(40), [P("机", 20, color=GRAY)])
        if float_:
            textbox(s, X(70), Y(134), L(230), L(34), [P("↕ 浮かせた", 20, True, GRAY)])
    else:
        box(s, X(0), Y(0), L(500), L(220), fill="F4F4F4")
        textbox(s, X(8), Y(186), L(400), L(34), [P("机（上から見た図）", 18, color=GRAY)])
        fy = 95
    top = view == "top"
    box(s, X(20), Y(fy), L(250 if top else 282), L(50), fill=SKIN, line=SKIN_LINE, line_w=2, radius=12)
    if top:  # 親指が上を上から見る：手を大きめに描き、親指が手の上に乗って見えるようにする
        hx, hy, hw, hh = (262, fy - 4, 180, 58) if hand == "open" else (262, fy - 22, 104, 94)
    elif hand == "open":
        hx, hy, hw, hh = 296, fy + 8, 150, 34
    else:
        hx, hy, hw, hh = 296, fy - 5, 72, 60
    if act == "push":
        box(s, X(hx), Y(hy), L(hw), L(hh), fill=SKIN, line=SKIN_LINE, line_w=2, radius=14)
        if top:
            if hand == "open":   # 伸ばした指の境目と、指に沿って伸びた親指
                for f in (0.3, 0.5, 0.7):
                    line(s, X(hx + 100), Y(hy + hh * f), X(hx + hw - 10), Y(hy + hh * f), SKIN_LINE, 1.5)
                tx, ty, tw, th = hx + 8, hy + 14, 100, 26
            else:                # 握った指の節と、上に乗った親指
                for dx in (72, 83, 94):
                    line(s, X(hx + dx), Y(hy + 8), X(hx + dx), Y(hy + 36), SKIN_LINE, 1.5)
                tx, ty, tw, th = hx + 8, hy + 42, 78, 28
            box(s, X(tx), Y(ty), L(tw), L(th), fill=THUMB, line=SKIN_LINE, line_w=2, radius=13)
            box(s, X(tx + tw - 22), Y(ty + 5), L(16), L(th - 10), fill="FFF7EF", line=SKIN_LINE, line_w=1,
                radius=4)
            textbox(s, X(hx - 72), Y(fy + 54), L(66), L(30), [P("親指", 19, True, SKIN_LINE, align=PP_ALIGN.RIGHT)])
            line(s, X(hx - 4), Y(fy + 66), X(tx + 14), Y(ty + th / 2), SKIN_LINE, 1.5)
            textbox(s, X(24), Y(fy - 34), L(180), L(30), [P("手の甲側", 18, True, GRAY)])
            textbox(s, X(24), Y(fy + 54), L(180), L(30), [P("手のひら側", 18, True, GRAY)])
        cx = hx + hw / 2
        ax = min(hx + hw + 26, 470)
        line(s, X(ax), Y(fy + 20), X(ax), Y(fy - 60), col, 7, head="end")
        if extra:
            textbox(s, X(ax - 290), Y(fy + (88 if top else 52)), L(320), L(40), [P(extra, 19, True, col, spacing=1.1,
                                                                   align=PP_ALIGN.RIGHT)])
        if resist == "desk":
            box(s, X(230), Y(hy - 26), L(200), L(22), fill=SKIN_LINE)
            textbox(s, X(100), Y(hy - 34), L(125), L(30), [P("天板の裏", 19, True, GRAY, align=PP_ALIGN.RIGHT)])
        elif resist:
            box(s, X(cx - 40), Y(hy - 24), L(80), L(22), fill=RESIST, radius=6)
            line(s, X(cx), Y(hy - 80), X(cx), Y(hy - 28), RESIST, 6, head="end")
            textbox(s, X(cx - 220), Y(hy - 76), L(205), L(34),
                    [P(rlabel, 19, True, GRAY, align=PP_ALIGN.RIGHT)])
    else:
        up = act == "bend_up"
        hs = box(s, X(hx - 6), Y(fy - 38 if up else fy + 28), L(hw), L(hh), fill=SKIN, line=SKIN_LINE,
                 line_w=2, radius=14)
        hs.rotation = -50 if up else 50
        if up:
            line(s, X(440), Y(fy + 10), X(440), Y(fy - 70), col, 7, head="end")
        else:
            line(s, X(440), Y(fy + 30), X(440), Y(fy + 100), col, 7, head="end")
        textbox(s, X(330), Y(fy + 60 if up else fy - 40), L(170), L(34), [P("誰も押さえない", 19, True, col)])


def motion_card(s, x, y, w, h, key, pose, cap, col, pale, k, hot=False, tags=(), **kw):
    box(s, x, y, w, h, fill=pale if hot else "FFFFFF", line=col if hot else RULE, line_w=4 if hot else 2,
        radius=12)
    textbox(s, x + 20, y + 14, w - 40, 50, [dict(runs=[(key + "　", 32, True, col), (pose, 24, True, GRAY)])])
    iw = 500 * k
    motion(s, x + (w - iw) / 2, y + 66, k, col=col, **kw)
    textbox(s, x + 20, y + 66 + 220 * k + 10, w - 40, 80, [P(cap, 26, True, spacing=1.25)])
    if tags:
        textbox(s, x + 20, y + h - 40, w - 40, 30, [P("　".join(tags), 20, True, ORANGE_TXT)])



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

# 4〜6 試した動作
s = deck.slide(NOTES["tasks_base"])
title(s, "試した動作：確認動作と A・B", 4)
bullets(s, 120, 230, 1672, 150, ["確認動作は誰も押さえない。疲れる前の最初に取った",
                                 "A と B は、押さえる人だけが違う"], size=40, gap=10)
cw, ch, cy = 540, 450, 400
cards = [("確認", "手のひら下", "手首を自由に反らしきる", dict(view="side", hand="open", act="bend_up"), False),
         ("A", "手のひら下・握る", "自分の反対の手で押さえる\n（前回までのやり方）",
          dict(view="side", resist="self", rlabel="自分の手"), False),
         ("B", "手のひら下・握る", "他の人に上から押さえてもらう",
          dict(view="side", resist="other", rlabel="他の人"), True)]
for i, (key, pose, cap, kw, hot) in enumerate(cards):
    motion_card(s, 116 + i * (cw + 28), cy, cw, ch, key, pose, cap, BLUE, PALE_BLUE, 0.96, hot=hot, **kw)

s = deck.slide(NOTES["tasks_ext"])
title(s, "試した動作：伸展のほかの候補", 5)
bullets(s, 120, 220, 1672, 70, ["文献の課題から、前腕の向き・握る／開く・横方向を変えた"], size=40)
ch = 360
cards = [("C", "親指が上・握る", "手の甲側へ押す", dict(view="top", resist="other", rlabel="他の人"), ()),
         ("D", "親指が上・握る", "手の甲側＋小指側",
          dict(view="top", resist="other", rlabel="他の人", extra="＋小指側（机へ）", float_=True), ("腕を浮かせた",)),
         ("E", "親指が上・開く", "包まれた手を開きながら反らす",
          dict(view="top", hand="open", resist="other", rlabel="両手で包む", float_=True), ("腕を浮かせた",)),
         ("F", "手のひら下・握る", "反らす＋親指側",
          dict(view="side", resist="other", rlabel="他の人", extra="＋親指側", float_=True), ("腕を浮かせた",)),
         ("G", "手のひら下・開く", "指を伸ばしたまま反らす",
          dict(view="side", hand="open", resist="other", rlabel="他の人", float_=True), ("腕を浮かせた",)),
         ("H", "手のひら下・握る", "一人で、天板の裏を押し上げる",
          dict(view="side", resist="desk", float_=True), ("腕を浮かせた", "CSV なし"))]
for i, (key, pose, cap, kw, tags) in enumerate(cards):
    r, c = divmod(i, 3)
    motion_card(s, 116 + c * (cw + 28), 300 + r * (ch + 20), cw, ch, key, pose, cap, BLUE, PALE_BLUE, 0.9,
                tags=tags, **kw)

s = deck.slide(NOTES["tasks_flex"])
title(s, "試した動作：屈曲", 6)
bullets(s, 120, 230, 1672, 150, ["確認動作は、手首から先を机の端から出して曲げきる",
                                 "課題は手のひら上の 2 つ。どちらも腕を浮かせた"], size=40, gap=10)
ch = 450
cards = [("確認", "手のひら下", "手首を自由に曲げきる", dict(view="side", hand="open", act="bend_down"), ()),
         ("I", "手のひら上・握る", "こぶしを押さえてもらい\n手のひら側へ曲げる",
          dict(view="side", resist="other", rlabel="他の人", float_=True), ("腕を浮かせた",)),
         ("J", "手のひら上", "相手の指を握りながら\n手のひら側へ曲げる",
          dict(view="side", resist="other", rlabel="他の人", float_=True), ("腕を浮かせた",))]
for i, (key, pose, cap, kw, tags) in enumerate(cards):
    motion_card(s, 116 + i * (cw + 28), cy, cw, ch, key, pose, cap, ORANGE_TXT, PALE_ORANGE, 0.96, tags=tags,
                **kw)

# 7 どう比べたか
s = deck.slide(NOTES["method"])
title(s, "どう比べたか", 7)
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

# 8 伸展の結果
s = deck.slide(NOTES["ext"])
title(s, "伸展：B で足りた", 8)
bullets(s, 120, 250, 1672, 170, ["腕を机に乗せ、上から押さえてもらう（B）で 56 %MVC",
                                 "確認動作は疲れる前に取った　→　疲れがあっても結論は同じ"], size=42, gap=16)
textbox(s, 116, 450, 1676, 40, [P("伸筋側：確認動作は MVC の何 %か", 28, True, GRAY)])
pct_bars(s, [("09-29　A", "自分の反対の手で押さえる", 350, False),
             ("10-06　A", "同じやり方", 96, False),
             ("10-06　B", "他の人に上から押さえてもらう", 56, True)], 520, 92, 2.6)
textbox(s, 1100, 450, 692, 40, [P("A が日で違う理由は未確定（センサの位置？押さえ方？）", 24, color=GRAY,
                                  align=PP_ALIGN.RIGHT)])
takeaway(s, "伸展の MVC は B に決める", BLUE)

# 9 足りなかったこと
s = deck.slide(NOTES["short"])
title(s, "足りなかったこと", 9)
bullets(s, 120, 250, 1672, 260, ["屈曲は、確認動作が 416 %MVC で足りない",
                                 "続けて取ったので、ほかの課題の差は疲れと分けられない",
                                 "D 以降（屈曲の I・J も）は腕を浮かせた　→　うまくいかなそう"], size=42, gap=12)
textbox(s, 116, 560, 1676, 40, [P("屈筋側：確認動作は MVC の何 %か", 28, True, GRAY)])
pct_bars(s, [("J　相手の手を握る", "屈曲で一番大きい課題", 416, True)], 660, 100, 2.4, color=ORANGE)
takeaway(s, "腕を浮かせず、休みをとって取り直す", ORANGE_TXT)

# 10 次やること
s = deck.slide(NOTES["next"])
title(s, "次やること", 10)
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

# 11 まとめ
s = deck.slide(NOTES["summary"])
title(s, "まとめ", 11)
goal_boxes(s, 250)
box(s, 116, 560, 440, 56, fill=PALE_GRAY, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("前腕 2 か所で新しく取った", 30, True, GRAY, align=PP_ALIGN.CENTER)])
bullets(s, 116, 640, 740, 150, ["6 か所は、MVC を確かめてから"], size=36, gap=10)
box(s, 1032, 560, 440, 56, fill=PALE_BLUE, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("伸展は B に決定", 30, True, NAVY, align=PP_ALIGN.CENTER)])
bullets(s, 1032, 640, 760, 150, ["屈曲は次回確かめる", "一人で取れるかも残った"], size=36, gap=10)
takeaway(s, "来週：MVC を確かめて、6 か所で本番データを取る")

deck.save(SLIDES_DIR / "2026-10-08.pptx")
