# Worked examples

Each rig here was written from the request above it, then checked two ways: `scripts/rig.py check` (OK, no warnings) and the Synth Patch app's own rig reader and engine (no problems, and it makes sound). Values were set with `scripts/rig.py value` and positions with `scripts/rig.py layout`.

## [Acid Line](acid-line.json)

> A squelchy acid bassline around 128 BPM that plays by itself, with a bit of delay.

Sequencer → Oscillator (16′ saw) → Filter (resonance 0.85, envelope +4 octaves) → VCA → Delay → Speaker, with one Envelope (no sustain) on both the filter and the VCA.

- The Sequencer steps once per beat of its own clock, so eighth notes at 128 BPM is Tempo 256.
- Steps 2 and 7 rest (`"Gate 2": false`), steps are semitones ÷ 24.
- The Sequencer's Pitch Output also goes to the Filter's V/Oct Input, so the resonance tracks the notes.
- The delay time is a dotted eighth at 128 BPM (0.35 s).

## [Pentatonic Drift](generative-ambient.json)

> Something generative and ambient I can leave running: random notes in A minor pentatonic, slow and soft, with lots of reverb.

Clock (48 BPM) → Random → Quantizer (Minor Pentatonic, root A) → Glide → Oscillator → Filter → VCA → Reverb → Speaker. The same Clock gates a slow Envelope; an LFO sweeps the cutoff over about 14 seconds.

- A pitch chain that plays itself: clock, sample and hold, quantizer, glide.
- Random's own clock is replaced by patching its Clock Input, so notes and envelope stay in step.
- Root A on a 12-step knob is 9 ÷ 11 = 0.8182.

## [Glide Lead](glide-lead.json)

> A lead I can play from my computer keyboard, with portamento and a little vibrato.

Keyboard (C4) → Glide → Oscillator and Filter V/Oct; Keyboard gate → Envelope → Filter and VCA; LFO (5.5 Hz) → Oscillator FM Input; Delay → Speaker.

- A Keyboard module takes the notes, so everything it's cabled to plays from the keys.
- Vibrato depth is the Oscillator's FM Amount: 0.018 octaves is about 20 cents either way.
- Key Track at 1 keeps the filter's brightness the same up and down the keyboard.

## [Evolving Drone](evolving-drone.json) and [Custom Slow LFO](slow-lfo.synth.json)

> A drone that slowly changes over a couple of minutes. The normal LFO doesn't go slow enough.

A variant first: `custom-slow-lfo` extends `synth-patch-lfo`, moves the Rate range down to 0.002–2 Hz and adds a Unipolar Output (0 to 1, from an attenuverter block inside it). Then the rig: two 16′ saws a fifth apart (Tune 7 semitones, Fine +7 cents) → Mixer → Filter → VCA → Reverb → Speaker. The slow LFO's Unipolar Output opens the filter through its Envelope Input over a 100-second cycle. The VCA's Initial Level holds it open with no envelope.

- A variant lists only what changes. The `lfo` block's `params` are given in full because a block's fields replace the base's.
- The rig names the variant by its slug. Check it with `rig.py check evolving-drone.json --synth slow-lfo.synth.json`.
- To play it, add the variant with Add module → Paste synth JSON, then paste the rig.

## From the docs

`references/examples/` holds the two rigs from the format docs: [Wavefolded Bass](../references/examples/wavefolded-bass.json), a Keyboard playing an Oscillator folded by a Code module, and [Demo One Echo](../references/examples/demo-one-echo.json), a drawn synth with its own keys and output, through a Delay module.
