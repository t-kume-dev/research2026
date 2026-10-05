# analysis — EMG の取得と正規化

Trigno（Trigno Discover 世代）から Delsys API で EMG を取り、安静参照と MVC で正規化するところまで。
`docs/progress/2026-09-24.md` 4章の #1〜#3 に当たる。

```
emgpipe/
  sources.py      取得元。DelsysSource（実機）と SimulatedSource（疑似信号）が同じ形で使える
  recording.py    記録と .npz 入出力
  processing.py   バンドパス 20–450 Hz → 全波整流 → 6 Hz 低域通過で包絡線
  calibration.py  安静参照 + MVC の手順、calibration.json、正規化
  plot.py         波形の表示
tests/            疑似信号でパイプライン全体を通すテスト
```

## 実機を使う前の準備

1. `pip install -r requirements.txt`

   Windows で `UnicodeDecodeError: 'cp932' codec can't decode ...` が出たら、UTF-8 モードで実行する
   （`requirements.txt` の日本語コメントを cp932 で読もうとして失敗している）

   ```powershell
   $env:PYTHONUTF8 = "1"; pip install -r requirements.txt
   ```
2. Delsys の [Example-Applications](https://github.com/delsys-inc/Example-Applications) の
   `Python/resources/` の中身を**全部** `analysis/resources/` に置く。
   `DelsysAPI.dll` は `Signals.dll` などほかの DLL に依存しているため、単体では読み込めない
3. Delsys 発行のキーとライセンスを `analysis/delsys_license.json` に書く

   ```json
   {"key": "...", "license": "..."}
   ```

   環境変数 `DELSYS_KEY` / `DELSYS_LICENSE` でもよい。DLL とキーはどちらも `.gitignore` 済みで、コミットしない
4. Trigno Discover は閉じておく（開いているとベースを掴めない）

## 使い方

`analysis/` で実行する。`--source sim` を付けると機材なしで同じ流れを試せる。

```powershell
# 1. 接続確認。センサとチャネル（名前・種類・サンプリング周波数）が表示される
python -m emgpipe devices

# 2. キャリブレーション（安静10秒 → 伸展・屈曲の MVC 5秒×3試行、試行間60秒休憩）
python -m emgpipe calibrate --session 2026-10-01

# 3. 練習中などの記録
python -m emgpipe record --session 2026-10-01 --duration 60 --name aim_01

# 4. 正規化（同じセッションの calibration.json を使う）→ aim_01_norm.npz
python -m emgpipe normalize ../data/raw/2026-10-01/aim_01.npz

# 5. 表示
python -m emgpipe plot ../data/raw/2026-10-01/aim_01_norm.npz
```

保存先は `data/raw/<セッション>/`（`.gitignore` 済み）。記録済みファイルから `calibration.json` を
作り直すには `python -m emgpipe recalib --session 2026-10-01`。

テスト: `python -m unittest discover tests`

## Trigno Discover の CSV から使う（API キーがないとき）

Discover で記録して CSV に書き出し、1 つのフォルダ（例 `data/raw/2026-09-29/`）に入れる。
ファイル名は `rest.csv`、`mvc_<課題>_<試行>.csv`（例 `mvc_wrist_extension_01.csv`）、それ以外は自由。
同じフォルダに、部位とセンサ番号の対応表 `sensors.json` を置く。

```json
{"前腕の上（伸筋群）": 3, "前腕の下（屈筋群）": 0}
```

```powershell
python -m emgpipe import-csv 2026-09-29        # *.csv → *.npz。マーカーの最初〜最後だけ切り出す
python -m emgpipe recalib --session 2026-09-29 # rest.npz と mvc_*.npz から calibration.json
python -m emgpipe normalize ../data/raw/2026-09-29/demo.npz
python -m emgpipe plot ../data/raw/2026-09-29/demo_norm.npz
```

MVC の取り方を比べるとき（手順は `docs/lab/mvc_trial.md`）は、`mvc_<課題>_<試行>.csv` に加えて
確認動作を `check_<名前>.csv` で書き出し、`import-csv` のあとに次を実行する。

```powershell
python -m emgpipe mvc-compare --session 2026-10-xx  # 課題ごとの MVC と、確認動作が何 %MVC か。mvc_compare.csv にも保存
```

- 切り出したくないときは `import-csv --no-crop`
- CSV の単位は mV（API は V）。キャリブレーションと正規化する記録は、同じ取り方のものを組み合わせる

## 正規化の定義

| 出力 | 式 | 用途 |
| --- | --- | --- |
| `<ch>.env` | 包絡線（V） | 生の大きさ |
| `<ch>.pct_mvc` | env / MVC × 100 | 標準の %MVC |
| `<ch>.pct_mvc_rest` | (env − rest) / (MVC − rest) × 100 | 姿勢による保持活動の床を差し引いたもの |

- MVC 値は、全課題・全試行を通した「包絡線の 0.5 秒移動平均の最大値」。センサが筋を分離できないため、
  どの課題で最大になるかはチャネルごとに決まる（`calibration.json` の `mvc_source` に記録）
- rest は安静記録の前後 1 秒を除いた包絡線の中央値
- 「静止区間の残余活動」を指標にする場合、rest を引くと見たいものまで消えうるので、両方残している
- MVC が rest の 5 倍未満のチャネルは警告を出す（電極の接触不良か、収縮が足りない）

## 実機で確認が必要なところ

- `ScanSensors` の引数が API のバージョンで異なるため、両方の形を試している（`sources.py` の `_scan`）
- Avanti の EMG サンプリング周波数とチャネル名は `devices` で実測して確認する
- フィルタはオフライン用のゼロ位相。リアルタイム提示に進むときは因果フィルタに差し替える
