"""コマンドライン入口。analysis/ で `python -m emgpipe <コマンド>` として使う。

  devices     接続してセンサとチャネルを一覧する（機材スパイクの最初の確認）
  record      自由記録（練習中など）
  calibrate   安静参照 + MVC の手順を実行し、calibration.json を作る
  recalib     記録済みのセッションから calibration.json を作り直す
  mvc-compare MVC の課題ごとの大きさと、確認動作（check_*）が何 %MVC になるかを比べる
  normalize   記録を calibration.json で正規化する
  plot        記録（生 / 正規化済み）を表示する
  import-csv  Trigno Discover の CSV をまとめて .npz に変換する（API キーがないときの代わり）

--source sim を付けると疑似信号で動く（既定は delsys = 実機）。
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .calibration import (ProtocolConfig, Calibration, calibration_from_dir, compare_tasks, normalize,
                          print_calibration, print_comparison, run_protocol, save_comparison)
from .recording import Recording, record
from .sources import make_source

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"


def _session_dir(arg: str | None) -> Path:
    if arg:
        p = Path(arg)
        return p if p.is_absolute() or p.exists() else RAW_DIR / arg
    return RAW_DIR / datetime.now().strftime("%Y-%m-%d")


def _open(args):
    kw = {"realtime": True, "seed": args.seed} if args.source == "sim" else {"emg_only": not args.all_channels}
    src = make_source(args.source, **kw)
    src.connect()
    return src


def cmd_devices(args):
    src = _open(args)
    print("\n取得するチャネル:")
    for c in src.channels:
        print(f"  {c.name:<16} {c.type:<5} {c.fs:9.3f} Hz  ({c.sensor})")
    src.close()


def cmd_record(args):
    src = _open(args)
    out_dir = _session_dir(args.session)
    name = args.name or datetime.now().strftime("free_%H%M%S")
    rec = record(src, args.duration, args.task)
    path = rec.save(out_dir / f"{name}.npz")
    src.close()
    print(f"保存: {path}")
    for n in rec.emg_names:
        print(f"  {n}: {rec.data[n].size} samples")


def cmd_calibrate(args):
    src = _open(args)
    cfg = ProtocolConfig(rest_s=args.rest, tasks=tuple(args.tasks), trials=args.trials,
                         contraction_s=args.contraction, rest_between_s=args.rest_between)
    out_dir = _session_dir(args.session)
    run_protocol(src, out_dir, cfg, interactive=not args.yes)
    src.close()
    print(f"保存: {out_dir / 'calibration.json'}")


def cmd_recalib(args):
    out_dir = _session_dir(args.session)
    calib = calibration_from_dir(out_dir)
    calib.save(out_dir / "calibration.json")
    print_calibration(calib)


def cmd_mvc_compare(args):
    out_dir = _session_dir(args.session)
    rows = compare_tasks(out_dir)
    print_comparison(rows)
    print(f"保存: {save_comparison(rows, out_dir / 'mvc_compare.csv')}")


def cmd_normalize(args):
    src_path = Path(args.file)
    calib_path = Path(args.calib) if args.calib else src_path.parent / "calibration.json"
    calib = Calibration.load(calib_path)
    out = normalize(Recording.load(src_path), calib)
    path = out.save(src_path.with_name(src_path.stem + "_norm.npz"))
    print(f"保存: {path}")


def cmd_import_csv(args):
    from .discover_csv import import_dir
    out_dir = _session_dir(args.session)
    saved = import_dir(out_dir, crop=not args.no_crop)
    print(f"{len(saved)} ファイルを変換: {out_dir}")


def cmd_plot(args):
    from .plot import plot_file
    plot_file(Path(args.file), out=Path(args.out) if args.out else None)


def main(argv=None):
    p = argparse.ArgumentParser(prog="emgpipe")
    p.add_argument("--source", choices=["delsys", "sim"], default="delsys")
    p.add_argument("--seed", type=int, default=None, help="疑似信号の乱数シード")
    p.add_argument("--all-channels", action="store_true", help="EMG 以外（IMU など）も記録する")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("devices").set_defaults(func=cmd_devices)

    r = sub.add_parser("record")
    r.add_argument("--duration", type=float, default=30.0)
    r.add_argument("--session", help="セッション名か保存先ディレクトリ（既定は data/raw/<今日の日付>）")
    r.add_argument("--name", help="ファイル名（拡張子なし）")
    r.add_argument("--task", default="", help="記録のラベル")
    r.set_defaults(func=cmd_record)

    c = sub.add_parser("calibrate")
    c.add_argument("--session")
    c.add_argument("--rest", type=float, default=10.0, help="安静参照の長さ [s]")
    c.add_argument("--tasks", nargs="+", default=list(ProtocolConfig.tasks))
    c.add_argument("--trials", type=int, default=3)
    c.add_argument("--contraction", type=float, default=5.0, help="1試行の収縮時間 [s]")
    c.add_argument("--rest-between", type=float, default=60.0, help="試行間の休憩 [s]")
    c.add_argument("--yes", action="store_true", help="Enter 待ちとカウントダウンを省く（動作確認用）")
    c.set_defaults(func=cmd_calibrate)

    rc = sub.add_parser("recalib")
    rc.add_argument("--session", required=True)
    rc.set_defaults(func=cmd_recalib)

    mc = sub.add_parser("mvc-compare")
    mc.add_argument("--session", required=True)
    mc.set_defaults(func=cmd_mvc_compare)

    n = sub.add_parser("normalize")
    n.add_argument("file")
    n.add_argument("--calib", help="既定は同じディレクトリの calibration.json")
    n.set_defaults(func=cmd_normalize)

    ic = sub.add_parser("import-csv")
    ic.add_argument("session", help="CSV が入ったフォルダ（セッション名かパス）")
    ic.add_argument("--no-crop", action="store_true", help="マーカー区間で切り出さず、全体を残す")
    ic.set_defaults(func=cmd_import_csv)

    pl = sub.add_parser("plot")
    pl.add_argument("file")
    pl.add_argument("--out", help="画像に保存する場合のパス")
    pl.set_defaults(func=cmd_plot)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
