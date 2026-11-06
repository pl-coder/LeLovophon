"""FreeCAD-free model of the Le Lovophon Lab Frame Ratio Review.

The twelve-voice geometry is the ``Motion.LinkageGeometry`` property of
``outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd``. The kinematics are a
line-for-line port of ``harpe_live_beta`` and ``harpe_live_roots`` in
``outputs/Animate_Lovophone_Lab_Ratio_Review.FCMacro``. The pluck convention
is the one used by ``work/make_lovophone_midi.py``: a voice plucks each time
its follower angle crosses ``beta_mid``, which happens twice per cam
revolution.

Everything here is ideal kinematics. It does not model belt ripple, pick
compliance, string acoustics or motor regulation, and it proves nothing about
a physical machine.
"""
from __future__ import annotations

import json
import math
import zipfile
import xml.etree.ElementTree as ET
from fractions import Fraction
from functools import reduce
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
DESIGN_JSON = PACKAGE_DIR / "design.json"
FCSTD = REPO_ROOT / "outputs" / "Lovophone_Lab_Frame_Ratio_Review.FCStd"

# Fixed geometry shared by all twelve voices, as hard-coded in the macro.
CAM_CENTRE_Y = -59.0
CAM_CENTRE_Z = -116.0
CAM_ECCENTRICITY_MM = 4.0
CAM_RADIUS_MM = 12.0
ROLLER_RADIUS_MM = 3.0
CONTACT_DISTANCE_MM = CAM_RADIUS_MM + ROLLER_RADIUS_MM
DRIVER_AXIS_Y = -83.0
DRIVER_AXIS_Z = -131.0
DEFAULT_INPUT_RPM = 3.0
TWO_PI = 2.0 * math.pi

POSE_KINDS = ("Driver", "Output", "LongArmRotor", "Rocker")


# --------------------------------------------------------------------------
# Geometry loading
# --------------------------------------------------------------------------

def _motion_object(path: Path):
    with zipfile.ZipFile(path) as archive:
        tree = ET.fromstring(archive.read("Document.xml"))
    return next(o for o in tree.findall("./ObjectData/Object") if o.attrib["name"] == "Motion")


def read_fcstd_rows(path: Path = FCSTD) -> list[dict]:
    """Return the LinkageGeometry rows straight from the FreeCAD document.

    An ``.FCStd`` file is a zip archive; ``Document.xml`` holds every object's
    properties. No FreeCAD import is needed.
    """
    prop = _motion_object(path).find("./Properties/Property[@name='LinkageGeometry']/String")
    return json.loads(prop.attrib["value"])


def read_fcstd_motion_properties(path: Path = FCSTD) -> dict:
    """Scalar and string properties of the Motion object, for the snapshot."""
    out = {}
    for prop in _motion_object(path).findall("./Properties/Property"):
        name = prop.attrib["name"]
        child = next(iter(prop), None)
        if child is None or name in {"LinkageGeometry", "Proxy", "ExpressionEngine"}:
            continue
        value = child.attrib.get("value")
        if value is None:
            continue
        if child.tag == "Float":
            value = float(value)
        elif child.tag == "Bool":
            value = value == "true"
        elif child.tag == "Integer":
            value = int(value)
        out[name] = value
    return out


def load_design(path: Path = DESIGN_JSON) -> dict:
    """Load the committed snapshot. See ``make_snapshot`` for its shape."""
    return json.loads(Path(path).read_text())


def make_snapshot(fcstd: Path = FCSTD) -> dict:
    """Build the design snapshot dict from the FreeCAD file."""
    import hashlib

    rows = read_fcstd_rows(fcstd)
    props = read_fcstd_motion_properties(fcstd)
    return {
        "source": str(Path(fcstd).resolve().relative_to(REPO_ROOT)),
        "source_sha256": hashlib.sha256(Path(fcstd).read_bytes()).hexdigest(),
        "motion": props,
        "shared_geometry_mm": {
            "cam_centre_y": CAM_CENTRE_Y,
            "cam_centre_z": CAM_CENTRE_Z,
            "cam_eccentricity": CAM_ECCENTRICITY_MM,
            "cam_radius": CAM_RADIUS_MM,
            "roller_radius": ROLLER_RADIUS_MM,
            "driver_axis_y": DRIVER_AXIS_Y,
            "driver_axis_z": DRIVER_AXIS_Z,
        },
        "input_rpm": DEFAULT_INPUT_RPM,
        "voices": rows,
    }


# --------------------------------------------------------------------------
# Kinematics (port of the macro)
# --------------------------------------------------------------------------

def beta(row: dict, theta: float) -> float:
    """Follower lever angle for cam angle ``theta`` (radians).

    The cam is an eccentric disc: its centre sits 4 mm from the output axle at
    angle ``theta``. The follower roller (3 mm) rides on the 12 mm disc, so the
    roller centre is 15 mm from the disc centre and ``lever_length`` from the
    follower pivot. Of the two circle intersections the macro keeps the one
    with the larger y. Returns ``atan2`` of the lever direction, in radians.
    """
    uy = row.get("follower_y", row["pivot_y"])
    uz = row.get("follower_z", row["pivot_z"])
    cy = CAM_CENTRE_Y - CAM_ECCENTRICITY_MM * math.sin(theta)
    cz = CAM_CENTRE_Z + CAM_ECCENTRICITY_MM * math.cos(theta)
    vy, vz = cy - uy, cz - uz
    d = math.hypot(vy, vz)
    vy, vz = vy / d, vz / d
    lever = row["lever_length"]
    a = (lever * lever - CONTACT_DISTANCE_MM**2 + d * d) / (2.0 * d)
    h = math.sqrt(max(0.0, lever * lever - a * a))
    py, pz = uy + vy * a, uz + vz * a
    b1 = (py - vz * h, pz + vy * h)
    b2 = (py + vz * h, pz - vy * h)
    by, bz = b1 if b1[0] > b2[0] else b2
    return math.atan2(-(by - uy), bz - uz)


