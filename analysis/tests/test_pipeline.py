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


if __name__ == "__main__":
    unittest.main()
