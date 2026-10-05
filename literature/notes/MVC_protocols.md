# MVC の取り方（手持ち文献 13 本のまとめ）

- 読んだ日: 2026-10-01
- 目的: 伸展の MVC で全力を出し切れなかった問題（`docs/progress/2026-10-01.md`）を解決するため、文献の取り方を後で試す
- PDF: `literature/pdf/`（Git 管理外）。2026-10-01 に Forman 2020（2 本）と D. A. Forman 博論（2020）を追加で取得

## 背景：今回うまくいかなかったこと

- 伸展の MVC は「机に固定した手を、自分の反対の手で押さえて反らす」で取った（5 秒 × 3）
- デモで手首を自由に反らしきっただけで、伸筋側がこの MVC の約 3.5 倍（約 350 %MVC）になった
- MVC が小さすぎると %MVC が 100% を超え、日をまたいだ比較の土台にならない

## 手順が書いてある文献

### Lacelle 2025（筋ごとの姿勢を表で明記）

- 研究者が手で抵抗をかける。1 筋につき約 3 秒 × 3 回。値はピーク
- 筋ごとの姿勢（表 5.3。Forman et al. 2020 と Gustafsson et al. 2011 による）

  | 筋 | 前腕 | 手 | 動き |
  | --- | --- | --- | --- |
  | ECR（橈側手根伸筋） | 回内（手のひら下） | 握る | 伸展 ＋ 橈屈（親指側） |
  | ED（総指伸筋） | 回内 | 開く | 伸展。抵抗は手の先のほう |
  | ECU（尺側手根伸筋） | 回内 | 半分開く | 伸展 ＋ 尺屈（小指側） |
  | APL（長母指外転筋） | 回内 | 開く | 橈屈 ＋ 母指外転 ＋ 伸展 |
  | FCR（橈側手根屈筋） | 回外（手のひら上） | 握る | 屈曲 |
  | FCU（尺側手根屈筋） | 回外 | 握る | 屈曲 ＋ 尺屈 |
  | FD（指屈筋） | 回外 | 開く | 屈曲。抵抗は手の先のほう |

- 別に MVE（最大随意努力、力センサで測る）も取る
  - 握力計で握力、6 軸力センサで手首伸展トルク。各約 3 秒 × 3 回
  - 姿勢：肩の屈曲・外転 約 15°、肘 110°、前腕 90° 回内、手首はまっすぐ（伸展・橈尺屈 0°）
- **MVE のときの EMG のほうが筋ごとの MVC より大きければ、MVE の値で正規化する**

### Forman 2023（博論）、Forman 2025（2 本）

- 筋ごとの MVC を、実験者が手で抵抗をかけて 2 ラウンド。全力のときは声をかけて励ます
- 細かい手順は本文になく、Forman 2020 を参照している。さらにたどった先が下の Forman 2019 の表
- MVC の後に、力センサで握力・橈屈・尺屈の最大も取る（約 3 秒 × 2 回、順番はランダム）
  - 橈屈・尺屈は、腕を板にベルトで固定し、マウスを持つ手の形を真似てボールを握った状態で行う
- MVC の値：RMS のピークを中心にした 1 秒（前後 0.5 秒）
- Forman 2025（Valorant）の考察：MVC の取り方や励まし方の違いで %MVC が変わる、と書いている

### Forman 2019（同じグループの元の手順。筋ごとの表）

- 参照のたどり方：Forman 2025 → Forman 2020（Sci Rep）→ 「Forman et al. 2019 の Table 1 を参照」
- Forman 2019（J Electromyogr Kinesiol 45:53–60）は有料。著者 D. A. Forman の博論（2020、Ontario Tech、公開）の 3 章が同じ論文で、表 3.1 に載っている
- 研究者が手で抵抗をかける。握り方や手首の動きを組み合わせて、筋ごとに狙う

  | 筋 | 前腕 | 手 | 動き |
  | --- | --- | --- | --- |
  | ECR（橈側手根伸筋） | 中間位（親指が上） | 握る | 伸展。手で抵抗 |
  | ED（総指伸筋） | 中間位 | 半分開いて研究者の手で包む | 伸展 ＋ 手を全力で開く |
  | ECU（尺側手根伸筋） | 中間位 | 握る | 伸展 ＋ 尺屈 |
  | FCR（橈側手根屈筋） | 回外（手のひら上） | 握る | 屈曲。手で抵抗 |
  | FDS（浅指屈筋） | 回外 | 半分開いて研究者の手を握る | 屈曲 ＋ 全力で握る |
  | FCU（尺側手根屈筋） | 回外 | 握る | 屈曲 ＋ 尺屈 |
  | 上腕二頭筋 | 回外 | — | 肘・肩 90°。肘を全力で曲げる |
  | 上腕三頭筋 | 中間位 | — | 肘・肩 90°。肘を全力で伸ばす |

- Lacelle との違い：伸筋側の前腕が**中間位（親指が上）**。Lacelle は回内（手のひら下）。ECR に橈屈を足していない
- 同じグループの Holmes 2022（PeerJ）：筋ごとに 2 回、**各 5 秒、間に 30 秒以上休憩**

