# literature

読んだ論文の文献表と読書メモ。

## 運用

- **PDFは `literature/pdf/` に置く。Gitの管理対象外**（[理由](pdf/README.md)）
- 読書メモは `literature/notes/<著者姓>_<年>_<キーワード>.md` に書き、コミットする
- 下の文献表に1行追加する。`読了` 列を埋めていけば進捗がわかる

PDFのファイル名はメモと揃える。

```
literature/pdf/McGregor_2022_emg-similarity-feedback.pdf
literature/notes/McGregor_2022_emg-similarity-feedback.md
```

## 文献表

| 文献 | 内容 | 本研究との関係 | 読了 |
| --- | --- | --- | --- |
| [EMG space similarity feedback promotes learning of expert-like muscle activation patterns (Front Hum Neurosci, 2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9897456/) | 熟練者のEMGパターンとの類似度をフィードバックすると複雑な運動スキルの学習が促進される | **最重要**。手法の有効性の根拠であり、差別化すべき直接の先行研究 | |
| [Increasing muscle co-contraction speeds up internal model acquisition (Sci Rep, 2018)](https://www.nature.com/articles/s41598-018-34737-5) | 学習初期の同時収縮と内部モデル獲得の関係 | 脱力を「熟達の結果」と位置づける理論的根拠 | |
| [Temporal and quantitative variability in muscle electrical activity decreases as dexterous hand motor skills are learned (PLOS ONE, 2020)](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0236254) | 巧緻運動の学習に伴いEMGの変動性が減少する | 差分指標に変動性を含める根拠 | |
| [Expertise-Related Differences in Wrist Muscle Co-contraction in Drummers](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8343458/) | 熟達度と手首の同時収縮の関係 | 手首中心の微細動作という点でエイムに近い | |
| [Biofeedback training can enhance esports players' shooting performance (Comput Human Behav, 2025)](https://www.sciencedirect.com/science/article/pii/S0747563225002833) | 脳活動・視線のバイオフィードバック訓練で射撃時間が30〜47ms短縮 | eスポーツへの生体信号応用の先例。シャム統制群の設計を参照 | |
| [Method of Electrical Muscle Stimulation for Training FPS Game Players in the Timing of Shots (ACM, 2023)](https://dl.acm.org/doi/10.1145/3611067) | EMSによる射撃タイミングの訓練 | 身体を介したFPS支援の系譜。本研究は刺激ではなく可視化 | |
| [KovaaK's aim trainer as a reliable metrics platform (2024)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10925653/) | 市販エイムトレーナーの指標の信頼性 | 自作タスクの妥当性を議論する際の参照点 | |
| [Evaluating EEG neurofeedback in sport psychology: a systematic review of RCT studies](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11328324/) | スポーツ領域のニューロフィードバックRCTのレビュー | 訓練実験の設計と効果量の相場観 | |

## これから網羅する範囲

新規性の主張（「身体側を可視化したエイム支援は存在しない」）を確定させるための調査。

- **国際会議**: CHI、CHI PLAY、UIST、AHs（Augmented Humans）の過去5年
  - 検索語: `skill` `training` `wearable` `EMG` `aim` `esports`
- **国内**: WISS、情報処理学会HCI研究会・EC研究会、日本バーチャルリアリティ学会
- **身体スキル伝達系**: `motion guidance` `skill transfer` `body movement visualization`
  - スポーツ・楽器・伝統芸能領域に類似手法が多数あるはずなので、差別化軸を確認する
- **Delsys Trigno の実装事例**: SDK / リアルタイムストリーミングを使った研究の実装方法
