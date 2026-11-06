"""Command line for the Lovophon model.

    python3 -m sim.lovophon --csv --midi            # 480 s at 3 rpm into outputs/
    python3 -m sim.lovophon --rpm 6 --duration 120 --csv --out /tmp/x
    python3 -m sim.lovophon --snapshot               # refresh design.json from the FCStd
    python3 -m sim.lovophon --tune C3=128 --midi     # override a string's pitch
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from . import midi as midi_writer
from .model import (
    DEFAULT_INPUT_RPM,
    DESIGN_JSON,
    FCSTD,
    REPO_ROOT,
    load_design,
    make_snapshot,
    pluck_events,
    repeat_seconds,
)

OUTPUTS = REPO_ROOT / "outputs"
STEM = "Lovophone_Lab_Frame"


def parse_tunings(items: list[str]) -> dict:
    tunings = {}
    for item in items:
        note, _, hz = item.partition("=")
        if not hz:
            raise SystemExit(f"--tune expects NOTE=HZ, got {item!r}")
        tunings[note] = float(hz)
    return tunings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m sim.lovophon", description=__doc__.split("\n")[0])
    p.add_argument("--rpm", type=float, default=DEFAULT_INPUT_RPM, help="input shaft speed (default 3)")
    p.add_argument("--duration", type=float, default=None, help="seconds; default is one full repeat")
    p.add_argument("--tune", action="append", default=[], metavar="NOTE=HZ", help="override a voice's pitch, e.g. C3=128")
    p.add_argument("--csv", action="store_true", help="write the pluck-time CSV")
    p.add_argument("--midi", action="store_true", help="write just-intonation and equal-temperament MIDI")
    p.add_argument("--out", type=Path, default=OUTPUTS, help="output directory (default outputs/)")
    p.add_argument("--snapshot", action="store_true", help="regenerate design.json from the FreeCAD file")
    p.add_argument("--summary", action="store_true", help="print the twelve voices and the repeat time")
    args = p.parse_args(argv)

    if args.snapshot:
        snapshot = make_snapshot(FCSTD)
        DESIGN_JSON.write_text(json.dumps(snapshot, indent=1) + "\n")
        print(f"wrote {DESIGN_JSON.relative_to(REPO_ROOT)} from {snapshot['source']}")

    design = load_design()
    duration = args.duration if args.duration is not None else repeat_seconds(design, args.rpm)
    tunings = parse_tunings(args.tune)

    if args.summary or not (args.csv or args.midi or args.snapshot):
        print(f"input {args.rpm:g} rpm, full repeat {repeat_seconds(design, args.rpm):g} s, schedule {duration:g} s")
        print("voice  ratio  teeth    cam s   string mm   arm mm    Hz")
        for row in design["voices"]:
            period = 60.0 / args.rpm / row["ratio"]
            print(
                f"{row['display_note']:5} {row['ratio_exact']:>5}  {row['driver_teeth']:>2}/{row['driven_teeth']:<2} "
                f"{period:8.3f} {row['speaking_length']:10.3f} {row['radius']:8.3f} {row['frequency_hz']:8.3f}"
            )

    if not (args.csv or args.midi):
        return 0

    events = pluck_events(design, duration, args.rpm, tunings)
    args.out.mkdir(parents=True, exist_ok=True)
    tag = f"{duration:g}s" + ("" if args.rpm == DEFAULT_INPUT_RPM else f"_{args.rpm:g}rpm")

    if args.csv:
        path = args.out / f"{STEM}_{tag}_Pluck_Times.csv"
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seconds", "voice", "midi_channel_1_based", "midi_note", "just_frequency_hz", "crossing_in_cycle", "cam_revolution"])
            for e in events:
                row = design["voices"][e["index"]]
                w.writerow([f"{e['time']:.9f}", e["voice"], midi_writer.CHANNELS[e["index"]] + 1, row["midi_note"], f"{e['frequency_hz']:.9f}", e["crossing"], e["cam_revolution"]])
        print(f"wrote {path} ({len(events)} plucks)")

    if args.midi:
        for just, name in [(True, "Just_Intonation"), (False, "Equal_Temperament")]:
            path = args.out / f"{STEM}_{tag}_{name}.mid"
            path.write_bytes(midi_writer.build_midi(design, events, duration, args.rpm, just_intonation=just, tunings=tunings))
            print(f"wrote {path}")
        print("note: *.mid is gitignored upstream; regenerate rather than commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
