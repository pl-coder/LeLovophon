"""Checks for the FreeCAD-free Lovophon model.

Run from the repository root:  python3 -m unittest discover -s sim/tests
"""
import csv
import math
import struct
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sim.lovophon import model, midi  # noqa: E402

RATIOS = ["1", "9/8", "5/4", "3/2", "5/3", "2", "9/4", "5/2", "3", "10/3", "4", "9/2"]
OLD_CSV = ROOT / "outputs" / "Lovophone_160min_Pluck_Times.csv"


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.design = model.load_design()

    def test_snapshot_matches_freecad_file(self):
        self.assertEqual(self.design["voices"], model.read_fcstd_rows(model.FCSTD))

    def test_twelve_voices_with_exact_ratios(self):
        voices = self.design["voices"]
        self.assertEqual(len(voices), 12)
        for row, ratio in zip(voices, map(Fraction, RATIOS)):
            self.assertEqual(Fraction(row["ratio_exact"]), ratio)
            self.assertEqual(Fraction(row["pitch_ratio_exact"]), ratio)
            self.assertEqual(Fraction(row["driver_teeth"], row["driven_teeth"]), ratio)
            self.assertAlmostEqual(row["speaking_length"] * float(ratio), 330.0, places=8)
            self.assertAlmostEqual(row["radius"] * float(ratio), voices[0]["radius"], places=8)
            self.assertAlmostEqual(row["frequency_hz"], midi.C3_HZ * float(ratio), places=9)

    def test_repeat_is_480_seconds_at_3_rpm(self):
        self.assertEqual(model.repeat_seconds(self.design, 3.0), 480.0)
        self.assertEqual(model.repeat_seconds(self.design, 6.0), 240.0)


class KinematicsTests(unittest.TestCase):
    def setUp(self):
        self.design = model.load_design()
        self.voices = self.design["voices"]

    def test_two_crossings_per_cam_revolution(self):
        for row in self.voices:
            phases = model.pluck_phases(row)
            self.assertEqual(len(phases), 2, row["display_note"])
            for x in phases:
                self.assertAlmostEqual(model.wrap_angle(model.beta(row, -x) - row["beta_mid"]), 0.0, places=12)

    def test_voice_c_matches_pauls_published_pluck_times(self):
        """Voice C kept its follower geometry through the ratio correction, so
        its two crossings must land where the archived 160-minute CSV says."""
        with OLD_CSV.open() as f:
            old = [float(r["seconds"]) for r in csv.DictReader(f) if r["string"] == "C"]
        c_row = self.voices[0]
        phases = model.pluck_phases(c_row)
        period = model.cam_period_seconds(c_row, 3.0)
        expected = sorted(x / (2 * math.pi) * period for x in phases)
        self.assertAlmostEqual(expected[0], old[0], places=8)
        self.assertAlmostEqual(expected[1], old[1], places=8)
        self.assertAlmostEqual(expected[0] + period, old[2], places=8)

    def test_pluck_count_is_two_per_cam_revolution(self):
        events = model.pluck_events(self.design, 480.0, 3.0)
        for index, row in enumerate(self.voices):
            n = sum(1 for e in events if e["index"] == index)
            self.assertEqual(n, 2 * 24 * Fraction(row["ratio_exact"]), row["display_note"])

    def test_schedule_repeats_after_480_seconds(self):
        events = model.pluck_events(self.design, 960.0, 3.0)
        first = [(e["index"], e["crossing"], e["time"]) for e in events if e["time"] < 480.0]
        second = [(e["index"], e["crossing"], e["time"] - 480.0) for e in events if e["time"] >= 480.0]
        self.assertEqual(len(first), len(second))
        for a, b in zip(first, second):
            self.assertEqual(a[:2], b[:2])
            self.assertAlmostEqual(a[2], b[2], places=6)

    def test_rpm_scales_time_linearly(self):
        slow = model.pluck_events(self.design, 480.0, 3.0)
        fast = model.pluck_events(self.design, 240.0, 6.0)
        self.assertEqual(len(slow), len(fast))
        for a, b in zip(slow, fast):
            self.assertAlmostEqual(a["time"], 2 * b["time"], places=9)

    def test_poses_match_macro_conventions(self):
        row = self.voices[0]
        p0 = model.poses(row, 0.0)
        self.assertEqual(p0["Driver"]["position"], (row["station"], -83.0, -131.0))
        self.assertEqual(p0["Driver"]["angle_deg"], 0.0)
        self.assertEqual(p0["Output"]["angle_deg"], 0.0)
        p1 = model.poses(row, 1.0)
        self.assertAlmostEqual(p1["Driver"]["angle_deg"], -18.0)
        self.assertAlmostEqual(p1["Output"]["angle_deg"], -18.0 * row["ratio"])
        swing = max(abs(model.arm_swing_deg(row, t / 10)) for t in range(201))
        self.assertAlmostEqual(swing, row["swing_half_angle_deg"], delta=0.05)

    def test_tuning_override_changes_frequency_not_timing(self):
        base = model.pluck_events(self.design, 60.0)
        tuned = model.pluck_events(self.design, 60.0, tunings={"C3": 128.0})
        for a, b in zip(base, tuned):
            self.assertEqual(a["time"], b["time"])
            if a["voice"] == "C3":
                self.assertEqual(b["frequency_hz"], 128.0)
            else:
                self.assertEqual(a["frequency_hz"], b["frequency_hz"])


