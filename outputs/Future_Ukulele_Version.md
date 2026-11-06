# Future branch: clip-on four-string ukulele player

User concept: a removable unit clips onto a four-string ukulele and plays MIDI files. Keep this as a future branch while developing the current acoustic instrument.

The simplest first prototype would use four individually controlled compliant pluckers, one per string, with adjustable position and soft, non-marking mounting pads. The unit should remove without drilling or permanent alterations. MIDI parsing would map suitable note events to the four open strings; unsupported notes should be reported or deliberately arranged rather than silently promising full melody playback. Note velocity could eventually vary pluck depth or actuator speed, subject to testing.

Full chromatic melodies and chords require additional fretting actuators or a different musical arrangement. That is a larger mechanical problem involving reach, fret force, string clearance, tuning and mounting loads. The initial design should therefore prove reliable open-string plucking and MIDI timing before adding fretting.

Unresolved: ukulele dimensions and tuning, clamp location and finish compatibility, actuator noise and reaction loads, power source, electronics enclosure, note-off/damping behaviour, maintenance access, transport and total added mass. No hardware or code for this branch has been built yet.
