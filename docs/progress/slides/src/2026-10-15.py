"""2026-10-15 の進捗報告スライドを作る。

    python docs/progress/slides/src/2026-10-15.py

docs/progress/slides/2026-10-15.pptx に書き出す。次の週は、このファイルをコピーして
中身（NOTES と各スライド）を差し替える。
"""
from pptx_kit import *  # noqa: F401,F403
from pptx_kit import px

IMG = REPO / "docs/progress/img"

NOTES = {
    "cover": """\n今週は、記録のやり方を Trigno Discover の CSV から Delsys API に移しました。結論から言うと、API で Discover と同じ設定で記録でき、センサ 2 本の同時記録と、本番の MVC と同じ流れでの続けての記録まで確かめました。あわせて、研究の背景に使える論文を 1 本読みました。

流れは、目標 → やったこと → わかったこと → 次やること → まとめ、の順で話します。
""",
    "goal": """\n大きな目標は先週と同じで、EMG でデータを取り、実際に違いが出ているデータを確認することです。

そのための小さな目標が、Trigno Discover で CSV を書き出すやり方から、Delsys API で直接記録するやり方に移すことです。

API は、Delsys が配っている、プログラムから基地局を動かすための部品です。Discover を開かずに、自分のコードから記録の開始・停止やデータの受け取りができます。使うにはキーとライセンスが要り、先週届きました。

移す理由は 2 つです。1 つ目、Discover では 1 回ごとに手で CSV を書き出していて、書き出し忘れが起きました。10-06 の一人でやる方法（H）は、取ったのに CSV がなく比べられませんでした。2 つ目、API なら記録してすぐ保存でき、MVC の手順（calibrate）や、エイム課題との時刻合わせもコードで扱えます。
""",
    "done": """\nやったことは 4 つです。

1 つ目、届いた API のキーとライセンスで、自分の PC から基地局（Trigno Centro）につなぎました。自分のコード（emgpipe）で、API から記録できるようにしています。届いた .key と .lic のファイルをそのまま置けば読むようにし、今の API で接続の設定が失敗するのを直しました。

2 つ目、記録中に、指示（「脱力」「全力で反らす」など）と筋活動のグラフを出す窓を作りました。

3 つ目、10-13 に研究室で実機で試しました。センサ 1 本で 10 秒（5 秒脱力 → 3 秒反らす → 2 秒脱力）、センサ 2 本で同時に 10 秒、それから、つないだまま安静 → 伸展 × 2 → 屈曲 × 2 の 5 回を続けて記録しました。最後のは本番の MVC と同じ流れで、力は入れていません。

4 つ目、論文を 1 本読みました。Neri ほか（2021）で、FPS の練習で、難しさを本人の成績に合わせて上げていくと上達が速くなるか、を調べたものです。
""",
    "api": """\n小さな目標への答えです。API で記録できるようになりました。Discover と同じ設定で取れ、筋の動きにも反応しました。

設定は Discover と同じ Avanti、2148 Hz です。10 秒で 21,481 サンプルで、10 秒 × 2148 Hz とちょうど合い、取りこぼしはありませんでした。

左の図が記録中の窓です。上に今の指示と経過秒、下に直近 5 秒の筋活動（0.1 秒ごとの RMS、μV）が出ます。この図は、記録したデータの 7.5 秒目を、窓と同じ描き方で描き直したものです。

脱力は 2 μV で、Discover のとき（3〜5 μV）と同じくらいでした。反らすと 43〜46 μV に上がり、戻すとすぐ 2 μV に戻りました。今回は自分で反らしただけで、押さえてもらっていないので、全力の MVC ではありません。

【10-13 の記録（包絡線の 1 秒ごとの平均、μV）】
api_test_03：2, 2, 2, 2, 2, 21, 46, 43, 11, 2（0〜5 秒 脱力、5〜8 秒 反らす、8〜10 秒 脱力）
0.5 秒平均の最大は 51 μV
包絡線は 20〜450 Hz のバンドパス → 整流 → 6 Hz のローパス。単位は API も Discover の CSV も mV
""",
    "flow": """\n本番に向けて、2 つ確かめました。

1 つ目、センサ 2 本を同時に記録して、両方とも 21,481 サンプルでそろいました。

2 つ目、つないだまま、安静 → 伸展 × 2 → 屈曲 × 2 の 5 回を続けて記録して、途中で止まりませんでした。本番の MVC（安静 → 課題ごとに数回）を API で回せます。

確かめていないことは 3 つです。6 本同時（今回は 2 本まで）、数分の長い記録（今回は 10 秒まで）、全力の MVC です。MVC の取り方は、今週は進めていません。

【calib_test の設定】安静 3 秒、伸展・屈曲 2 秒 × 2、休憩 2 秒。サンプル数は安静 6,444、各試行 4,296 で、すべて合っていた。力を入れていないので値は使わない。

【うまくいかなかったこと】

つながるまでに 3 か所でつまずきました。1 つ目、基地局が自分の PC につながっていませんでした。ふだんは研究室の PC に挿さっているので、挿し替えました。2 つ目、センサが眠っていて、0 本と出ました。3 つ目、今の API は、使わない「同期出力」の周波数を決めないと、接続の設定が通りませんでした。同期出力は外部機器に合図を送る機能で、使わなくても、有効な値（37・74・148 Hz のどれか）を入れる必要がありました。

センサが肌から浮くと、信号の 97% が電源の雑音（50 Hz とその倍数）になり、反らしても変わりませんでした。記録の前に、脱力と反らしで差が出るか見る必要があります。

また、最初の 2 回は合図がなく、いつ反らすかわかりませんでした。合図のない記録は使えないので、記録中の窓を作りました。最初は窓の文字が「脱力」のまま変わらなかったので、毎回その場で描き直すように直し、記録中の画面を撮って切り替わることを確かめました。
""",
    "paper": """\n論文です。研究の背景に使えると思って読みました。本人の成績に合わせて練習を変えると、上達が速くなる。具体的なフィードバックで上達を促すという、この研究の考え方の裏付けになります。ゲームを研究している人が研究室にほかにもいるので、紹介も兼ねています。

Neri ほか（2021、Frontiers in Psychology）です。FPS 未経験の 21 人が、CS:GO を 1 日 2 時間 × 3 週間（15 回、約 30 時間）練習しました。半分は普通の CS:GO で、難しさは 4 段階から自分で選びます。もう半分は難しさを 24 段階にした改造版で、2 ラウンド続けて「倒した数が倒された数の 2 倍以上」になったら、実験者が 1 段上げました。

結果です。改造版のほうが、難しさ × 成績で見た点数が速く伸び、最大で約 2.5 倍難しい段階まで上がりました。射撃場の課題（止まった的・動く的を撃つ）は、両群とも練習の前後で上達しましたが、群の差はありませんでした。注意や反応の速さなどの認知課題も両群で速くなり、3 か月後も残りました。筋電や体の動きは測っていません。

【改造版の難しさ】敵のボットの能力（狙いの速さ・正確さ、反応時間、連携、攻撃性、武器の得意不得意、移動の速さ）を約 100 通り組み合わせ、チームの強さ・人数・武器・マップの広さで 24 段階にした。24 段階目で基準を満たしたら 17 段階目に戻し、基準を 3 倍に上げる。
""",
    "paper_limit": """\nこの論文を背景に使うときの注意です。

改造版が勝っていたのは、「補正した K/D」という指標です。K/D は倒した数 ÷ 倒された数で、それに難しさの段階をかけたものです。例えば K/D 2.3、段階 16 なら 36.8 です。

改造版は、成績が良いと段階が上がるので、この指標は伸びやすくなります。段階が上がると敵が強くなり K/D は 2 前後に落ち着きますが、段階をかけるので点数は段階に比例して伸びます。さらに、普通版の 4 段階は 1・5・7・10 段階に当てはめられているので、一番難しい Expert を選んでも 10 段階です。改造版は 24 段階まであります。同じ K/D 2 でも、普通版は最大 20、改造版は最大 48 になります。当てはめ方の根拠は書かれていません。

段階をかけない K/D そのものは、2 群で差がありませんでした。エイムの課題でも差がありませんでした。なので、言えるのは「練習を個人に合わせると、ゲーム内の成績が速く伸びた（有利な指標で）」までです。フィードバックで上達する、エイムの技能が伸びる、という根拠にはなりません。改造版が変えたのは敵の強さだけで、プレイヤーにフィードバックはしていません。

ほかの弱点は予備のページにまとめています。
""",
    "next": """\n次やることです。

API で、決めたやり方の MVC を取ります。順番は、確認動作（疲れる前の最初）→ 伸展（B、腕を机に乗せ、上から押さえてもらう）→ 屈曲（机に向かって押し下げる）です。calibrate で、記録中の窓を出しながら取れるようにします。今は record にしか窓がありません。

あわせて、6 本同時と、数分の長い記録を実機で確かめます。窓は記録全体をつなぎ直して描いているので、長い記録だと重くなるかもしれません。

ほかの箇所（肩・上腕・僧帽筋）の MVC も考えます。
""",
    "summary": """\nまとめです。

大きな目標は、データを取る道具が Discover の CSV から API に移りました。違いが出ているデータの確認はまだです。

小さな目標は、API で、センサ 2 本まで、つないだまま続けて記録できました。6 本と長い記録は次回確かめます。

来週は、API で前腕の MVC を取ります。
""",
    "records": """\n（予備）10-13 に取った記録の一覧です。data/raw/2026-10-13/ にあります（Git 管理外）。

api_test_01 はセンサを肌に付ける前で、±5.5 mV の上限に 6% 張り付いていて、雑音だけでした。api_test_02 は付けたあとですが合図がなく、脱力 11〜14 μV、反らして 30 μV で、雑音の 51% が 50 Hz でした。api_test_03 は窓の合図ありで、脱力 2 μV、反らして 43〜46 μV です。

数値は包絡線の 1 秒ごとの平均です。浮いたセンサの判定には、信号のうち 50 Hz とその倍数（±1 Hz）が占める割合を使いました。api_test_03 を最初に取ったとき（画面を見ていなかった回、消去済み）は 97% でした。
""",
    "paper_weak": """\n（予備）Neri 2021 の弱点です。

比べ方：段階をかけた指標は改造版に有利で、K/D そのものは差がない。普通版の段階の当てはめ方の根拠がない。普通版は難しさを自分で選び、改造版は実験者が上げたので、「本人に合わせたこと」と「強制的に難しくされたこと」を分けられない。段階は実験者が手で上げていて、実験者が群を知っていたかは読んだ範囲では書かれていない。

人数と対象：11 人と 10 人。検出力 0.93 は観察された効果量から逆算したもの。認知課題の解析は、自由度 F(2,16) から逆算すると 10 人前後に見える（本文で確かめていない）。対象は FPS 未経験者で、タイトルは「プロの FPS」だが、プロや経験者には試していない。

ベースラインと統制：コースの時間は改造版の群が練習前から約 30 秒遅く、伸びしろが大きかった可能性。ゲームをしない対照群がないので、認知の伸びが練習のおかげか、同じテストの慣れかを区別できない。

報告：全体・部分課題の全体の正答率は 3 か月後に下がった（p = 0.024）。3 か月後は直後に効果が出た課題だけ測っている。データは「求めに応じて公開」。表 1 の斜めの的の「外れ」が 938 などで、命中（71〜80）と桁が合わない。

文献：Neri, F., Smeralda, C. L., Momi, D. ほか（2021）Personalized Adaptive Training Improves Performance at a Professional First-Person Shooter Action Videogame. Frontiers in Psychology 12:598410.
""",
}


