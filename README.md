# research2026

修士研究のメモ・計画・実装を管理するリポジトリ。

**テーマ**: ウェアラブル生体計測によるエイムスキル学習支援システム

エイム練習における「画面には映らない身体の使い方の差」を Delsys Trigno などのウェアラブルセンサで
捉え、熟達者または自己の成功試行との差分として学習者に提示するシステムを構築し、その学習促進効果を
検証する。

## ドキュメント

| ファイル | 内容 |
| --- | --- |
| [docs/research-plan.md](docs/research-plan.md) | 研究計画書。背景・新規性・システム構成・アルゴリズム・評価計画・スケジュール |
| [literature/README.md](literature/README.md) | 読んだ論文の文献表とメモの置き場 |

## ディレクトリ構成

```
docs/           研究計画、発表資料の下書き、議事メモ
literature/
  README.md     文献表（コミットする）
  notes/        論文ごとの読書メモ（コミットする）
  pdf/          論文PDF（.gitignore で除外。コミットしない）
```

実装が始まったら `unity/`（タスク）、`firmware/`（M5StickC）、`analysis/`（信号処理・統計）を追加する。

## 運用メモ

- 論文PDFはリポジトリに入れない。理由は [literature/pdf/README.md](literature/pdf/README.md) を参照
- 計測の生データもコミットしない（`.gitignore` で除外済み）。別途バックアップを用意する
