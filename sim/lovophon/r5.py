"""Plucking Layout R5 without FreeCAD: poses and pluck times.

Paul's current design (``outputs/LeLovophon_Pluck_Layout_R5/``) drives each
voice from the common input shaft through one external spur-gear pair to a
crank, a pushrod and a rocker that carries the pendulum arm and pick. The
closure below is his ``work/direct_gear_math.py`` ``linkage``/``angle`` pair,
ported line for line, and the per-voice rows are a snapshot of his committed
``Drive_Effort/Reproduction/kinematics.json`` (R5 only moves whole stations
along X; the linkage, phases and rocker midpoints are the direct-gear ones).

Conventions, all in the CAD's native frame (X along the strings, Y up, Z
across the lanes; rotations about +X, angles in the YZ plane from +Y toward
+Z):

- Crank angle ``theta = phase_rad + 2*pi * (rpm/60) * t * ratio``. The saved
  CAD pose is ``theta = phase_rad`` for every voice: the shared centre crossing
  at ``t = 0``.
- Input shaft turns ``-(theta - phase) / ratio`` about ``drive_yz`` (external
  mesh, so opposite to the crank); the same ``-2*pi*(rpm/60)*t`` for all.
- Rocker and pendulum turn ``angle(row, theta)`` about ``pivot_yz``: the rocker
  angle relative to its swing midpoint, wrapped to (-pi, pi].
- The coupler (pushrod) is carried by the crank pin ``a`` and turned by the
  change of its own bearing ``atan2(b - a)``.
- A pluck is a centre crossing, ``angle == 0``: outward (rising) at
  ``k * period`` and return (falling) at ``k * period + delta``, with ``delta``
  found once per voice by bisection. This is the convention of Paul's
  ``work/make_direct_gear_sound.py`` and his 1350-row event list.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from .model import DEFAULT_INPUT_RPM, TWO_PI

C3_HZ = 440.0 * 2 ** (-21 / 12)  # 130.8127826502993, as in Paul's event list

REPO_ROOT = Path(__file__).resolve().parents[2]
R5_DIR = REPO_ROOT / "outputs" / "LeLovophon_Pluck_Layout_R5"
FCSTD = R5_DIR / "LeLovophon_Pluck_Layout_R5.FCStd"
KINEMATICS_JSON = R5_DIR / "Drive_Effort" / "Reproduction" / "kinematics.json"
DESIGN_JSON = Path(__file__).with_name("r5_design.json")

# Constants shared by every voice (work/direct_gear_math.py line 8 and
# work/protokoto_r3/config.py): crank and rocker radii, the input axis, the
# speaking nut, and the lane pitch.
CRANK_MM = 10.0
ROCKER_MM = 14.0
GEAR_MODULE = 0.5
DRIVE_YZ = (65.0, -25.0)
NUT_X = 321.0
BASS_SPEAKING_MM = 600.0
LANE_PITCH_MM = 14.0
FIRST_LANE_Z = -102.0
ARM_BASS_MM = 109.0
PIVOT_Y_OFFSET = -91.0  # pivot y = -91 + arm radius, so the pick tip meets the string line
POSE_KINDS = ("Input", "Crank", "Rocker", "Coupler")


# --------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------

def read_kinematics(path: Path = KINEMATICS_JSON) -> dict:
    return json.loads(path.read_text())


def derive_row(index: int, ratio: Fraction, pair: tuple[int, int], pick_x: float) -> dict:
    """Recompute one voice from the formulas, for checking the snapshot."""
    radius = ARM_BASS_MM / float(ratio)
    pivot = (PIVOT_Y_OFFSET + radius, FIRST_LANE_Z + LANE_PITCH_MM * index)
    centre = GEAR_MODULE * sum(pair) / 2
    pd = math.dist(pivot, DRIVE_YZ)
    crank = tuple(DRIVE_YZ[k] + centre * (pivot[k] - DRIVE_YZ[k]) / pd for k in range(2))
    ground = math.dist(pivot, crank)
    row = {"pivot_yz": list(pivot), "crank_yz": list(crank), "ground_mm": ground, "coupler_mm": ground, "arm_radius_mm": radius}
    vals = [linkage(row, j * TWO_PI / 10000)[2] for j in range(10001)]
    ref = vals[0]
    vals = [ref + math.atan2(math.sin(v - ref), math.cos(v - ref)) for v in vals]
    row["rocker_mid_rad"] = (min(vals) + max(vals)) / 2
    row["half_swing_deg"] = math.degrees((max(vals) - min(vals)) / 2)

    def f(t):
        return angle(row, t)

    for j in range(10000):
        lo = j * TWO_PI / 10000
        hi = (j + 1) * TWO_PI / 10000
        if f(lo) <= 0 < f(hi):
            for _ in range(50):
                m = (lo + hi) / 2
                if f(m) > 0:
                    hi = m
                else:
                    lo = m
            row["phase_rad"] = (lo + hi) / 2
            break
    row["pick_x"] = pick_x
    row["bridge_x"] = NUT_X - BASS_SPEAKING_MM / float(ratio)
    return row


def make_snapshot(kinematics_path: Path = KINEMATICS_JSON, fcstd_path: Path = FCSTD) -> dict:
    """The twelve rows as the page and the tests use them."""
    kin = read_kinematics(kinematics_path)
    voices = []
    for row in kin["voices"]:
        ratio = Fraction(row["ratio"])
        length = NUT_X - row["bridge_x"]
        voices.append(
            {
                "index": row["index"],
                "note": f"V{row['index']:02d}",
                "display_note": row["note"],
                "ratio": float(ratio),
                "ratio_exact": row["ratio"],
                "driver_teeth": row["driver_teeth"],
                "driven_teeth": row["driven_teeth"],
                "station_x": row["station_x"],
                "pick_x": row["pick_x"],
                "bridge_x": row["bridge_x"],
                "speaking_length": length,
                "lane_z": row["pivot_yz"][1],
                "frequency_hz": C3_HZ * float(ratio),
                "pivot_yz": row["pivot_yz"],
                "crank_yz": row["crank_yz"],
                "ground_mm": row["ground_mm"],
                "coupler_mm": row["coupler_mm"],
                "arm_radius_mm": row["arm_radius_mm"],
                "rocker_mid_rad": row["rocker_mid_rad"],
                "half_swing_deg": row["half_swing_deg"],
                "phase_rad": row["phase_rad"],
            }
        )
    return {
        "design": "Plucking Layout R5",
        "source": str(kinematics_path.relative_to(REPO_ROOT)),
        "source_sha256": hashlib.sha256(kinematics_path.read_bytes()).hexdigest(),
        "fcstd": str(fcstd_path.relative_to(REPO_ROOT)),
        "fcstd_sha256": hashlib.sha256(fcstd_path.read_bytes()).hexdigest() if fcstd_path.exists() else None,
        "drive_yz": kin["drive_yz"],
        "shared_geometry_mm": {"crank": CRANK_MM, "rocker": ROCKER_MM, "nut_x": NUT_X, "lane_pitch": LANE_PITCH_MM},
        "input_rpm": DEFAULT_INPUT_RPM,
        "voices": voices,
    }


def load_design(path: Path = DESIGN_JSON) -> dict:
    return json.loads(path.read_text())


# --------------------------------------------------------------------------
# Kinematics (work/direct_gear_math.py, ported)
# --------------------------------------------------------------------------

def linkage(row: dict, t: float) -> tuple[tuple[float, float], tuple[float, float], float]:
    """Crank pin ``a``, rocker pin ``b`` and raw rocker angle at crank angle ``t``."""
    q = row["crank_yz"]
    o = row["pivot_yz"]
    l = row["ground_mm"]
    a = (q[0] + CRANK_MM * math.cos(t), q[1] + CRANK_MM * math.sin(t))
    dx = a[0] - o[0]
    dy = a[1] - o[1]
    d = math.hypot(dx, dy)
    v = (ROCKER_MM * ROCKER_MM - l * l + d * d) / (2 * d)
    h = math.sqrt(max(0.0, ROCKER_MM * ROCKER_MM - v * v))
    ux = dx / d
    uy = dy / d
    b = (o[0] + v * ux - h * uy, o[1] + v * uy + h * ux)
    return a, b, math.atan2(b[1] - o[1], b[0] - o[0])


def angle(row: dict, t: float) -> float:
    """Rocker angle relative to its swing midpoint, wrapped to (-pi, pi]."""
    beta = linkage(row, t)[2] - row["rocker_mid_rad"]
    return math.atan2(math.sin(beta), math.cos(beta))


def crank_angle(row: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> float:
    return row["phase_rad"] + TWO_PI * (rpm / 60.0) * t * row["ratio"]


def crank_period_seconds(row: dict, rpm: float = DEFAULT_INPUT_RPM) -> float:
    return (60.0 / rpm) / row["ratio"]


def repeat_seconds(design: dict, rpm: float = DEFAULT_INPUT_RPM) -> float:
    """24 input turns: the least common multiple of the ratio denominators."""
    turns = 1
    for row in design["voices"]:
        turns = math.lcm(turns, Fraction(row["ratio_exact"]).denominator)
    return turns * 60.0 / rpm


def poses(row: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> dict:
    """Rigid motions of the four moving groups of one voice at time ``t``.

    Angles in degrees about +X. ``Input``, ``Crank`` and ``Rocker`` rotate about
    ``drive_yz``, ``crank_yz`` and ``pivot_yz``; ``Coupler`` rotates about its
    saved-pose crank pin ``a0`` and then translates by ``a - a0`` (mm).
    """
    theta = crank_angle(row, t, rpm)
    delta = theta - row["phase_rad"]
    a0, b0, _ = linkage(row, row["phase_rad"])
    a, b, _ = linkage(row, theta)
    th0 = math.atan2(b0[1] - a0[1], b0[0] - a0[0])
    th = math.atan2(b[1] - a[1], b[0] - a[0])
    return {
        "Input": {"angle_deg": -math.degrees(delta) / row["ratio"]},
        "Crank": {"angle_deg": math.degrees(delta)},
        "Rocker": {"angle_deg": math.degrees(angle(row, theta))},
        "Coupler": {"angle_deg": math.degrees(th - th0), "dy": a[0] - a0[0], "dz": a[1] - a0[1]},
    }


def coupler_anchor(row: dict) -> tuple[float, float]:
    """The crank pin at the saved pose, ``a0``: the coupler's rotation centre."""
    return linkage(row, row["phase_rad"])[0]


