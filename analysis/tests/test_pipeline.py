"""疑似信号でパイプライン全体を通す。analysis/ で `python -m unittest discover tests`。"""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from emgpipe import processing as proc  # noqa: E402
from emgpipe.calibration import Calibration, ProtocolConfig, calibration_from_dir, normalize, run_protocol  # noqa: E402
from emgpipe.recording import Recording, record  # noqa: E402
from emgpipe.sources import SimulatedSource  # noqa: E402


class FastSim(SimulatedSource):
    def __init__(self, **kw):
        super().__init__(realtime=False, seed=0, **kw)


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_record_length_and_roundtrip(self):
        src = FastSim()
        rec = record(src, 2.0, "rest", progress=False)
        for c in src.channels:
            self.assertEqual(rec.data[c.name].size, int(round(c.fs * 2.0)))
        back = Recording.load(rec.save(self.tmp / "r.npz"))
        self.assertEqual(back.task, "rest")
        np.testing.assert_array_equal(back.data["S1_EMG1"], rec.data["S1_EMG1"])

    def test_envelope_tracks_amplitude(self):
        fs = 2000.0
        rng = np.random.default_rng(1)
        x = np.concatenate([0.1 * rng.standard_normal(4000), 1.0 * rng.standard_normal(4000)])
        env = proc.envelope(x, fs)
        ratio = env[5000:7000].mean() / env[500:3000].mean()
        self.assertAlmostEqual(ratio, 10.0, delta=1.5)

    def test_protocol_and_normalization(self):
        src = FastSim()
        cfg = ProtocolConfig(rest_s=4, trials=2, contraction_s=3, rest_between_s=0, countdown_s=0)
        calib = run_protocol(src, self.tmp, cfg, interactive=False)
        self.assertEqual(calib.warnings, [])
        # 伸筋側チャネルは伸展で、屈筋側は屈曲で最大になるはず
        self.assertTrue(calib.mvc_source["S1_EMG1"].startswith("wrist_extension"))
        self.assertTrue(calib.mvc_source["S2_EMG1"].startswith("wrist_flexion"))

        # ファイルから再計算しても同じ値になる
        again = calibration_from_dir(self.tmp)
        for n in calib.mvc:
            self.assertAlmostEqual(again.mvc[n], calib.mvc[n])

        # 伸展の記録を正規化すると、S1 のピークはおよそ 100 %MVC になる
        ext = Recording.load(self.tmp / "mvc_wrist_extension_1.npz")
        norm = normalize(ext, Calibration.load(self.tmp / "calibration.json"))
        peak = proc.moving_mean(norm.data["S1_EMG1.pct_mvc"], 1925.926, 0.5).max()
        self.assertGreater(peak, 85)
        self.assertLessEqual(peak, 100.5)

        # 電極ゲインが違っても、正規化後の安静レベルは同程度になる
        rest = normalize(Recording.load(self.tmp / "rest.npz"), calib)
        r1 = np.median(rest.data["S1_EMG1.pct_mvc_rest"][2000:-2000])
        self.assertLess(abs(r1), 2.0)

    def test_compare_tasks(self):
        from emgpipe.calibration import compare_tasks, save_comparison
        src = FastSim()
        cfg = ProtocolConfig(rest_s=4, trials=2, contraction_s=3, rest_between_s=0, countdown_s=0)
        run_protocol(src, self.tmp, cfg, interactive=False)
        # 確認動作として、伸展の 1 試行目をそのまま check_ にする → 伸展に対して 100% 以下
        Recording.load(self.tmp / "mvc_wrist_extension_1.npz").save(self.tmp / "check_free_extension_01.npz")

        rows = compare_tasks(self.tmp)
        s1 = [r for r in rows if r["channel"] == "S1_EMG1"]
        self.assertEqual(s1[0]["task"], "wrist_extension")
        self.assertEqual(len(s1[0]["trials"]), 2)
        self.assertEqual(s1[-1]["task"], "全課題")
        self.assertAlmostEqual(s1[-1]["mvc"], s1[0]["mvc"])
        self.assertLessEqual(s1[0]["check_pct_mvc"], 100.0 + 1e-9)
        # 屈曲は伸筋側にとって小さい MVC なので、同じ確認動作が 100% を超える
        flex = next(r for r in s1 if r["task"] == "wrist_flexion")
        self.assertGreater(flex["check_pct_mvc"], 100.0)
        self.assertTrue(save_comparison(rows, self.tmp / "mvc_compare.csv").exists())


