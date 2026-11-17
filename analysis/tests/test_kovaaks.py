"""KovaaK's の CSV の読み込み・取り込み・突き合わせ。analysis/ で `python -m unittest discover tests`。"""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from emgpipe.kovaaks import align, import_runs, parse_stats  # noqa: E402

HEADER = "Kill #,Timestamp,Bot,Weapon,TTK,Shots,Hits,Accuracy,Damage Done,Damage Possible,Efficiency,Cheated,OverShots"


def write_stats(d: Path, end: str, start: str, kills: list[tuple[str, int]], pause: int = 0) -> Path:
    """end は "2026.11.17-17.25.15"、start と kills の時刻は "HH:MM:SS.mmm"。"""
    lines = [HEADER]
    for i, (t, shots) in enumerate(kills, 1):
        lines.append(f"{i},{t},target,BB Gun,0.0s,{shots},1,1,1,1,1,0,0")
    total = sum(s for _, s in kills)
    lines += ["", "Weapon,Shots,Hits,Damage Done,Damage Possible,,Sens Scale", f"BB Gun,{total},{len(kills)},1,1,",
              "", "Score:,123.4", f"Challenge Start:,{start}", f"Pause Count:,{pause}", "DPI:,1600", ""]
    p = d / f"test scen - Challenge - {end} Stats.csv"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


class KovaaksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.stats = self.tmp / "stats"
        self.stats.mkdir()

    def test_parse(self):
        p = write_stats(self.stats, "2026.11.17-17.25.15", "17:24:15.166",
                        [("17:24:16.587", 1), ("17:24:17.508", 3)])
        r = parse_stats(p)
        self.assertEqual(r.scenario, "test scen")
        self.assertEqual(r.total_shots, 4)
        self.assertEqual(list(r.shots_per_kill), [1, 3])
        self.assertAlmostEqual(r.kills[0] - r.start, 1.421, places=3)
        self.assertEqual(r.info["DPI"], "1600")

    def test_parse_across_midnight(self):
        p = write_stats(self.stats, "2026.11.18-00.00.30", "23:59:50.000",
                        [("23:59:55.000", 1), ("00:00:05.000", 1)])
        r = parse_stats(p)
        self.assertAlmostEqual(r.kills[1] - r.kills[0], 10.0, places=3)
        self.assertEqual(datetime.fromtimestamp(r.start).day, 17)

    def test_import_and_align(self):
        p = write_stats(self.stats, "2026.11.17-17.25.15", "17:24:15.000",
                        [("17:24:16.000", 1), ("17:24:18.000", 2)], pause=1)
        t0 = datetime(2026, 11, 17, 17, 24, 10).timestamp()
        session = self.tmp / "session"
        session.mkdir()
        ev = session / "ev.csv"
        ev.write_text("t_s,dx,dy,button,cursor_x,cursor_y,abs\n", encoding="utf-8")
        ev.with_suffix(".json").write_text(json.dumps({"t0_unix": t0, "duration_s": 70}), encoding="utf-8")
        before = p.read_bytes()

        copied, warnings = import_runs(ev, self.stats)
        self.assertEqual(len(copied), 1)
        self.assertEqual(copied[0].read_bytes(), before)
        self.assertEqual(p.read_bytes(), before)  # 元は変えない
        self.assertTrue(any("一時停止" in w for w in warnings))
        manifest = json.loads((session / "kovaaks" / "ev_import.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["runs"][0]["challenge_start_s"], 5.0)

        # 開始のクリック（4.9 s）は数えず、外し 1 回を含む 3 回を数える
        clicks = t0 + np.array([4.9, 5.997, 7.0, 7.996, 30.0])
        a = align(clicks, parse_stats(copied[0]))
        self.assertEqual(a["shots_csv"], 3)
        self.assertEqual(a["clicks_in_run"], 3)
        self.assertAlmostEqual(a["kill_minus_click_ms"]["max"], 4.0, places=1)

        # 2 回目は上書きしない
        copied2, _ = import_runs(ev, self.stats)
        self.assertEqual(copied2, copied)

    def test_runs_outside_recording_are_ignored(self):
        write_stats(self.stats, "2026.11.17-17.25.15", "17:24:15.000", [("17:24:16.000", 1)])
        session = self.tmp / "s2"
        session.mkdir()
        ev = session / "ev.csv"
        ev.write_text("t_s,dx,dy,button,cursor_x,cursor_y,abs\n", encoding="utf-8")
        t0 = datetime(2026, 11, 17, 18, 0, 0).timestamp()
        ev.with_suffix(".json").write_text(json.dumps({"t0_unix": t0, "duration_s": 70}), encoding="utf-8")
        copied, warnings = import_runs(ev, self.stats)
        self.assertEqual(copied, [])
        self.assertTrue(warnings)


if __name__ == "__main__":
    unittest.main()
