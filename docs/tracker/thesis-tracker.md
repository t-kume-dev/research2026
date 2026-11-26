# Master's Thesis Progress Tracker（中身の下書き）

- 作成日: 2026-11-19
- 研究室の雛形（`template.pptx`、全 14 ページ）の月ごとの欄に合わせて、`docs/milestones.md` を書き出したもの
- 先生に見せる pptx は `python docs/tracker/make_tracker.py` で、この Markdown から `thesis-tracker.pptx` を作る。直すときはこの Markdown を直して回し直す
  （表紙の 2 枚目と How to use のページは外す。見出しの書式・各ページの欄の名前は変えない）
- 元は `docs/milestones.md`（2026-11-17 に組み直した版）。日付は目安。マイルストーンを変えたら、ここも合わせる
- 雛形の欄：Objectives / Milestones（1. objective 2. milestone 3. success criteria）・Planned Activities（☐ task + note、済んだら ✓）・Status（Not started / In progress / Complete）・Supervisor Comments（空けておく）
- objective の種類は雛形の a〜d：a. experiment design/data　b. system development/analysis　c. paper/presentation　d. etc.

---

## Research Timeline（3 ページ目）

| 月 | Research objective | milestones |
| --- | --- | --- |
| November 2026 | b. 筋電とゲームを一緒に記録する仕組み | M1 計測系が回る（ほぼ済）、M2 毎回取れる形になる（前半） |
| December 2026 | a. 最初の本番で、1 回の来室の流れを通す | M1 完了（12/10）、M2 完了（12/17） |
| January 2027 | a. 自分の通常プレイを取り続ける | M3 自己記録で差が見える（前半） |
| February 2027 | a/b. 取り続けながら、スコアが低い回の筋電を探す | M3 自己記録で差が見える（後半） |
| March 2027 | b. 差を図にし、実験1 の設計に入る | M3 完了（3/4）、M4 実験1 の設計が決まる（開始） |
| April–May 2027 | a. 実験1 の設計を決め、本実験を始める | M4 完了（4/1）、M5 実験1 が終わる（開始） |
| June–July 2027 | a/b. 本実験と分析を終える | M5 完了（7/29） |
| August–September 2027 | c. 修論の下書き | M6 修論の下書き（9/30） |
| October–November 2027 | c. 下書きの仕上げ | M7 修論の提出（準備） |
| December 2027 | Milestone checkpoint and thesis submission preparation | M7（最終確認） |
| January 2028 | Final thesis submission due | M7 修論の提出（2028/1〜2） |

---

## November 2026: Research Objectives

**Objectives / Milestones**

1. objective：b. system development — 筋電（6 か所）と、マウス・KovaaK's の結果を一緒に記録できるようにする
2. milestone：M1 計測系が回る（10 月までにほぼ済み）／M2 毎回取れる形になる（前半）
3. success criteria：クリック・マウスの動き・KovaaK's の結果を、時刻をそろえて記録できる。1 つのコマンドで筋電とマウスを同時に取れる

**Planned Activities**

- ✓ マウスとクリックを時刻付きで記録するツールを作る
  - ゲーム中も裏で取れる方式（Windows の Raw Input）。ゲーム中は約 125 Hz（8 ms ごと）
- ✓ KovaaK's の結果と時刻を合わせる
  - 5 回プレイし、倒した 370 体すべてで「倒した時刻 − 直前のクリック」が 5 ms 以内。撃った数 = 左クリックの数
- ✓ KovaaK's の結果の CSV を、記録のあとに自動で取り込む
  - 元のファイルは書き換えず、記録のフォルダにコピーする
- ☐ 筋電とマウスを同時に記録する（M2-2）（今週）
  - 1 つのコマンドで筋電・マウス・画面録画・KovaaK's の結果を、同じ時計でそろえて取る形まで。実機での確認は次の来室で
- ☐ 1 回の来室の流れを作る（M2-3）（今週）
  - MVC → KovaaK's 5 回を 1 つのコマンドで流す形まで。回ごとのスコアと %MVC の一覧はまだ

**Status**：In progress

**Supervisor Comments**：

---

## December 2026: Research Objectives

**Objectives / Milestones**

1. objective：a. experiment/data — 研究室で、1 回の来室の流れを本番として通す
2. milestone：M1 計測系が回る（完了）／M2 毎回取れる形になる（完了）
3. success criteria：1 回の来室で、MVC → KovaaK's 5 回（筋電・マウス・スコアを同時に記録）まで止まらずに通り、回ごとのスコアと %MVC が一覧で出る

**Planned Activities**

- ☐ 1 回の来室の流れを仕上げる（M2-3）
- ☐ 最初の本番（M2-4）
  - プレイ中に 6 か所とも 100 %MVC を超えないか。センサがマウス操作の邪魔にならないか
- ☐ 前腕以外 4 か所の確認動作を取る（M1-7。M1 の最後）
  - 4 か所とも 100 %MVC 以下に収まれば M1 完了
- ☐ プレイ中の筋電がどう見えるかを図にする
- ☐ 自分の通常プレイの記録（M3）を始める

**Status**：Not started

**Supervisor Comments**：

---

## January 2027: Research Objectives

**Objectives / Milestones**

1. objective：a. data — 自分の通常プレイを、毎回同じ手順で取り続ける
2. milestone：M3 自己記録で差が見える（前半）
3. success criteria：週 2 回の来室で、毎回 KovaaK's 5 回ぶんの筋電・マウス・スコアがそろっている

