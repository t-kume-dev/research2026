# 引き継ぎメモ（2026-10-06 時点）

PC を移るときに、Git に入っていないものと、やりかけのことをまとめたもの。
状況が変わったら書き換え、不要になったら消す。

## 1. 新しい PC での準備

1. `git clone https://github.com/t-kume-dev/research2026`
2. `analysis/` で依存ライブラリを入れる（Windows では UTF-8 モードが必要）

   ```powershell
   $env:PYTHONUTF8 = "1"; pip install -r requirements.txt
   ```
3. Delsys の DLL を置く：[Example-Applications](https://github.com/delsys-inc/Example-Applications) の
   `Python/resources/` の中身を**全部** `analysis/resources/` に（約 13 MB。`.gitignore` 済み）
4. 確認：`analysis/` で `python -m unittest discover tests` が 5 件とも通る

## 2. Git に入っていないもの

| もの | 場所 | 移し方 |
| --- | --- | --- |
| 09-29 のデモデータ | `data/raw/2026-09-29/` | **手で持っていく**（USB かクラウド、約 34 MB） |
| 10-06 の MVC 比較データ | `data/raw/2026-10-06/` | **手で持っていく**（約 105 MB）。CSV 13 個、`sensors.json`、`notes.txt` |
| Delsys の DLL | `analysis/resources/` | 1-3 のとおり取り直せばよい |
| API のキーとライセンス | `analysis/delsys_license.json` | まだない（届いたらここに書く） |
| 問い合わせメールの下書き | `_local/delsys_inquiry.md` | 先生に渡し済みなので不要 |

- どちらの日も、必要なのは **CSV と `sensors.json`（と `notes.txt`）** だけ。`.npz`・`calibration.json`・`mvc_compare.csv` は次で作り直せる

  ```powershell
  python -m emgpipe import-csv 2026-09-29
  python -m emgpipe recalib --session 2026-09-29
  python -m emgpipe normalize ../data/raw/2026-09-29/demo.npz
  python -m emgpipe import-csv 2026-10-06
  python -m emgpipe mvc-compare --session 2026-10-06
  ```
- 10-06 のセンサは 09-29 と逆（センサ 0 = 伸筋側、3 = 屈筋側）。記録中に上下がわからなくなり、課題ごとの反応から決めた。理由は `notes.txt`
- `_local/` は `.git/info/exclude` で除外していた。新しい PC で同じ使い方をするなら、そこに `_local/` を 1 行足す

## 3. やりかけのこと

| 状態 | やること | メモ |
| --- | --- | --- |
| 返事待ち | Delsys API のキーとライセンス | 問い合わせメールを先生に渡した。届いたら `analysis/delsys_license.json` に書き、Trigno Discover を閉じて `python -m emgpipe devices` |
| 確認 | 研究室の PC に一人用（H）の記録が残っていないか | 10-06 に取ったはずだが CSV がない（E と F のあいだが 3.5 分空いている）。Trigno Discover に残っていれば CSV に書き出し、`data/raw/2026-10-06/mvc_ext_fixed_solo_01.csv` として入れて `import-csv` → `mvc-compare` |
| 次に研究室で | MVC の取り直し | 10-06 の結果（`docs/progress/2026-10-08.md`）：伸展は B（`ext_fist_pron`）で確認動作 56 %MVC に収まった。屈曲は確認動作が 416 %MVC で足りない。取り直すのは B と H を 2 回ずつ、屈曲の課題、最後に確認動作。記録の前にセンサ番号と位置を `sensors.json` に書き、反らしてどちらが伸筋側か確かめる。1 試行ごとに CSV が書き出せたかその場で見る |
| 未着手 | 屈曲の MVC を決める | 曲げきる動きを屈曲の課題に加えるか、取り方を見直す。決まったら `calibration.py` の `DEFAULT_TASKS` と 4 章の表を差し替える（`mvc_trial.md` の「決め方」5） |
| 次に研究室で | 6 か所に付けて本番データを取る | 手順は 4 章。MVC を固めてから |
| 未着手 | コードの MVC 課題一覧を 6 課題に増やす | `analysis/emgpipe/calibration.py` の `MVC_TASKS` は、手首の伸展・屈曲・グリップと、伸展の MVC を比べる候補（`mvc_trial.md`）だけ。肩・肘の課題はまだない。CSV で進めるあいだは、ファイル名に課題名が入っていれば動くので困らない。API で `calibrate` を使うときに必要 |
| 未確認 | デモの 41 秒の屈筋側の振れ | 反らしきった手首を戻した瞬間に約 100 %MVC。戻す動きの筋活動か、手が机に当たったノイズか |
| 未着手 | エイム課題のイベント記録 | 「静止区間の残余活動」を出すには、待機中・クリック直前などの区間が要る。マウスのクリック・位置の時刻ログを取り、EMG と時刻を合わせる仕組みを作る。Aim Lab を使う場合、Discover のマーカーは 1 本（1 タスク）ごとに始まりと終わりの 2 つ |
| 検討中 | 前腕の小指側にセンサを足すか | マウスを左右に振る動き（橈屈・尺屈）のうち、小指側は今の上下 2 か所では弱く映る可能性。波形を見てから決める |
| 検討中 | 最終実験での下側センサの付け方 | 前腕の下側のセンサは、腕を机に置くと当たって邪魔。貼る位置をずらす、Trigno Mini を使う、アームレストを使う など |

## 4. Trigno Discover で記録する手順

API のキーが届くまでは、この手順で CSV を取り、`import-csv` から正規化する。

### 準備

- 電極を付け、どのセンサ番号をどこに付けたかを `sensors.json`（部位 → センサ番号）に書く

  ```json
  {
    "前腕の上（伸筋群）": 3,
    "前腕の下（屈筋群）": 0,
    "三角筋中部": 1,
    "上腕二頭筋": 2,
    "上腕三頭筋": 4,
    "僧帽筋上部": 5
  }
  ```
  （番号は例。付けた日に実物を見て書く）

  | 筋 | 付け方 |
  | --- | --- |
  | 前腕の伸筋群（前腕の上） | 前腕バンド |
  | 前腕の屈筋群（前腕の下） | 前腕バンド |
  | 三角筋中部 | 上腕バンド（肩寄り） |
  | 上腕二頭筋 | 上腕バンド |
  | 上腕三頭筋 | 上腕バンド |
  | 僧帽筋上部 | 貼り付け（探索期間だけ） |
- Trigno Discover を開き、全センサの波形が出ていることを確認する

### 記録（1 回ごとに別ファイルで書き出す）

動作の始まりと終わりに Discover のマーカーを付ける。`import-csv` は最初と最後のマーカーの間だけを使う。

| 内容 | 長さ | ファイル名 |
| --- | --- | --- |
| 安静：マウスに手を置いたまま脱力（マウスがなければ机の上で） | 10 秒 | `rest.csv` |
| 手首の伸展：手の甲を上に反らす（固定方法は 3 章を参照） | 5 秒 × 3 | `mvc_wrist_extension_01.csv` 〜 `_03` |
| 手首の屈曲：机に置いた手を下に押し下げる | 5 秒 × 3 | `mvc_wrist_flexion_01.csv` 〜 `_03` |
| 肩の外転：腕を横に 90° 上げ、上から押さえてもらって全力で持ち上げる | 5 秒 × 3 | `mvc_shoulder_abduction_01.csv` 〜 |
| 肘の屈曲：肘を 90° に曲げ、手首を押さえてもらって全力で曲げる | 5 秒 × 3 | `mvc_elbow_flexion_01.csv` 〜 |
| 肘の伸展：同じ姿勢で全力で伸ばす | 5 秒 × 3 | `mvc_elbow_extension_01.csv` 〜 |
| 肩のすくめ：肩を上から押さえてもらい、全力ですくめる | 5 秒 × 3 | `mvc_shoulder_shrug_01.csv` 〜 |
| （任意）橈屈・尺屈：手を縦にして、親指側を上に／小指側を下に全力で | 5 秒 × 3 | `mvc_radial_deviation_01.csv` 〜 / `mvc_ulnar_deviation_01.csv` 〜 |
| エイム練習など | 自由 | `aim_01.csv` など |

- MVC はマウスを持たずに取る。前腕を机に置き、手のひらは下向き。手首がほとんど動かない状態で力だけを全力で出す
- 試行間は 60 秒休憩（全部で 20 分近くかかる。長すぎれば 2 試行・30 秒休憩に減らしてよい）
- 電極は途中で貼り直さない（貼り直したら安静と MVC から取り直す）
- エイムの記録は、始めた直後にマウスを 3 回強く握るなどの合図を入れておくと、後でゲーム側のログと時刻を合わせやすい

### 保存

- 全ファイルを `data/raw/<日付>/` に入れる（`.gitignore` 済み）
- 何秒ごとに何をしたか、どの姿勢で MVC を取ったかを同じフォルダの `notes.txt` に書く