def _write_discover_csv(path: Path, fs: float, x0: np.ndarray, x3: np.ndarray, markers: list[float]):
    """Trigno Discover 2.1.0.7 と同じ形の CSV を書く（センサ 0 と 3、EMG 各 1 チャネル）。"""
    head = [
        "Application:, Trigno Discover (2.1.0.7)",
        "Date/Time:, 2026/09/29 15:50:51",
        f"Collection Length (seconds):, {x0.size / fs}",
        "Avanti Sensor 0 (89542), , Avanti Sensor 3 (89563)",
        "sensor mode: 40, , sensor mode: 40",
        "EMG 1 Time Series (s), EMG 1 (mV), EMG 1 Time Series (s), EMG 1 (mV)",
        f", {fs} Hz, , {fs} Hz",
        f", {1 / fs} s, , {1 / fs} s, , Type, Name, Label, Time (s), , Pair",
    ]
    lines = []
    for i in range(x0.size):
        t = i / fs
        row = f"{t}, {x0[i]}, {t}, {x3[i]}, "
        if i < len(markers):
            row += f", General, E{i + 1}, E{i + 1}, {markers[i]}, , "
        lines.append(row)
    path.write_text("\n".join(head + lines) + "\n", encoding="utf-8")


class LabStepsTest(unittest.TestCase):
    def test_checks_cover_all_sites_before_mvc(self):
        from emgpipe import poses
        from emgpipe.session import CHECKS, OTHER_TASKS, WRIST_TASKS_SOLO, build_steps
        steps = build_steps(list(WRIST_TASKS_SOLO + OTHER_TASKS), 2, 10, 180)
        names = [s.name for s in steps]
        checks = [n for n in names if n.startswith("check_")]
        self.assertEqual(len(checks), 6)
        # 確認動作は、疲れる前（最初の MVC より前）に全部取る
        self.assertLess(names.index(checks[-1]), min(i for i, n in enumerate(names) if n.startswith("mvc_")))
        for task, *_ in CHECKS:
            self.assertIn(task, poses.DRAW)


class SiteCheckTest(unittest.TestCase):
    def test_swapped_sensors_are_flagged(self):
        from emgpipe.session import SITE_LEAD, SITE_MOVES, SITE_OFF, SITE_ON, check_sites, site_check_step
        from emgpipe.sources import ChannelInfo
        fs = 2000.0
        dur = site_check_step().duration
        rng = np.random.default_rng(0)
        sites = list(SITE_MOVES)
        chans, data = [], {}
        for k in range(6):
            name = f"S{k + 1}_EMG1"
            x = 0.002 * rng.standard_normal(int(dur * fs))
            t0 = SITE_LEAD + k * (SITE_ON + SITE_OFF)   # S(k+1) は k 番目の動作で強く反応する
            x[int(t0 * fs):int((t0 + SITE_ON) * fs)] *= 20
            chans.append(ChannelInfo(name, "EMG", fs, name))
            data[name] = x
        rec = Recording(chans, data)
        # sensors.json で S3 と S6 を取り違えた
        table = {f"S{k + 1}_EMG1": sites[k] for k in range(6)}
        table["S3_EMG1"], table["S6_EMG1"] = sites[5], sites[2]
        rows = {r["channel"]: r for r in check_sites(rec, table)}
        self.assertEqual([c for c, r in rows.items() if not r["ok"]], ["S3_EMG1", "S6_EMG1"])
        self.assertEqual(rows["S3_EMG1"]["best_site"], "三角筋中部")


class DiscoverCsvTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_read_crop_and_labels(self):
        from emgpipe.discover_csv import import_dir
        fs, n = 1000.0, 5000
        rng = np.random.default_rng(0)
        x0, x3 = 0.01 * rng.standard_normal(n), 0.02 * rng.standard_normal(n)
        _write_discover_csv(self.tmp / "rest.csv", fs, x0, x3, [1.0, 4.0])
        (self.tmp / "sensors.json").write_text('{"前腕の上（伸筋群）": 3, "前腕の下（屈筋群）": 0}', encoding="utf-8")

        import_dir(self.tmp)
        rec = Recording.load(self.tmp / "rest.npz")
        self.assertEqual(rec.emg_names, ["前腕の下（屈筋群）", "前腕の上（伸筋群）"])
        self.assertEqual(rec.fs("前腕の上（伸筋群）"), fs)
        # 1.0〜4.0 秒だけが残る（両端を含むので 3001 サンプル）
        up = rec.data["前腕の上（伸筋群）"]
        self.assertEqual(up.size, 3001)
        np.testing.assert_allclose(up, x3[1000:4001], rtol=1e-6)
        self.assertEqual([m["name"] for m in rec.meta["markers"]], ["E1", "E2"])


class TestEvents(unittest.TestCase):
    def test_roundtrip_and_summary(self):
        """マウスのイベントの保存・読み込みと、報告レートの見積もり（1 ms 間隔なら約 1000 Hz）。"""
        from emgpipe.events import Events, summarize
        n = 500
        t = np.arange(n) * 0.001
        btn = [""] * n
        btn[100], btn[150] = "L_down", "L_up"
        ev = Events(t, np.ones(n, dtype=int), np.zeros(n, dtype=int), btn, np.zeros((n, 2), dtype=int),
                    {"clock": "time.perf_counter"})
        with tempfile.TemporaryDirectory() as d:
            back = Events.load(ev.save(Path(d) / "ev.csv"))
        self.assertEqual(back.button[100], "L_down")
        self.assertEqual(back.meta["clock"], "time.perf_counter")
        self.assertTrue(np.allclose(back.t, t, atol=1e-6))
        self.assertEqual(back.path[-1, 0], n)
        s = summarize(back)
        self.assertEqual(s["n_left_clicks"], 1)
        self.assertLess(abs(s["rate_hz"] - 1000), 1)


@unittest.skipUnless(sys.platform == "win32", "マウスの記録は Windows だけ")
class TestPlay(unittest.TestCase):
    def test_record_play_saves_both_with_offset(self):
        """筋電とマウスを同時に取り、同じ名前の .npz と .csv に残す。マウスの開始時刻のずれが残る。"""
        from emgpipe.events import Events
        from emgpipe.play import record_play, save_play
        src = SimulatedSource(realtime=True, seed=0)
        src.connect()
        rec, ev = record_play(src, 1.0)
        self.assertEqual(rec.data["S1_EMG1"].size, int(round(src.channels[0].fs * 1.0)))
        self.assertLess(abs(rec.meta["mouse_offset_s"]), 0.5)
        self.assertGreater(ev.meta["duration_s"], 0.9)
        with tempfile.TemporaryDirectory() as d:
            npz, csv = save_play(rec, ev, Path(d), "p")
            self.assertEqual(npz.stem, csv.stem)
            self.assertIn("t0_perf_counter", Recording.load(npz).meta)
            self.assertIn("emg_t0_perf_counter", Events.load(csv).meta)

    def test_record_play_with_obs(self):
        """OBS の代わりの偽物で、録画 → 筋電 → 止める の順と、録画ファイルが記録と同じ名前で動くことを確かめる。"""
        from types import SimpleNamespace
        from emgpipe.obs import ObsRecorder
        from emgpipe.play import record_play
        d = Path(tempfile.mkdtemp())
        raw = d / "obs_out.mkv"

        class FakeObs:
            active = False
            def get_record_status(self):
                return SimpleNamespace(output_active=self.active)
            def start_record(self):
                self.active = True
            def stop_record(self):
                self.active = False
                raw.write_bytes(b"x")
                return SimpleNamespace(output_path=str(raw))

        src = SimulatedSource(realtime=True, seed=0)
        src.connect()
        rec, _ = record_play(src, 0.5, obs=ObsRecorder(FakeObs()), video_dest=d / "sess" / "p_01")
        self.assertEqual(rec.meta["video"], "p_01.mkv")
        self.assertTrue((d / "sess" / "p_01.mkv").exists())
        self.assertLess(rec.meta["video_offset_s"], 0)  # 録画は筋電より前に始まる


if __name__ == "__main__":
    unittest.main()

