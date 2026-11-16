"""Checks for the Plucking Layout R5 model.

Run from the repository root:  python3 -m unittest discover -s sim/tests
"""
import csv
import hashlib
import math
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sim.lovophon import r5  # noqa: E402

PAIRS = [(36, 36), (36, 32), (40, 32), (48, 32), (40, 24), (48, 24), (54, 24), (60, 24), (60, 20), (80, 24), (80, 20), (90, 20)]
PICKS = [-129, -79, -39, 21, 51, 96, 122, 150, 190, 216, 242, 268]
PAUL_CSV = ROOT / "outputs" / "LeLovophon_Direct_Gear_Prototype" / "Axle_Clearance_Revision" / "Sound" / "LeLovophon_8min_Pluck_Times.csv"


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.design = r5.load_design()
        self.voices = self.design["voices"]

    def test_snapshot_matches_pauls_kinematics(self):
        self.assertEqual(self.design["source_sha256"], hashlib.sha256(r5.KINEMATICS_JSON.read_bytes()).hexdigest())
        self.assertEqual(r5.make_snapshot()["voices"], self.voices)
        if r5.FCSTD.exists():
            self.assertEqual(self.design["fcstd_sha256"], hashlib.sha256(r5.FCSTD.read_bytes()).hexdigest())

    def test_rows_follow_the_formulas(self):
        # work/direct_gear_math.py recomputed: pivots, crank centres, swing
        # midpoints and phases agree with Paul's committed rows.
        for i, (row, pair, pick) in enumerate(zip(self.voices, PAIRS, PICKS)):
            ratio = Fraction(row["ratio_exact"])
            self.assertEqual(Fraction(*pair), ratio)
            derived = r5.derive_row(i, ratio, pair, pick)
            for key in ("pivot_yz", "crank_yz"):
                for a, b in zip(derived[key], row[key]):
                    self.assertAlmostEqual(a, b, places=9)
            for key in ("ground_mm", "arm_radius_mm", "rocker_mid_rad", "phase_rad", "half_swing_deg", "bridge_x"):
                self.assertAlmostEqual(derived[key], row[key], places=7, msg=key)
            self.assertEqual(row["pick_x"], pick)
            self.assertAlmostEqual(row["speaking_length"], 600 / ratio)
            self.assertAlmostEqual(row["frequency_hz"], r5.C3_HZ * ratio)

    def test_saved_pose_is_the_shared_centre_crossing(self):
        for row in self.voices:
            p = r5.poses(row, 0.0)
            for kind in r5.POSE_KINDS:
                self.assertAlmostEqual(p[kind]["angle_deg"], 0.0, places=9)
            self.assertAlmostEqual(p["Coupler"]["dy"], 0.0)
            self.assertAlmostEqual(p["Coupler"]["dz"], 0.0)
            self.assertAlmostEqual(r5.angle(row, row["phase_rad"]), 0.0, places=9)

    def test_input_turns_the_same_for_every_voice(self):
        for t in (1.0, 7.5, 20.0, 123.4):
            angles = {round(r5.poses(row, t)["Input"]["angle_deg"], 9) for row in self.voices}
            self.assertEqual(len(angles), 1)
            self.assertAlmostEqual(angles.pop(), -360.0 * t / 20.0, places=9)

    def test_rocker_swing_within_half_swing(self):
        for row in self.voices:
            worst = max(abs(r5.angle(row, row["phase_rad"] + k * 2 * math.pi / 720)) for k in range(720))
            self.assertLess(math.degrees(worst), row["half_swing_deg"] + 1e-6)
            self.assertGreater(math.degrees(worst), row["half_swing_deg"] - 0.5)

    def test_coupler_keeps_its_length(self):
        for row in self.voices:
            for k in range(0, 360, 15):
                a, b, _ = r5.linkage(row, row["phase_rad"] + math.radians(k))
                self.assertAlmostEqual(math.dist(a, b), row["coupler_mm"], places=6)


class PluckTests(unittest.TestCase):
    def setUp(self):
        self.design = r5.load_design()

    def test_every_event_matches_pauls_list(self):
        rows = list(csv.DictReader(PAUL_CSV.open()))
        theirs = sorted((float(r["mechanism_seconds"]), int(r["string"]) - 1, 1 if r["direction"] == "outward" else 2) for r in rows)
        ours = sorted((e["time"], e["index"], e["crossing"]) for e in r5.pluck_events(self.design))
        self.assertEqual(len(ours), len(theirs))
        self.assertEqual(len(ours), 1350)
        for a, b in zip(ours, theirs):
            self.assertAlmostEqual(a[0], b[0], places=9)
            self.assertEqual(a[1:], b[1:])

    def test_return_crossing_is_a_falling_zero(self):
        for row in self.design["voices"]:
            frac = r5.return_fraction(row)
            self.assertGreater(frac, 0.0)
            self.assertLess(frac, 1.0)
            self.assertAlmostEqual(r5.angle(row, row["phase_rad"] + frac * 2 * math.pi), 0.0, places=9)
            self.assertLess(r5.angle(row, row["phase_rad"] + (frac + 0.01) * 2 * math.pi), 0.0)

    def test_repeat_and_rpm(self):
        self.assertEqual(r5.repeat_seconds(self.design), 480.0)
        self.assertEqual(r5.repeat_seconds(self.design, rpm=6.0), 240.0)
        slow = r5.pluck_events(self.design, 480.0)
        fast = r5.pluck_events(self.design, 240.0, rpm=6.0)
        self.assertEqual(len(slow), len(fast))
        for a, b in zip(slow, fast):
            self.assertAlmostEqual(a["time"], 2 * b["time"], places=9)

    def test_windowed_events_and_flat_layout(self):
        whole = [e for e in r5.pluck_events(self.design, 480.0) if 100.0 <= e["time"] < 160.0]
        window = r5.pluck_events(self.design, 160.0, start=100.0)
        self.assertEqual([(e["time"], e["index"]) for e in whole], [(e["time"], e["index"]) for e in window])
        flat = r5.events_flat(self.design, 100.0, 160.0)
        self.assertEqual(len(flat), 3 * len(window))
        poses = r5.poses_flat(self.design, 12.5)
        self.assertEqual(len(poses), 12 * 6)
        p = r5.poses(self.design["voices"][3], 12.5)
        self.assertAlmostEqual(poses[3 * 6 + 2], p["Rocker"]["angle_deg"])


if __name__ == "__main__":
    unittest.main()