# --------------------------------------------------------------------------
# Plucks
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _return_fraction(pivot_yz: tuple, crank_yz: tuple, ground_mm: float, mid: float, phase: float) -> float:
    """Fraction of the crank cycle from the outward crossing to the return one."""
    row = {"pivot_yz": pivot_yz, "crank_yz": crank_yz, "ground_mm": ground_mm, "rocker_mid_rad": mid}

    def f(x):
        return angle(row, phase + x)

    n = 10000
    for j in range(n):
        lo = j * TWO_PI / n
        hi = (j + 1) * TWO_PI / n
        if lo == 0.0:
            continue
        if f(lo) >= 0 > f(hi):
            for _ in range(60):
                m = (lo + hi) / 2
                if f(m) >= 0:
                    lo = m
                else:
                    hi = m
            return (lo + hi) / 2 / TWO_PI
    raise ValueError("no return crossing found")


def return_fraction(row: dict) -> float:
    return _return_fraction(tuple(row["pivot_yz"]), tuple(row["crank_yz"]), row["ground_mm"], row["rocker_mid_rad"], row["phase_rad"])


def pluck_events(design: dict, duration: float | None = None, rpm: float = DEFAULT_INPUT_RPM, start: float = 0.0) -> list[dict]:
    """Every pluck in ``[start, duration)``, sorted; same shape as ``model.pluck_events``.

    ``crossing`` is 1 for the outward crossing, 2 for the return.
    """
    if duration is None:
        duration = repeat_seconds(design, rpm)
    events = []
    for index, row in enumerate(design["voices"]):
        period = crank_period_seconds(row, rpm)
        phases = (0.0, return_fraction(row))
        first = max(0, math.floor(start / period) - 1)
        for k in range(first, math.ceil(duration / period) + 1):
            for crossing, frac in enumerate(phases, start=1):
                t = (k + frac) * period
                if start <= t < duration:
                    events.append({"time": t, "voice": row["display_note"], "index": index, "frequency_hz": row["frequency_hz"], "crossing": crossing, "crank_revolution": k})
    events.sort(key=lambda e: (e["time"], e["index"]))
    return events


# --------------------------------------------------------------------------
# Flat helpers for the page
# --------------------------------------------------------------------------

def poses_flat(design: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> list[float]:
    """Per voice: ``[input_deg, crank_deg, rocker_deg, coupler_deg, coupler_dy, coupler_dz]``."""
    out = []
    for row in design["voices"]:
        p = poses(row, t, rpm)
        out.extend((p["Input"]["angle_deg"], p["Crank"]["angle_deg"], p["Rocker"]["angle_deg"], p["Coupler"]["angle_deg"], p["Coupler"]["dy"], p["Coupler"]["dz"]))
    return out


def events_flat(design: dict, t0: float, t1: float, rpm: float = DEFAULT_INPUT_RPM) -> list[float]:
    out = []
    for e in pluck_events(design, t1, rpm, start=t0):
        out.extend((e["time"], float(e["index"]), float(e["crossing"])))
    return out
