"""コマンドライン入口。analysis/ で `python -m emgpipe <コマンド>` として使う。

  devices     接続してセンサとチャネルを一覧する（機材スパイクの最初の確認）
  record      自由記録（練習中など）
  calibrate   安静参照 + MVC の手順を実行し、calibration.json を作る
  recalib     記録済みのセッションから calibration.json を作り直す
  mvc-compare MVC の課題ごとの大きさと、確認動作（check_*）が何 %MVC になるかを比べる
  normalize   記録を calibration.json で正規化する
  long-stats  長い記録の %MVC の平均・上位 5%・最大を出す（10-29 の報告の表の確かめ）
  plot        記録（生 / 正規化済み）を表示する
  import-csv  Trigno Discover の CSV をまとめて .npz に変換する（API キーがないときの代わり）
  lab         研究室での 1 回ぶん（信号確認 → 安静 → 確認動作 → MVC → 長い記録）を通しで流す
  events      マウスの動きとクリックを時刻付きで記録する（M2-2。EMG なしで動く）
  events-plot 記録したマウスのイベントを図にし、報告レートなどを出す
  play        筋電とマウスを同時に記録し、KovaaK's の結果も取り込む（M2-2）。--obs で画面録画も
  kovaaks     記録の間に遊んだ KovaaK's の結果の CSV を kovaaks/ に取り込み、クリックと突き合わせる
              （events のあとにも自動で走る）
  visit       1 回の来室（M2-3）：lab の手順 → KovaaK's 5 回（筋電・マウス・画面録画・結果）
  pair        センサを 1 本ずつ、決めた番号（シールの番号）でペアリングし直す

--source sim を付けると疑似信号で動く（既定は delsys = 実機）。
"""

from __future__ import annotations

import argparse
import sys
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
        # "2026-10-22" のような名前だけなら data/raw/ の下、"../data/raw/..." のようなパスならそのまま
        return p.resolve() if p.is_absolute() or len(p.parts) > 1 or p.exists() else RAW_DIR / arg
    return RAW_DIR / datetime.now().strftime("%Y-%m-%d")


def _open(args):
    kw = {"realtime": True, "seed": args.seed, "n_channels": args.sim_channels} if args.source == "sim" else {"emg_only": not args.all_channels}
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
    view = None
    if args.live:
        from .plot import LiveView, parse_cues
        view = LiveView(src.channels, args.duration, parse_cues(args.cues))
        view.countdown(args.lead)
    rec = record(src, args.duration, args.task, on_update=view.update if view else None)
    if view:
        view.finish()
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


def cmd_long_stats(args):
    """上位 5% は 10-27 にその場で計算した値で、包絡線のどの段階で取ったかが残っていない。両方を並べて出す。"""
    import numpy as np
    from . import processing as proc
    out_dir = _session_dir(args.session)
    calib = Calibration.load(out_dir / "calibration.json")
    rec = Recording.load(out_dir / f"{args.name}.npz")
    print(f"{args.name}.npz を calibration.json の MVC で割った %MVC（安静は引かない）")
    print(f"  {'チャネル':<12}{'平均':>8}{'上位5%(包絡線)':>16}{'上位5%(0.5秒平均)':>18}{'最大(0.5秒平均)':>16}{'安静':>8}")
    for name in rec.emg_names:
        if name not in calib.mvc:
            continue
        fs, m = rec.fs(name), calib.mvc[name]
        env = proc.envelope(rec.data[name], fs) / m * 100
        avg = proc.moving_mean(env, fs, proc.MVC_WINDOW_S)
        print(f"  {name:<12}{env.mean():8.0f}{np.percentile(env, 95):16.0f}{np.percentile(avg, 95):18.0f}"
              f"{avg.max():16.0f}{calib.rest[name] / m * 100:8.0f}")
    print("上位 5%：大きい順に並べて上から 5% のところの値（3 分なら、これを超えていたのは合わせて約 9 秒）")


def cmd_import_csv(args):
    from .discover_csv import import_dir
    out_dir = _session_dir(args.session)
    saved = import_dir(out_dir, crop=not args.no_crop)
    print(f"{len(saved)} ファイルを変換: {out_dir}")


def cmd_plot(args):
    from .plot import plot_file
    plot_file(Path(args.file), out=Path(args.out) if args.out else None)


