# Le Lovophone — full 160-minute MIDI cycle

Open **Lovophone_160min_Just_Intonation.mid** for the intended tuning. It contains twelve string tracks plus a tempo track, at normal model speed: 3 rpm for the common axle, with two plucks per cam revolution. The complete pattern is 160 minutes and contains 16,150 plucks. Trigger times follow the model’s actual centre crossings, including its phase offsets and unequal half-cycle intervals.

The starting register is C4. Each string uses its own MIDI channel and a fixed pitch bend, with ±2-semitone bend sensitivity set by RPN. Channel 10 is avoided. The initial program is General MIDI nylon-string guitar; choose another sound if desired. A note lasts two seconds and is truncated at the end boundary when necessary. There is no generated audio in these files.

For correct just intonation, use a multitimbral instrument that respects pitch bend independently on each channel, or route each string track to a separate instrument instance. A plugin that treats all channels as one pitch-bend domain can detune the whole ensemble. The Scala file is an alternative tuning method: use it with the equal-tempered compatibility MIDI, root C / MIDI 60, **without** also applying the pitch-bend corrections. Applying both methods would double the correction.

**Lovophone_160min_Equal_Temperament.mid** preserves the identical timing and track layout with neutral pitch bends. It is a compatibility copy for plugins that ignore channel tuning. Without a Scala or other tuning map, it plays twelve-tone equal temperament rather than our just-intonation scale.

The CSV gives every trigger time. The JSON gives frequencies, pitch corrections, event counts and phase details. The schedule is an idealized mechanical performance: it does not simulate nylon vibration, contact force, motor fluctuation, dynamics or resonance. You can transpose the register, change the instrument and adjust note lengths in your DAW.
