"""Standard MIDI writer for a Lovophon pluck schedule.

Same conventions as Paul's ``work/make_lovophone_midi.py`` so the files drop
into the Bitwig setup described in ``outputs/Lovophone_MIDI_Readme.md``:
format 1, 960 PPQ, 120 BPM, one conductor track plus one track per voice on
its own channel (channel 10 skipped), RPN pitch-bend range +/-2 semitones,
General MIDI program 24 (nylon guitar), two-second notes, velocity 84.

Just intonation is carried as a fixed per-channel pitch bend from the voice's
equal-tempered MIDI note. The equal-temperament copy keeps identical timing
with neutral bends, for hosts that ignore channel tuning.
"""
from __future__ import annotations

import math
import struct

PPQ = 960
TEMPO_US = 500_000  # 120 BPM
TICKS_PER_SECOND = PPQ * 1_000_000 / TEMPO_US
CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]
NOTE_SECONDS = 2.0
VELOCITY = 84
PROGRAM_NYLON_GUITAR = 24
C3_MIDI = 48
C3_HZ = 130.8127826502993


def vlq(n: int) -> bytes:
    assert 0 <= n < 0x1000_0000
    out = [n & 127]
    n >>= 7
    while n:
        out.insert(0, (n & 127) | 128)
        n >>= 7
    return bytes(out)


def meta(kind: int, payload: bytes | str) -> bytes:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return bytes([255, kind]) + vlq(len(payload)) + payload


def track_chunk(events: list[tuple[int, int, bytes]]) -> bytes:
    """``events`` are ``(tick, order, message)``; sorted by tick then order."""
    events = sorted(events, key=lambda e: (e[0], e[1]))
    buf = bytearray()
    last = 0
    for tick, _, msg in events:
        buf += vlq(tick - last) + msg
        last = tick
    return b"MTrk" + struct.pack(">I", len(buf)) + buf


def pitch_bend_14bit(frequency_hz: float, midi_note: int) -> tuple[int, float]:
    """Bend value and its cents for ``frequency_hz`` against an equal-tempered
    ``midi_note`` (A4 = 440 Hz), within the +/-2 semitone RPN range."""
    et_hz = 440.0 * 2 ** ((midi_note - 69) / 12)
    cents = 1200.0 * math.log2(frequency_hz / et_hz)
    bend = round(8192 + cents / 200.0 * 8192)
    bend = max(0, min(16383, bend))
    return bend, cents


def build_midi(
    design: dict,
    events: list[dict],
    duration: float,
    rpm: float,
    just_intonation: bool = True,
    title: str | None = None,
    tunings: dict | None = None,
) -> bytes:
    from .model import voice_frequency

    voices = design["voices"]
    end_tick = round(duration * TICKS_PER_SECOND)
    label = "just-intonation" if just_intonation else "equal-temperament compatibility"
    title = title or f"Le Lovophon - Lab Frame ratio review, {duration:g} s {label} cycle"
    conductor = [
        (0, 0, meta(3, title)),
        (0, 1, meta(0x51, TEMPO_US.to_bytes(3, "big"))),
        (0, 2, meta(0x58, bytes([4, 2, 24, 8]))),
        (
            0,
            3,
            meta(
                1,
                f"Input shaft {rpm:g} rpm. Pitch and average cam rotation share exact "
                "pentatonic ratios. Two beta_mid crossings per cam revolution. "
                "C3 = MIDI 48. Per-channel pitch bend, range +/-2 semitones.",
            ),
        ),
        (0, 4, meta(6, "Cycle start")),
        (end_tick, 5, meta(6, "Cycle end")),
        (end_tick, 99, meta(0x2F, b"")),
    ]
    tracks = [track_chunk(conductor)]
    by_voice: dict[int, list[dict]] = {i: [] for i in range(len(voices))}
    for e in events:
        by_voice[e["index"]].append(e)

    for index, row in enumerate(voices):
        ch = CHANNELS[index]
        note = int(row["midi_note"])
        freq = voice_frequency(row, tunings)
        bend, cents = pitch_bend_14bit(freq, note)
        if not just_intonation:
            bend = 8192
        track = [
            (0, 0, meta(3, f"{row['display_note']} - {row['ratio_exact']} of C3")),
            (0, 1, meta(0x20, bytes([ch]))),
            (
                0,
                2,
                meta(
                    1,
                    f"Pitch {freq:.9f} Hz; correction {cents:+.6f} cents; "
                    f"speaking length {row['speaking_length']:.6f} mm; "
                    f"teeth {row['driver_teeth']}/{row['driven_teeth']}.",
                ),
            ),
            (0, 3, bytes([0xC0 | ch, PROGRAM_NYLON_GUITAR])),
            (0, 4, bytes([0xB0 | ch, 7, 100])),
            (0, 5, bytes([0xB0 | ch, 11, 127])),
        ]
        # RPN 0,0: pitch-bend sensitivity 2 semitones, then null RPN.
        for order, cc, val in [(6, 101, 0), (7, 100, 0), (8, 6, 2), (9, 38, 0), (10, 101, 127), (11, 100, 127)]:
            track.append((0, order, bytes([0xB0 | ch, cc, val])))
        track.append((0, 12, bytes([0xE0 | ch, bend & 127, (bend >> 7) & 127])))
        for e in by_voice[index]:
            on = round(e["time"] * TICKS_PER_SECOND)
            off = min(end_tick, round((e["time"] + NOTE_SECONDS) * TICKS_PER_SECOND))
            track.append((on, 30, bytes([0x90 | ch, note, VELOCITY])))
            track.append((off, 20, bytes([0x80 | ch, note, 0])))
        track.append((end_tick, 90, bytes([0xB0 | ch, 123, 0])))
        track.append((end_tick, 99, meta(0x2F, b"")))
        tracks.append(track_chunk(track))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    return header + b"".join(tracks)