def cmd_events(args):
    from .events import plot_events, print_summary, record_events, summarize
    out_dir = _session_dir(args.session)
    name = args.name or datetime.now().strftime("events_%H%M%S")
    print(f"マウスを記録します（{args.duration:.0f} 秒。Ctrl+C で早めに止められます）")
    ev = record_events(args.duration)
    path = ev.save(out_dir / f"{name}.csv")
    print(f"  保存: {path}")
    print_summary(summarize(ev))
    plot_events(ev, path.with_suffix(".png"))
    if not args.no_kovaaks:
        _kovaaks(path, args.stats_dir, quiet_if_none=True)


def _kovaaks(events_csv: Path, stats_dir_arg: str | None, quiet_if_none: bool = False) -> None:
    """記録の間に遊んだ KovaaK's の CSV を kovaaks/ に取り込み、クリックと突き合わせる。"""
    from .events import Events
    from .kovaaks import align, find_stats_dir, import_runs, parse_stats, print_alignment
    stats_dir = find_stats_dir(stats_dir_arg)
    if stats_dir is None:
        if not quiet_if_none:
            print("KovaaK's の stats フォルダが見つかりません。--stats-dir で渡してください")
        return
    copied, warnings = import_runs(events_csv, stats_dir)
    if not copied and quiet_if_none:
        return  # KovaaK's を遊ばなかった記録
    print("KovaaK's の結果")
    ev = Events.load(events_csv)
    t0 = ev.meta["t0_unix"]
    for p in copied:
        run = parse_stats(p)
        print(f"  取り込み: {p}")
        print_alignment(run, t0, align(t0 + ev.clicks, run))
    for w in warnings:
        print(f"  [注意] {w}")


def cmd_kovaaks(args):
    _kovaaks(Path(args.file), args.stats_dir)


def _open_obs(on: bool):
    if not on:
        return None
    from .obs import ObsRecorder
    return ObsRecorder()  # 筋電につなぐ前に、OBS につながるかを確かめる


def _play_runs(src, out_dir: Path, base: str, runs: int, duration: float, task: str, obs,
               no_kovaaks: bool, stats_dir: str | None, numbered: bool = False) -> None:
    """KovaaK's を runs 回、筋電・マウス（と録画）を取りながら遊ぶ。回ごとに Enter を待つ。"""
    from .events import print_summary, summarize
    from .play import plot_play, record_play, save_play
    for k in range(1, runs + 1):
        name = f"{base}_{k:02d}" if numbered or runs > 1 else base
        if numbered or runs > 1:
            input(f"\nKovaaK's {k}/{runs} 回目。Enter で記録を始め、KovaaK's を前に出して遊ぶ > ")
        print(f"筋電とマウスを記録します（{duration:.0f} 秒）。始まったら KovaaK's を遊んでください")
        rec, ev = record_play(src, duration, task, obs=obs, video_dest=out_dir / name)
        emg_path, ev_path = save_play(rec, ev, out_dir, name)
        if obs is not None:
            print(f"  録画: {rec.meta['video']}（筋電の開始から {-rec.meta['video_offset_s'] * 1000:.0f} ms 前に開始）")
        print(f"  保存: {emg_path}")
        print(f"  保存: {ev_path}")
        print(f"  マウスの開始は筋電の開始から {rec.meta['mouse_offset_s'] * 1000:+.1f} ms")
        print_summary(summarize(ev))
        plot_play(rec, ev, emg_path.with_suffix(".png"))
        print(f"  図: {emg_path.with_suffix('.png')}")
        if not no_kovaaks:
            _kovaaks(ev_path, stats_dir, quiet_if_none=True)


def cmd_play(args):
    out_dir = _session_dir(args.session)
    obs = _open_obs(args.obs)
    src = _open(args)
    try:
        _play_runs(src, out_dir, args.name or datetime.now().strftime("play_%H%M%S"), args.runs, args.duration,
                   args.task, obs, args.no_kovaaks, args.stats_dir)
    finally:
        src.close()