**Planned Activities**

- ☐ 週 2 回来室し、毎回 MVC → KovaaK's 5 回を取る
  - シナリオ・感度・DPI は固定（1wall 6targets small、Valorant 換算 感度 0.1・DPI 1600）
- ☐ 毎回、回ごとのスコアと %MVC の一覧を確かめる
  - 取りそこねた回があれば、その週のうちに取り直す
- ☐ 回の順番（慣れ・ウォームアップ）も一緒に記録する
  - 続けて遊ぶとスコアが上がる傾向が、11 月の試しで見えている
- ☐ 就活と並行して進める

**Status**：Not started

**Supervisor Comments**：

---

## February 2027: Research Objectives

**Objectives / Milestones**

1. objective：a/b. data/analysis — 取り続けながら、スコアが低い回に出る筋電の特徴を探す
2. milestone：M3 自己記録で差が見える（後半）
3. success criteria：週 2 回 × 8 週間ぶんがそろい、スコアが低い回の筋電の特徴の候補が出ている

**Planned Activities**

- ☐ 週 2 回の記録を続ける
- ☐ スコア（倒した数・精度）が低い回の筋電を見る
  - 候補：伸筋側・屈筋側に同時に力が入る度合い（力み）、どの部位に差が出るか
- ☐ クリック前後の筋電を、当たり・外れで比べる
  - 外したのは距離のせいか、力んだせいか
- ☐ 何日ぶん・何回ぶんあれば差が見えるかを見積もる

**Status**：Not started

**Supervisor Comments**：

---

## March 2027: Research Objectives

**Objectives / Milestones**

1. objective：b. analysis — 自己記録の差を図にまとめ、実験1 の設計に入る
2. milestone：M3 自己記録で差が見える（完了、3/4）／M4 実験1 の設計が決まる（開始）
3. success criteria：スコアが低い回に出る筋電の特徴を図で示せる。何日ぶん・何回ぶんあれば足りるかが分かる

**Planned Activities**

- ☐ 8 週間ぶんの結果を図にまとめる
- ☐ 実験1 で見る筋電の特徴を決める
- ☐ 予備実験（研究室の数名）の手順を作る
- ☐ 予備実験を始める
- ☐ 就活を終える（3 月の見込み）

**Status**：Not started

**Supervisor Comments**：

---

## Milestone Checkpoint: April–May 2027

**Objectives / Milestones**

1. objective：a. experiment design — 実験1 の設計を決め、本実験を始める
2. milestone：M4 実験1 の設計が決まる（完了、4/1）／M5 実験1 が終わる（開始）
3. success criteria：M3 の結果と予備実験で、見る筋電の特徴・手順・人数・来訪回数が決まる

**Planned Activities**

- ☐ 予備実験の結果をまとめる
- ☐ 実験1 の手順・人数・来訪回数を決める
- ☐ 被験者を集める
- ☐ 本実験を始める

**Status**：Not started

**Supervisor Comments**：

---

## Milestone Checkpoint: June–July 2027

**Objectives / Milestones**

1. objective：a/b. experiment/analysis — 実験1 の本実験と分析を終える
2. milestone：M5 実験1 が終わる（完了、7/29）
3. success criteria：本実験と分析が終わる。8 月に入る前に終える

**Planned Activities**

- ☐ 本実験を続ける
- ☐ 分析する
- ☐ 結果の図をそろえる

**Status**：Not started

**Supervisor Comments**：

---

## Milestone Checkpoint: August–September 2027

**Objectives / Milestones**

1. objective：c. paper — 修論の下書き
2. milestone：M6 修論の下書き（9/30）
3. success criteria：実験1 までで、修論の章立てと図表がそろう（夏の終わりに成果を出す）

**Planned Activities**

- ☐ 章立てを決める
- ☐ 図表をそろえる
- ☐ 下書きを書く
- ☐ （任意）実験2：フィードバックで上達するか
  - やる気と時間があればやる。修論の本体は実験1 まで

**Status**：Not started

**Supervisor Comments**：

---

## Milestone Checkpoint: October–November 2027

**Objectives / Milestones**

1. objective：c. paper — 下書きの仕上げ
2. milestone：M7 修論の提出（準備）
3. success criteria：先生に見せられる形の原稿ができる

**Planned Activities**

- ☐ 下書きを先生に見てもらう
- ☐ もらったコメントを直す
- ☐ （任意）実験2 の結果を足すか決める

**Status**：Not started

**Supervisor Comments**：

---

## December 2027 Milestone Checkpoint & Thesis Submission

- Milestone description：M7 修論の提出。M6 の下書きを仕上げて出す
- Planned activities：最終の直し、先生の確認、提出の手続き
- Expected output / evidence：提出できる形の修論
- Status：Not started
- Student notes：
- Supervisor comments：

**Final Thesis Submission Due: January 2028**（M7 の期限は 2028/1〜2）

---

## 補足メモ

- 月への割り振りは、`docs/milestones.md` の「一覧」の期限から決めた。期限の月を「完了」、その前を「開始」「前半」「後半」にした
- 11 月の ✓ は、`docs/progress/2026-11-19.md` と `docs/claude-notes/log.md` の 11-17 に書いてあること
- 雛形の PDF は使わない。pptx の雛形（`template.pptx`）から作る
- 実験2 は `docs/milestones.md` に合わせて、8〜11 月の「任意」にした
