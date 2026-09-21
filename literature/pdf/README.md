# literature/pdf

**このフォルダの中身は Git の管理対象外です**（`.gitignore` で除外済み。このREADMEだけが例外）。

## 使い方

読んだ論文のPDFをここに置く。ファイル名は `著者姓_年_短いキーワード.pdf` に揃えておくと、
`literature/notes/` 側のメモやREADMEの文献表から参照しやすい。

```
literature/pdf/McGregor_2022_emg-similarity-feedback.pdf
literature/pdf/Heald_2018_cocontraction-internal-model.pdf
```

## なぜコミットしないのか

出版社の著作権物であり、リポジトリに含めて公開リポジトリへ push すると権利侵害になる。
プライベートリポジトリでも、共同研究者の追加や将来の公開で事故が起きやすいので入れない。

リポジトリの肥大化を防ぐ意味もある。論文PDFは1本あたり数MBになり、Git は差分を圧縮できないため
履歴に一度でも入ると永久に残る。

## バックアップしたい場合

Git ではなく Zotero、Mendeley、クラウドドライブを使う。Zotero を使うなら BibTeX を
`literature/references.bib` に書き出してコミットすれば、PDF本体なしで文献情報だけをバージョン管理できる。
