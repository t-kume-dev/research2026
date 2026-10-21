# 引き継ぎメモ（2026-10-20 時点）

PC を移るときに、Git に入っていないものと、やりかけのことをまとめたもの。
状況が変わったら書き換え、不要になったら消す。

## 1. 新しい PC での準備

1. `git clone https://github.com/t-kume-dev/research2026`
2. 前の PC で作った `research2026_transfer_<日付>.zip` を、リポジトリの一番上で展開する（2 章）

   ```powershell
   tar -x -f <zip のパス>
   ```
3. `analysis/` で依存ライブラリを入れる（Windows では UTF-8 モードが必要）

   ```powershell
   $env:PYTHONUTF8 = "1"; pip install -r requirements.txt
   ```
4. Delsys の DLL を置く：[Example-Applications](https://github.com/delsys-inc/Example-Applications) の
   `Python/resources/` の中身を**全部** `analysis/resources/` に（約 13 MB。`.gitignore` 済み）
5. `.git/info/exclude` に `_local/` を 1 行足す
6. 確認：`analysis/` で `python -m unittest discover tests` が 5 件とも通る。
   `python -m emgpipe --source sim --sim-channels 6 lab --session sim_test` で、疑似信号のまま窓が最後まで進む

## 2. Git に入っていないもの

zip（約 76 MB）に入れたもの：

| もの | 場所 | メモ |
| --- | --- | --- |
| 計測データ | `data/raw/2026-09-29/`・`10-06/`・`10-13/`・`10-20/` | 消えると戻せない。10-20 が最新（M1-4〜M1-6） |
| 論文 PDF | `literature/pdf/`（18 本） | 読書メモは `literature/notes/`（Git 管理） |
| API のキーとライセンス | `analysis/DelsysAPI.key`、`analysis/DelsysAPI.lic` | 中身はチャットや Git に出さない。zip も人に渡さない |
| ローカルのメモ | `_local/` | `delsys_inquiry.md`（先生に渡し済み）、`discover_recording.md`（API 以前の手順）。どちらも不要なら消してよい |

zip に入れていないもの：

| もの | 場所 | 理由 |
| --- | --- | --- |
| Delsys の DLL | `analysis/resources/` | 1-4 のとおり取り直せる |
| 進捗スライドの PDF | `docs/progress/slides/pdf/` | スライドのスクリプトを実行すれば作り直せる |
| OneNote の検証コード自動入力 | `~/Documents/develop/ms-otp/`（リポジトリの外） | 今の PC だけで使う。ほかの PC では検証コードを手で入れる。`pptx_kit.py` はフォルダがなければ何もしない |
| Claude にプッシュを許す設定 | `.claude/settings.local.json` | 必要なら新しい PC で作る（`Bash(git push)` を許可） |

- 09-29・10-06 は CSV から `.npz` を作り直せる（`import-csv` → `recalib` / `mvc-compare`）。zip には `.npz` も入っているので、そのままでも使える
- 基地局の USB は、ふだん研究室の PC に挿さっている。記録する PC に挿し替える

## 3. やりかけのこと

マイルストーンと内訳は `docs/milestones.md`。今は **M1：計測系が回る（〜11/5）**。

| 状態 | やること | メモ |
| --- | --- | --- |
| 次に研究室で（10/29 まで） | M1-7：残り 4 か所の MVC を一人用で試す | `python -m emgpipe lab --solo --session <日付>`。前の日に `sensors.json` を書いておく（番号はシール 1〜6） |
| 同じ日に | M1-6：手首の屈曲を取り直す | 10-20 は指示に手の向きと図がなく、手のひら下で曲げた可能性がある。確認動作は手のひら上で上に曲げきる（`lab` の指示と図は直してある）。課題は天板の裏を押し上げる（`flex_fixed_solo`） |
| 同じ日に | 直した窓を実機で確かめる | 姿勢の図・折り返し・休憩 10 秒。模擬では 6 チャネル・17 ステップが通った |
| 未着手 | 10-22 のスライド | 成果報告 `docs/progress/2026-10-22.md` から作る。`2026-10-15.py` をコピーし、表紙の次に `roadmap(steps=...)`。ノート案は報告の補足メモ。`roadmap()` の状態に「一部済」の色がまだない |
| 未着手 | 再現性を高めるためにすることを考える | 同じやり方（A）でも、09-29 は確認動作が約 350 %MVC、10-06 は 96%。M3 のときに考える |
| 未着手 | エイム課題のイベント記録 | M2 の中身。クリック・マウス位置の時刻ログを取り、EMG と時刻を合わせる |
| 未確認 | デモの 41 秒の屈筋側の振れ | 反らしきった手首を戻した瞬間に約 100 %MVC |
| 検討中 | 前腕の小指側にセンサを足すか、下側センサの付け方 | 波形を見てから。M4 より後は機能を足さない |

## 4. 研究室での 1 回ぶん

```powershell
cd analysis
python -m emgpipe devices                          # 6 本見つかるか（S1〜S6）
python -m emgpipe pair 3                           # 見つからない番号だけ登録し直す
python -m emgpipe lab --solo --session <日付>       # 信号の確認 → 安静 → 確認動作 → MVC 2 周 → 3 分の記録
```

- `pair` は、センサを充電台に載せたまま Enter を押し、すぐ外す
- 本番の手首の MVC は「上に全力で曲げ、人に押さえてもらう」（`--solo` を外す）
- 窓はクリックで進む。記録は `data/raw/<日付>/` に入り、最後に `mvc_compare.csv` と `calibration.json` を作る
- 何をしたかは同じフォルダの `notes.txt` に書く（`session_log.txt` は自動で残る）