def goal_boxes(s, y):
    box(s, 116, y, 740, 250, fill=NAVY, radius=16, pad=(36, 40, 36, 40), paras=[
        P("大きな目標", 30, True, "BFD6EE", after=12),
        P("EMG で、違いが出ている\nデータを確認する", 44, True, "FFFFFF", spacing=1.3)])
    line(s, 1012, y + 130, 876, y + 130, BLUE, 6, head="end")
    box(s, 1032, y, 760, 250, fill=PALE_BLUE, line=BLUE, line_w=3, radius=16, pad=(36, 40, 36, 40), paras=[
        P("小さな目標", 30, True, BLUE, after=12),
        P("Discover の CSV から\nAPI での記録に移す", 44, True, spacing=1.3)])


def flow(s, y, steps, w=340, gap=72, h=200, x0=116):
    """左から右へ箱を並べ、矢印でつなぐ。steps は (ラベル, 本文, 強調するか)。"""
    for i, (lab, body, hot) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(s, x, y, w, h, fill=PALE_BLUE if hot else PALE_GRAY, line=BLUE if hot else RULE,
            radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(24, 24, 24, 24), paras=[
                P(lab, 26, True, BLUE if hot else GRAY, after=8), P(body, 32, True, spacing=1.3)])
        if i < len(steps) - 1:
            line(s, x + w + 4, y + h / 2, x + w + gap - 4, y + h / 2, GRAY, 4, head="end")