def wrap_angle(x: float) -> float:
    """Wrap to (-pi, pi]."""
    return math.atan2(math.sin(x), math.cos(x))


def input_degrees_per_second(rpm: float) -> float:
    return 6.0 * rpm


def cam_angle(row: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> float:
    """Cam angle ``theta`` (radians) at time ``t`` seconds. Negative sense, as
    in the macro: the output turns ``ratio`` times as fast as the input."""
    return -math.radians(input_degrees_per_second(rpm) * t * row["ratio"])


def poses(row: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> dict:
    """Placement of the four moving groups of one voice at time ``t``.

    Each value is ``{"position": (x, y, z), "angle_deg": a}`` meaning a
    rotation of ``a`` degrees about the global X axis at that position,
    matching ``App.Placement(V(s, y, z), App.Rotation(V(1, 0, 0), a))``.
    """
    s = row["station"]
    theta = cam_angle(row, t, rpm)
    b = beta(row, theta)
    delta = wrap_angle(b - row["beta_mid"])
    gain = row.get("swing_gain", 1.0)
    fy = row.get("follower_y", row["pivot_y"])
    fz = row.get("follower_z", row["pivot_z"])

    def place(y, z, angle_deg):
        return {"position": (s, y, z), "angle_deg": angle_deg}

    return {
        "Driver": place(DRIVER_AXIS_Y, DRIVER_AXIS_Z, -input_degrees_per_second(rpm) * t),
        "Output": place(CAM_CENTRE_Y, CAM_CENTRE_Z, math.degrees(theta)),
        "LongArmRotor": place(row["pivot_y"], row["pivot_z"], 90.0 + gain * math.degrees(delta)),
        "Rocker": place(fy, fz, math.degrees(b)),
    }


def arm_swing_deg(row: dict, t: float, rpm: float = DEFAULT_INPUT_RPM) -> float:
    """Pick-arm angle from its mid position, degrees. Zero is the string
    crossing; sign shows which side of the string the pick is on."""
    delta = wrap_angle(beta(row, cam_angle(row, t, rpm)) - row["beta_mid"])
    return row.get("swing_gain", 1.0) * math.degrees(delta)


# --------------------------------------------------------------------------
# Pluck schedule
# --------------------------------------------------------------------------

def pluck_phases(row: dict, samples: int = 2048) -> list[float]:
    """Cam phases in [0, 2pi) at which the follower crosses ``beta_mid``.

    Same search as ``work/make_lovophone_midi.py``: sample one revolution,
    bisect each sign change 55 times. The returned phase ``x`` is the positive
    rotation of the cam; the macro's ``theta`` is ``-x``.
    """

    def f(x):
        return wrap_angle(beta(row, -x) - row["beta_mid"])

    roots = []
    a, fa = 0.0, f(0.0)
    for j in range(1, samples + 1):
        b = TWO_PI * j / samples
        fb = f(b)
        if fa * fb < 0:
            lo, hi, flo = a, b, fa
            for _ in range(55):
                mid = (lo + hi) / 2.0
                fm = f(mid)
                if flo * fm <= 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            root = (lo + hi) / 2.0
            if not roots or abs(root - roots[-1]) > 1e-8:
                roots.append(root)
        a, fa = b, fb
    return roots


def cam_period_seconds(row: dict, rpm: float = DEFAULT_INPUT_RPM) -> float:
    return 60.0 / rpm / row["ratio"]


def repeat_seconds(design: dict, rpm: float = DEFAULT_INPUT_RPM) -> float:
    """Time for every ideal cam phase to return together: the LCM of the ratio
    denominators times one input revolution."""
    denominators = (Fraction(v["ratio_exact"]).denominator for v in design["voices"])
    return reduce(math.lcm, denominators) * 60.0 / rpm


def voice_frequency(row: dict, tunings: dict | None = None) -> float:
    """Just frequency of a voice, or the override in ``tunings`` keyed by
    ``display_note`` (e.g. ``{"C3": 128.0}``)."""
    if tunings and row["display_note"] in tunings:
        return float(tunings[row["display_note"]])
    return row["frequency_hz"]


def pluck_events(
    design: dict,
    duration: float | None = None,
    rpm: float = DEFAULT_INPUT_RPM,
    tunings: dict | None = None,
) -> list[dict]:
    """Every pluck in ``[0, duration)`` across the twelve voices, time-sorted.

    Each event: ``time`` (s), ``voice`` (display note), ``index`` (0..11),
    ``frequency_hz``, ``crossing`` (1 or 2, which of the two crossings in the
    cam cycle), ``cam_revolution`` (0-based).
    """
    if duration is None:
        duration = repeat_seconds(design, rpm)
    events = []
    for index, row in enumerate(design["voices"]):
        period = cam_period_seconds(row, rpm)
        phases = pluck_phases(row)
        freq = voice_frequency(row, tunings)
        for k in range(math.ceil(duration / period) + 1):
            for crossing, phase in enumerate(phases, start=1):
                t = (k + phase / TWO_PI) * period
                if 0.0 <= t < duration:
                    events.append(
                        {
                            "time": t,
                            "voice": row["display_note"],
                            "index": index,
                            "frequency_hz": freq,
                            "crossing": crossing,
                            "cam_revolution": k,
                        }
                    )
    events.sort(key=lambda e: (e["time"], e["index"]))
    return events