def cmd_visit(args):
    """1 回の来室（M2-3）：lab の手順（信号確認 → 部位 → 安静 → 確認動作 → MVC）→ KovaaK's を runs 回。"""
    from .session import OTHER_TASKS, WRIST_TASKS, WRIST_TASKS_SOLO, build_steps, run_lab_session
    out_dir = _session_dir(args.session)
    obs = _open_obs(not args.no_obs)
    src = _open(args)
    tasks = list(WRIST_TASKS_SOLO if args.solo else WRIST_TASKS) + ([] if args.wrist_only else list(OTHER_TASKS))
    try:
        if not args.skip_lab:
            run_lab_session(src, out_dir, build_steps(tasks, args.rounds, args.rest_between, 0),
                            expect=args.expect, lead=5)
        _play_runs(src, out_dir, "kovaaks", args.runs, args.duration, "play", obs, False, args.stats_dir,
                   numbered=True)
    finally:
        src.close()
    print(f"\n保存先: {out_dir}")


def cmd_events_plot(args):
    from .events import Events, plot_events, print_summary, summarize
    ev = Events.load(Path(args.file))
    print_summary(summarize(ev))
    plot_events(ev, Path(args.out) if args.out else None)


def cmd_pair(args):
    from .sources import DelsysSource
    src = DelsysSource()
    for n in args.numbers:
        input(f"\nシール {n} のセンサを充電台に載せたまま Enter を押し、すぐ外す（{args.timeout:.0f} 秒待つ） > ")
        ok = src.pair(n, args.timeout)
        print(f"  シール {n} → 登録番号 {n}: " + ("できた" if ok else "できなかった（時間切れか失敗。もう一度流す）"))
    src.close()
    print("\n確認: python -m emgpipe devices で、番号がシールと同じになっているか見る")


def cmd_lab(args):
    from .session import OTHER_TASKS, WRIST_TASKS, WRIST_TASKS_SOLO, build_steps, run_lab_session
    src = _open(args)
    tasks = list(WRIST_TASKS_SOLO if args.solo else WRIST_TASKS) + ([] if args.wrist_only else list(OTHER_TASKS))
    steps = build_steps(tasks, args.rounds, args.rest_between, args.long)
    try:
        # クリックしてから姿勢を作る（天板の裏に手を入れる、座面を握る）ので長めに数える
        run_lab_session(src, _session_dir(args.session), steps, expect=args.expect, lead=5)
    finally:
        src.close()