def check_rows(s, rows, y0, rh):
    """確かめたこと（済）と確かめていないこと（未）の一覧。rows は (済か, 項目, 補足)。"""
    for i, (ok, head, sub) in enumerate(rows):
        y = y0 + i * rh
        line(s, 116, y, 1792, y, "DDDDDD", 1.5)
        box(s, 116, y + rh / 2 - 26, 96, 52, fill=BLUE if ok else PALE_GRAY, line=None if ok else RULE,
            radius=26, anchor=MSO_ANCHOR.MIDDLE,
            paras=[P("済" if ok else "未", 26, True, "FFFFFF" if ok else GRAY, align=PP_ALIGN.CENTER)])
        textbox(s, 250, y, 560, rh, [P(head, 34, True, INK if ok else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, 830, y, 962, rh, [P(sub, 28, color=INK if ok else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
    line(s, 116, y0 + len(rows) * rh, 1792, y0 + len(rows) * rh, "DDDDDD", 1.5)


def stat(s, x, y, w, h, label, value, color=INK):
    box(s, x, y, w, h, fill=PALE_GRAY, radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(28, 16, 28, 16), paras=[
        P(label, 24, True, GRAY, after=4), P(value, 44, True, color)])


deck = Deck(SLIDES_DIR / "2026-10-08.pptx")

s = deck.slide(NOTES["cover"])
cover(s, "2026年10月15日")

# 1 今週の目標
s = deck.slide(NOTES["goal"])
title(s, "今週の目標", 1)
goal_boxes(s, 270)
textbox(s, 868, 318, 152, 40, [P("そのために", 26, True, BLUE, align=PP_ALIGN.CENTER)])
bullets(s, 120, 620, 1672, 200, ["Discover は 1 回ごとに手で CSV を書き出す　→　書き出し忘れ",
                                 "API なら記録してすぐ保存。MVC の手順もコードで回せる"], gap=24)

# 2 やったこと
s = deck.slide(NOTES["done"])
title(s, "やったこと", 2)
bullets(s, 120, 240, 1672, 230, ["自分のコードから基地局につなぎ、記録できるようにした",
                                 "実機で試した（10-13、研究室）",
                                 "論文を 1 本読んだ（Neri 2021）"], size=42, gap=12)
flow(s, 540, [("① つなぐ", "キーを置く\n設定を直す", True), ("② 窓を作る", "指示と筋活動を\n記録中に出す", True),
              ("③ 実機で試す", "1 本・2 本\n続けて 5 回", True)], w=500, gap=88)

# 3 API で記録できた
s = deck.slide(NOTES["api"])
title(s, "API で記録できた", 3)
bullets(s, 120, 220, 1672, 150, ["Discover と同じ設定（Avanti、2148 Hz）。10 秒で取りこぼしなし",
                                 "反らすと上がり、戻すとすぐ下がる"], size=40, gap=10)
textbox(s, 116, 380, 900, 34, [P("記録中の窓（7.5 秒目）", 22, True, GRAY)])
s.shapes.add_picture(str(IMG / "2026-10-15_api_live.png"), px(116), px(420), width=px(900))
stat(s, 1080, 420, 712, 112, "脱力", "2 μV")
stat(s, 1080, 548, 712, 112, "反らす", "43〜46 μV", BLUE)
stat(s, 1080, 676, 712, 112, "10 秒の記録", "21,481 サンプル")
takeaway(s, "API で、Discover と同じように取れる", BLUE)

# 4 本番の流れでも止まらなかった
s = deck.slide(NOTES["flow"])
title(s, "本番の流れでも止まらなかった", 4)
check_rows(s, [(True, "センサ 2 本を同時に", "両方 21,481 サンプルでそろった"),
               (True, "つないだまま 5 回続けて", "安静 → 伸展 × 2 → 屈曲 × 2（本番の MVC と同じ流れ）"),
               (False, "6 本を同時に", "今回は 2 本まで"),
               (False, "数分の長い記録", "今回は 10 秒まで"),
               (False, "全力の MVC", "押さえてもらっていない。取り方は今週は進めていない")], 240, 112)
takeaway(s, "本番の MVC を、API で回せる", BLUE)

# 5 論文
s = deck.slide(NOTES["paper"])
title(s, "論文：Neri ほか 2021", 5)
textbox(s, 116, 196, 1676, 70, [P("Personalized Adaptive Training Improves Performance at a Professional "
                                  "First-Person Shooter Action Videogame", 26, True, GRAY, spacing=1.1),
                                P("Frontiers in Psychology 12:598410", 22, color=GRAY)])
bullets(s, 120, 300, 1672, 130, ["FPS 未経験の 21 人が、CS:GO を 1 日 2 時間 × 3 週間",
                                 "難しさを成績に合わせて上げる群と、普通の群を比べた"], size=36, gap=6)
box(s, 116, 436, 820, 184, fill=PALE_GRAY, line=RULE, radius=12, pad=(32, 20, 32, 20), paras=[
    P("普通版", 28, True, GRAY, after=6), P("難しさは 4 段階から\n自分で選ぶ", 30, True, spacing=1.3)])
box(s, 972, 436, 820, 184, fill=PALE_BLUE, line=BLUE, line_w=3, radius=12, pad=(32, 20, 32, 20), paras=[
    P("改造版（本人に合わせる）", 28, True, BLUE, after=6),
    P("24 段階。K/D 2 以上が 2 回続くと\n実験者が 1 段上げる", 30, True, spacing=1.3)])
for i, (lab, body, hot) in enumerate([("ゲーム内の成績", "改造版が速く伸びた（最大で約 2.5 倍難しい段階まで）", True),
                                      ("エイムの課題", "両群とも伸びた。群の差はなし", False),
                                      ("認知の課題", "両群とも速くなった。練習しない群はない", False)]):
    y = 630 + i * 60
    textbox(s, 116, y, 400, 60, [P(lab, 28, True, INK if hot else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 520, y, 1272, 60, [P(body, 28, hot, INK if hot else GRAY)], anchor=MSO_ANCHOR.MIDDLE)
takeaway(s, "背景：練習を本人に合わせると、上達が速くなる")

# 6 論文：言える範囲
s = deck.slide(NOTES["paper_limit"])
title(s, "論文：言えるのはどこまでか", 6)
box(s, 116, 220, 1676, 100, fill=PALE_GRAY, radius=12, anchor=MSO_ANCHOR.MIDDLE, pad=(32, 0, 32, 0), paras=[
    dict(runs=[("改造版が勝った指標　", 28, True, GRAY), ("K/D × 難しさの段階", 40, True, INK)])])
textbox(s, 116, 350, 1676, 40, [P("届く段階の上限", 28, True, GRAY)])
scale = 40
for i, (lab, sub, lv, col) in enumerate([("普通版", "Expert でも 10 段階に当てはめ", 10, "9DB8D3"),
                                         ("改造版", "成績が良いと上がる", 24, BLUE)]):
    y = 400 + i * 110
    textbox(s, 116, y, 520, 100, [P(lab, 34, True), P(sub, 22, color=GRAY)], anchor=MSO_ANCHOR.MIDDLE)
    box(s, 640, y + 20, lv * scale, 60, fill=col, radius=4)
    textbox(s, 640 + lv * scale + 16, y, 300, 100, [P(f"{lv} 段階", 34, True)], anchor=MSO_ANCHOR.MIDDLE)
bullets(s, 120, 640, 1672, 160, ["K/D そのものと、エイムの課題は、2 群で差がない",
                                 "変えたのは敵の強さだけ。フィードバックはしていない"], size=36, gap=8)
takeaway(s, "言えるのは「個人に合わせると、ゲーム内の成績が速く伸びた」まで", ORANGE_TXT)

# 7 次やること
s = deck.slide(NOTES["next"])
title(s, "次やること", 7)
textbox(s, 116, 225, 1676, 40, [P("API で、決めたやり方の前腕の MVC を取る（記録中の窓を出す）", 30, True)])
flow(s, 285, [("1 最初（疲れる前）", "確認動作", False), ("2 伸展", "上から押さえてもらう", True),
              ("3 屈曲", "机に向かって押し下げる", True)], w=500, gap=88, h=150)
textbox(s, 116, 470, 1676, 40, [P("あわせてやること", 30, True)])
for i, (head, sub) in enumerate([("6 本を同時に\n記録する", "今回は 2 本まで"),
                                 ("数分の長い\n記録を確かめる", "今回は 10 秒まで\n窓が重くならないか"),
                                 ("ほかの箇所の\nMVC を考える", "肩・上腕・僧帽筋")]):
    box(s, 116 + i * 588, 530, 500, 250, fill=PALE_GRAY, line=RULE, radius=12, pad=(28, 28, 28, 28), paras=[
        P(head, 34, True, spacing=1.3, after=14), P(sub, 24, color="4A4A4A", spacing=1.3)])

# 8 まとめ
s = deck.slide(NOTES["summary"])
title(s, "まとめ", 8)
goal_boxes(s, 250)
box(s, 116, 560, 440, 56, fill=PALE_GRAY, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("取る道具が API に移った", 30, True, GRAY, align=PP_ALIGN.CENTER)])
bullets(s, 116, 640, 740, 150, ["違いが出ているデータの確認はまだ"], size=36, gap=10)
box(s, 1032, 560, 500, 56, fill=PALE_BLUE, radius=28, anchor=MSO_ANCHOR.MIDDLE,
    paras=[P("2 本・続けて記録できた", 30, True, NAVY, align=PP_ALIGN.CENTER)])
bullets(s, 1032, 640, 760, 150, ["6 本と長い記録は次回"], size=36, gap=10)
takeaway(s, "来週：API で前腕の MVC を取る")

# 9 予備：10-13 の記録
s = deck.slide(NOTES["records"])
title(s, "予備：10-13 の記録", 9)
cols = [(116, 330, "ファイル"), (460, 560, "内容"), (1030, 762, "結果")]
y0, rh = 270, 100
for x, w, head in cols:
    textbox(s, x, y0 - 50, w, 40, [P(head, 24, True, GRAY)])
rows = [("api_test_01", "1 本、肌に付ける前", "上限に 6% 張り付く。雑音だけ"),
        ("api_test_02", "1 本、付けたあと、合図なし", "脱力 11〜14 μV、反らして 30 μV\n雑音の 51% が 50 Hz"),
        ("api_test_03", "1 本、窓の合図あり", "脱力 2 μV、反らして 43〜46 μV"),
        ("api_test_2ch", "2 本、10 秒", "両方 21,481 サンプル"),
        ("calib_test/", "calibrate を短く（5 回続けて）", "5 回とも記録できた（値は使わない）")]
for i, row in enumerate(rows):
    y = y0 + i * rh
    line(s, 116, y, 1792, y, "DDDDDD", 1.5)
    for (x, w, _), v in zip(cols, row):
        textbox(s, x, y, w - 12, rh, [P(v, 26, x == 116, spacing=1.15)], anchor=MSO_ANCHOR.MIDDLE)
line(s, 116, y0 + len(rows) * rh, 1792, y0 + len(rows) * rh, "DDDDDD", 1.5)
textbox(s, 116, 800, 1676, 40, [P("数値は包絡線の 1 秒ごとの平均。data/raw/2026-10-13/（Git 管理外）", 22, color=GRAY)])

# 10 予備：Neri 2021 の弱点
s = deck.slide(NOTES["paper_weak"])
title(s, "予備：Neri 2021 の弱点", 10)
groups = [("比べ方", ["段階をかけた指標は改造版に有利", "普通版の段階の当てはめに根拠がない",
                     "「合わせた」と「難しくされた」を分けられない"]),
          ("人数と対象", ["11 人と 10 人", "認知課題は 10 人前後に見える", "FPS 未経験者だけ"]),
          ("統制", ["練習前のコースが改造版で約 30 秒遅い", "ゲームをしない対照群がない"]),
          ("報告", ["3 か月後に下がった課題もある", "データは求めに応じて公開", "表 1 に桁の合わない値"])]
for i, (head, items) in enumerate(groups):
    c, r = i % 2, i // 2
    x, y = 116 + c * 856, 230 + r * 300
    textbox(s, x, y, 820, 44, [P(head, 30, True, BLUE)])
    textbox(s, x, y + 54, 820, 230, [P("・" + t, 26, spacing=1.25, after=6) for t in items])

deck.save(SLIDES_DIR / "2026-10-15.pptx")
