"""Le Lovophon kinematic model, free of FreeCAD.

    from sim.lovophon import load_design, pluck_events, poses

    design = load_design()
    for e in pluck_events(design, duration=60, rpm=3):
        print(f"{e['time']:8.3f}  {e['voice']}  {e['frequency_hz']:.2f} Hz")
"""
from .model import (  # noqa: F401
    DEFAULT_INPUT_RPM,
    DESIGN_JSON,
    FCSTD,
    arm_swing_deg,
    beta,
    cam_angle,
    cam_period_seconds,
    events_flat,
    load_design,
    make_snapshot,
    pluck_events,
    pluck_phases,
    poses,
    poses_flat,
    read_fcstd_rows,
    repeat_seconds,
    speaking_frequency,
    voice_frequency,
)