def main(argv=None):
    # 画面でなくパイプに出すとき（Claude Code の `!` など）、Windows では cp932 で出て文字化けする。UTF-8 にそろえる
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="emgpipe")
    p.add_argument("--source", choices=["delsys", "sim"], default="delsys")
    p.add_argument("--seed", type=int, default=None, help="疑似信号の乱数シード")
    p.add_argument("--all-channels", action="store_true", help="EMG 以外（IMU など）も記録する")
    p.add_argument("--sim-channels", type=int, default=2, help="疑似信号のチャネル数")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("devices").set_defaults(func=cmd_devices)

    r = sub.add_parser("record")
    r.add_argument("--duration", type=float, default=30.0)
    r.add_argument("--session", help="セッション名か保存先ディレクトリ（既定は data/raw/<今日の日付>）")
    r.add_argument("--name", help="ファイル名（拡張子なし）")
    r.add_argument("--task", default="", help="記録のラベル")
    r.add_argument("--live", action="store_true", help="記録中に窓を開き、指示と直近の RMS を表示する")
    r.add_argument("--cues", default="", help='--live で出す指示。"0:脱力,5:反らす"（開始からの秒:指示）')
    r.add_argument("--lead", type=int, default=3, help="--live で開始前に数える秒数")
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

    ls = sub.add_parser("long-stats")
    ls.add_argument("--session", required=True)
    ls.add_argument("--name", default="long_free", help="長い記録のファイル名（拡張子なし）")
    ls.set_defaults(func=cmd_long_stats)

    ic = sub.add_parser("import-csv")
    ic.add_argument("session", help="CSV が入ったフォルダ（セッション名かパス）")
    ic.add_argument("--no-crop", action="store_true", help="マーカー区間で切り出さず、全体を残す")
    ic.set_defaults(func=cmd_import_csv)

    pl = sub.add_parser("plot")
    pl.add_argument("file")
    pl.add_argument("--out", help="画像に保存する場合のパス")
    pl.set_defaults(func=cmd_plot)

    ev = sub.add_parser("events")
    ev.add_argument("--duration", type=float, default=60.0, help="記録の長さ [s]")
    ev.add_argument("--session", help="既定は data/raw/<今日の日付>")
    ev.add_argument("--name", help="ファイル名（既定は events_<時刻>）")
    ev.add_argument("--no-kovaaks", action="store_true", help="記録のあとに KovaaK's の結果を取り込まない")
    ev.add_argument("--stats-dir", help="KovaaK's の stats フォルダ（既定は Steam の置き場所を探す）")
    ev.set_defaults(func=cmd_events)

    ep = sub.add_parser("events-plot")
    ep.add_argument("file", help="events で保存した .csv")
    ep.add_argument("--out", help="画像に保存する場合のパス")
    ep.set_defaults(func=cmd_events_plot)

    py = sub.add_parser("play")
    py.add_argument("--duration", type=float, default=90.0, help="記録の長さ [s]（KovaaK's の 1 回 60 秒 + 前後）")
    py.add_argument("--session", help="既定は data/raw/<今日の日付>")
    py.add_argument("--name", help="ファイル名（既定は play_<時刻>。.npz と .csv が同じ名前でできる）")
    py.add_argument("--task", default="play", help="記録のラベル")
    py.add_argument("--runs", type=int, default=1, help="続けて何回取るか（2 回以上なら <name>_01, _02, … になり、回ごとに Enter を待つ）")
    py.add_argument("--obs", action="store_true", help="OBS で画面録画も一緒に取る（OBS を起動し、WebSocket サーバーを有効にしておく）")
    py.add_argument("--no-kovaaks", action="store_true", help="記録のあとに KovaaK's の結果を取り込まない")
    py.add_argument("--stats-dir", help="KovaaK's の stats フォルダ（既定は Steam の置き場所を探す）")
    py.set_defaults(func=cmd_play)

    kv = sub.add_parser("kovaaks")
    kv.add_argument("file", help="events で保存した .csv")
    kv.add_argument("--stats-dir", help="KovaaK's の stats フォルダ（既定は Steam の置き場所を探す）")
    kv.set_defaults(func=cmd_kovaaks)

    pr = sub.add_parser("pair")
    pr.add_argument("numbers", type=int, nargs="+", help="登録する番号（シールの番号）。1 本ずつ順に")
    pr.add_argument("--timeout", type=float, default=60.0, help="1 本あたり待つ秒数")
    pr.set_defaults(func=cmd_pair)

    lb = sub.add_parser("lab")
    lb.add_argument("--session", help="既定は data/raw/<今日の日付>")
    lb.add_argument("--expect", type=int, default=6, help="付けたセンサの本数（足りなければ警告）")
    lb.add_argument("--rounds", type=int, default=2, help="MVC の課題を何周するか（1 周で全課題を 1 回ずつ）")
    lb.add_argument("--rest-between", type=float, default=10.0,
                    help="試行のあいだの休憩 [s]。課題を 1 周ずつ回すので、同じ筋は約 1 分空く")
    lb.add_argument("--wrist-only", action="store_true", help="MVC を手首の 2 課題だけにする")
    lb.add_argument("--long", type=float, default=180.0, help="長い記録の長さ [s]")
    lb.add_argument("--solo", action="store_true", help="手首を一人用（天板の裏を押し上げる）で取る。本番は押さえてもらう")
    lb.set_defaults(func=cmd_lab)

    vs = sub.add_parser("visit", help="1 回の来室：lab の手順 → KovaaK's を --runs 回（画面録画つき）")
    vs.add_argument("--session", help="既定は data/raw/<今日の日付>")
    vs.add_argument("--runs", type=int, default=5, help="KovaaK's を何回遊ぶか")
    vs.add_argument("--duration", type=float, default=90.0, help="KovaaK's 1 回ぶんの記録の長さ [s]")
    vs.add_argument("--expect", type=int, default=6, help="付けたセンサの本数（足りなければ警告）")
    vs.add_argument("--rounds", type=int, default=2, help="MVC の課題を何周するか")
    vs.add_argument("--rest-between", type=float, default=10.0, help="試行のあいだの休憩 [s]")
    vs.add_argument("--wrist-only", action="store_true", help="MVC を手首の 2 課題だけにする")
    vs.add_argument("--solo", action="store_true", help="手首を一人用で取る")
    vs.add_argument("--skip-lab", action="store_true", help="MVC までを飛ばして KovaaK's から始める（途中で止まったとき）")
    vs.add_argument("--no-obs", action="store_true", help="画面録画をしない")
    vs.add_argument("--stats-dir", help="KovaaK's の stats フォルダ（既定は Steam の置き場所を探す）")
    vs.set_defaults(func=cmd_visit)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