### Forman 2020（Front Sports Act Living）：力センサで測る MVC

- EMG ではなく、手首の力の最大を力センサで測る手順。一人で取るときの参考になる
- 手首はまっすぐのまま、机に固定した力センサに向かって全力で伸展（または屈曲）する
  - **手は開いたまま**（指を伸ばす）。前腕は台にしっかり付ける。伸展の日は回内、屈曲の日は回外
  - 使わない手は、手のひらを上にして机の上に置く（押さえるのに使わせない）
- 3〜4 秒 × 2 回、間に 1 分休憩。声で励まし、**力の値を画面で見せる**。大きいほうを採用

### Wang 2023

- 「Perotto 2011（筋電図の解剖ガイド）に従った」とだけ書いている。具体的な姿勢はなし

## MVC を使っていない文献

- Park 2021：−1〜1 にスケーリング
- Prajapati 2024：StandardScaler で標準化
- Kuikkaniemi 2010：その時々の最小・最大で正規化（EMG ではなく呼吸・皮膚電気）
- Okinaka & Wada 2023：RMS のみ。正規化なし
- Donovan 2022、Dupuy 2024、Dupuy 2025：EMG を測っていない
- Jeong 2024：平均パワー周波数（MPF）だけを使っていて、振幅の正規化をしていない（PDF の文字が化けるため、ページを画像にして読んだ）

## 後で試すこと

上から順に試す。毎回、同じデモ（手首を反らしきる）で %MVC が 100% 以下に収まるかを確認する。

1. **抵抗を他の人にかけてもらう**
   - 今回との違いはここがいちばん大きい。どの文献も、抵抗は実験者がかけている。自分の反対の手で押さえているものはない
   - 全力のときに声をかけてもらう
2. **伸筋側の課題を筋ごとに分ける（Forman 2019・Lacelle の表）**
   - 伸展（握る）、伸展 ＋ 尺屈（握る）、伸展 ＋ 手を全力で開く、の 3 つを取る。Lacelle にならって伸展 ＋ 橈屈も足してよい
   - 前腕の向きは、中間位（親指が上、Forman）と回内（手のひら下、Lacelle）の 2 通りがある。両方試して大きいほうを見る
   - 今のセンサは大きく、伸筋を 1 つずつ分けて拾えない。課題を増やしておけば、チャネルごとに最大になった課題が自動で選ばれる
3. **一人でやる場合は、固定してから押す（MVE 寄り）**
   - 机の天板の裏に手の甲を当てて押し上げるなど、動かない物に対して押す
   - 姿勢は Lacelle の MVE を参考に：肘 110° くらい、手のひら下、手首はまっすぐ
   - Forman 2020 のように、使わない手は机の上に置いておく。押さえるのに使うと、押さえる側に力が逃げる
4. **それでも 100% を超える動きがあれば、その動きを課題に加える**
   - Lacelle も、MVE のほうが大きければそちらを使っている。全課題の最大を MVC にする今のコードと同じ考え方

試行の長さは 3〜5 秒（今は 5 秒）。回数は 2〜3 回。休憩は 30 秒〜1 分。

## 未確認

- Gustafsson et al. 2011、Perotto 2011 の具体的な姿勢

## 参考文献（追加で取得したもの）

- Forman, D. A. et al. (2019). The influence of simultaneous handgrip and wrist force on forearm muscle activity. *J Electromyogr Kinesiol*, 45, 53–60. https://doi.org/10.1016/j.jelekin.2019.02.004（有料。内容は下の博論の 3 章）
- Forman, D. A. (2020). *Muscle fatigue and other factors influencing forearm muscle activity*（博士論文, Ontario Tech University）. https://hdl.handle.net/10155/1210
- Forman, G. N. et al. (2020). Investigating the Muscular and Kinematic Responses to Sudden Wrist Perturbations During a Dynamic Tracking Task. *Sci Rep*, 10, 4161. https://doi.org/10.1038/s41598-020-61117-9
- Forman, D. A. et al. (2020). Sustained Isometric Wrist Flexion and Extension Maximal Voluntary Contractions Similarly Impair Hand-Tracking Accuracy in Young Adults Using a Wrist Robot. *Front Sports Act Living*, 2, 53. https://doi.org/10.3389/fspor.2020.00053
- Holmes, M. W. R. et al. (2022). The effects of isometric hand grip force on wrist kinematics and forearm muscle activity during radial and ulnar wrist joint perturbations. *PeerJ*, 10, e13495. https://doi.org/10.7717/peerj.13495（PDF は取得できず。Europe PMC で本文を読んだ）

## コードの場所

- MVC の課題一覧：`analysis/emgpipe/calibration.py` の `MVC_TASKS`（今は伸展・屈曲・グリップ）
- 測定の手順（案内つき）：同じファイルの `ProtocolConfig`（安静 10 秒、5 秒 × 3、試行間 60 秒）
- 研究室での手順書：`docs/handoff.md` の 4 章
- 「後で試すこと」を 1 回で比べる手順：`docs/lab/mvc_trial.md`。比較は `python -m emgpipe mvc-compare --session <日付>`
