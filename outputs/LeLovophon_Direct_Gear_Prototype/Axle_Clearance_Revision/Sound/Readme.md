Generated audio/video files named below are retained locally and intentionally excluded from this repository. This folder preserves their settings, credits and checks.

# Le Lovophon — corrected direct-gear film soundtrack

The WAV is an exactly eight-minute, 48 kHz, 24-bit stereo synthesized nylon-like string audition, tuned to the established C-based just-intonation pentatonic ratios. The MP3 is a convenient listening copy. This is not a recording or an acoustic prediction of the unbuilt instrument. There is no reverb; decays wrap around the loop rather than being cut off.

Plucks occur at both centre crossings of each exact crank-rocker mechanism, including its unequal outward/return timing. These supersede the old Lab Frame/Unified MIDI for this corrected direct-gear video. The audio and both MIDI variants share one event list.

In Bitwig, use 120 BPM, place the audio/video/MIDI at the same zero, and import the twelve string tracks into your group. The duration is 240 bars in 4/4. Octave names can differ: MIDI 48 is our C3, 130.8127826503 Hz.

For Bitwig with the supplied Scala tuning, use LeLovophon_8min_Bitwig_Scala.mid and apply LeLovophon_Pentatonic.scl to every instrument, with conventional C-based mapping and C3 at 130.8127826503 Hz. This MIDI has neutral pitch bend. Alternatively use LeLovophon_8min_Just_Intonation.mid with ordinary equal-tempered instruments that honor each track's pitch-bend channel and +/-2-semitone range. Do not combine pitch-bend tuning with Scala tuning. The WAV already has the correct tuning.

The current film samples both zero and 480 seconds in 5760 images. To match those images, internal pluck times are scaled by 5759/5760 (less than 0.02%). There is no additional duplicate pluck on its closing zero frame: that belongs to the next loop. No opening silence, no count-in. The CSV includes both mechanism and film/audio times. MIDI event rounding is at most 0.261 milliseconds. Gate lengths are 1.8 seconds; your chosen synth envelope controls the audible decay.

The prototype assumes picks release on both passes. Actual pick-release deflection, string tension and measured sound remain bench-test questions. Files stay local.