class MidiTests(unittest.TestCase):
    def test_midi_is_well_formed_and_balanced(self):
        design = model.load_design()
        events = model.pluck_events(design, 480.0, 3.0)
        data = midi.build_midi(design, events, 480.0, 3.0)
        self.assertEqual(data[:4], b"MThd")
        length, fmt, ntracks, ppq = struct.unpack(">IHHH", data[4:14])
        self.assertEqual((length, fmt, ntracks, ppq), (6, 1, 13, 960))
        i, note_ons = 14, 0
        for _ in range(ntracks):
            self.assertEqual(data[i:i + 4], b"MTrk")
            size = struct.unpack(">I", data[i + 4:i + 8])[0]
            i += 8
            end = i + size
            t, active = 0, set()
            while i < end:
                dt, i = self._vlq(data, i)
                t += dt
                status = data[i]
                i += 1
                if status == 255:
                    kind = data[i]
                    i += 1
                    ln, i = self._vlq(data, i)
                    i += ln
                    if kind == 0x2F:
                        self.assertEqual(i, end)
                else:
                    n = 1 if status & 0xF0 in (0xC0, 0xD0) else 2
                    vals = data[i:i + n]
                    i += n
                    key = (status & 15, vals[0])
                    if status & 0xF0 == 0x90 and vals[1] > 0:
                        self.assertNotIn(key, active)
                        active.add(key)
                        note_ons += 1
                    elif status & 0xF0 == 0x80:
                        active.remove(key)
            self.assertFalse(active)
            self.assertEqual(t, round(480 * midi.TICKS_PER_SECOND))
        self.assertEqual(i, len(data))
        self.assertEqual(note_ons, len(events))

    @staticmethod
    def _vlq(b, i):
        n = 0
        for _ in range(4):
            x = b[i]
            i += 1
            n = (n << 7) | (x & 127)
            if not x & 128:
                return n, i
        raise AssertionError("VLQ too long")

    def test_tuning_override_reaches_midi_even_without_events(self):
        design = model.load_design()
        events = model.pluck_events(design, 0.1, tunings={"C3": 128.0})
        self.assertFalse(any(e["voice"] == "C3" for e in events))
        data = midi.build_midi(design, events, 0.1, 3.0, tunings={"C3": 128.0})
        self.assertIn(b"Pitch 128.000000000 Hz", data)

    def test_pitch_bend_for_just_ratios(self):
        bend, cents = midi.pitch_bend_14bit(midi.C3_HZ * 5 / 4, 52)  # E3 just vs ET
        self.assertAlmostEqual(cents, -13.686286, places=5)
        self.assertEqual(bend, 8192 + round(-13.686286 / 200 * 8192))


if __name__ == "__main__":
    unittest.main()
