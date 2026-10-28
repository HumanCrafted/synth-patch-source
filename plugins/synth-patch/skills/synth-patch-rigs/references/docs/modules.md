<!-- Copied from docs/modules.md in synth-patch-source by scripts/build_reference.py. Edit the original. -->

# Standard modules

Synth Patch's own modules: generic building blocks (oscillator, filter, envelope…) for cabling into [rigs](rigs.md). Each is a generated [`synthjson/2`](synth-package.md#generated-synths) package with an [engine](engine.md) and graphics from the [parts library](parts.md), in [`modules/`](../library/modules). Their slugs start `synth-patch-`, so they read as made by "Synth Patch" next to real manufacturers.

## Design

The modules are a small, complete starter system, in the spirit of VCV Rack's free modules and the classic basic systems (Doepfer's A-100 Mini System, the Moog Mother-32): each module does one job, and together they patch into a full mono voice with no extra utilities. Four rules:

1. **One job per module.** No combination modules. A module's name says what it does.
2. **Every modulation input has its own amount knob.** V/Oct inputs stay unscaled so pitch tracks exactly; every other CV input has a knob that scales it (FM Amount, PWM Amount, CV Amount).
3. **Sensible normals.** Modules work before they're fully patched: internal clocks run until a clock is patched in, Random samples its own noise, and a VCA's Initial Level can pass sound with nothing in its CV.
4. **One signal convention**, the same on every module ([Signals](engine.md#signals)), so any cable does what you'd predict.

Left out on purpose:

- **Mult:** any output already feeds any number of inputs.
- **A separate sample and hold:** Random is one (its Sample Input).
- **Logic, comparators, switches, polyphony, wavetables:** beyond a starter set. The Code module covers the odd case.
- **Ring modulation:** the VCA clamps its CV at zero, so it doesn't ring-modulate. Code covers it for now.

Names are an API: rigs find controls and jacks by name, so a module never renames a control or jack once rigs use it. New controls are added instead.

## The modules

Every control and jack, spelled exactly as rigs must spell them. Switch positions are in parentheses; knobs are unipolar (0 to 1) unless marked bipolar. Panel sizes are in 288 dpi pixels, as the app lays them out, for placing instances in a rig.

#### Sound

| Module | Panel | Controls | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| [`synth-patch-oscillator`](../library/modules/synth-patch-oscillator.json) | 1240 × 1239 | Octave (32', 16', 8', 4'), Tune (bipolar), Fine (bipolar), Pulse Width, FM Amount, PWM Amount | V/Oct Input, FM Input, PWM Input, Sync Input | Saw Output, Triangle Output, Square Output |
| [`synth-patch-noise`](../library/modules/synth-patch-noise.json) | 520 × 634 | Color (White, Pink, Brown) | – | Noise Output |
| [`synth-patch-filter`](../library/modules/synth-patch-filter.json) | 1575 × 1021 | Cutoff, Resonance, Envelope Amount (bipolar), Key Track, CV Amount | Filter Input, V/Oct Input, Envelope Input, Cutoff CV Input | LP Output, HP Output |
| [`synth-patch-vca`](../library/modules/synth-patch-vca.json) | 896 × 750 | Gain, Initial Level, CV Amount | VCA Input, CV Input | VCA Output |
| [`synth-patch-mixer`](../library/modules/synth-patch-mixer.json) | 1280 × 750 | Level A, Level B, Level C, Level D | Input A, Input B, Input C, Input D | Mixer Output |
| [`synth-patch-speaker`](../library/modules/synth-patch-speaker.json) | 592 × 1222 | Level | Speaker Input | – |

#### Modulation & Timing

| Module | Panel | Controls | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| [`synth-patch-keyboard`](../library/modules/synth-patch-keyboard.json) | 2272 × 2200 | Octave (C2, C3, C4, C5), Gate (LED), 13 keys, C3, C#3 … B3, C4 | – | Pitch Output, Gate Output |
| [`synth-patch-envelope`](../library/modules/synth-patch-envelope.json) | 1280 × 750 | Attack, Decay, Sustain, Release | Gate Input | Envelope Output |
| [`synth-patch-lfo`](../library/modules/synth-patch-lfo.json) | 948 × 762 | Rate, Shape (Sine, Triangle, Saw, Square), CV Amount | Rate CV Input | LFO Output |
| [`synth-patch-random`](../library/modules/synth-patch-random.json) | 1140 × 750 | Rate, Smooth, Clock (LED) | Clock Input, Sample Input | Stepped Output, Smooth Output |
| [`synth-patch-clock`](../library/modules/synth-patch-clock.json) | 760 × 956 | Tempo, Clock (LED) | Run Input, Reset Input | Clock Output, ÷2 Output, ÷4 Output |
| [`synth-patch-sequencer`](../library/modules/synth-patch-sequencer.json) | 1712 × 1509 | Tempo, Length (8 steps), Gate Length, Step 1 … Step 8, Gate 1 … Gate 8 (buttons), 1 … 8 (LEDs) | Clock Input, Reset Input, Run Input | Pitch Output, Gate Output |

#### Effects

| Module | Panel | Controls | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| [`synth-patch-delay`](../library/modules/synth-patch-delay.json) | 988 × 750 | Time, Feedback, Mix | Delay Input | Delay Output |
| [`synth-patch-reverb`](../library/modules/synth-patch-reverb.json) | 988 × 750 | Size, Damping, Mix | Reverb Input | Reverb Output |

#### Utilities

| Module | Panel | Controls | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| [`synth-patch-glide`](../library/modules/synth-patch-glide.json) | 591 × 750 | Time | Glide Input | Glide Output |
| [`synth-patch-attenuverter`](../library/modules/synth-patch-attenuverter.json) | 637 × 1348 | Amount A (bipolar), Offset A (bipolar), Amount B (bipolar), Offset B (bipolar) | A Input, B Input | A Output, B Output |
| [`synth-patch-quantizer`](../library/modules/synth-patch-quantizer.json) | 973 × 762 | Scale (Chromatic, Major, Minor, Major Pentatonic, Minor Pentatonic, Blues), Root (12 steps) | Quantizer Input | Quantizer Output |
| [`synth-patch-code`](../library/modules/synth-patch-code.json) | 1280 × 1004 | P1, P2, P3, P4, Code (code) | A Input, B Input, C Input, D Input | Code Output |

## Module reference


How each module behaves, by the heading it sits under in the app's Add module menu. Knob ranges are what the knob covers end to end, with its default in brackets; "exponential" knobs give finer control at the low end. Levels follow the [signal conventions](engine.md#signals). The blocks behind them are in [Engine](engine.md#block-types).

### Sound

**Oscillator** (`synth-patch-oscillator`)
- Saw, Triangle and Square outputs, all at once (no wave switch). Saw and square are band-limited (PolyBLEP), the triangle's corners too (PolyBLAMP).
- **Octave:** 32′, 16′, 8′, 4′ [8′]. At 8′ with nothing in V/Oct, it plays middle C (261.63 Hz).
- **Tune:** ±12 semitones [0]. **Fine:** ±50 cents [0].
- **Pulse Width:** 50–95% [50%], for the Square output.
- **V/Oct Input:** pitch, never scaled (1.0 = one octave).
- **FM Input** with **FM Amount:** 0–1 octave per unit of CV [0.1]. An LFO there gives vibrato; turned up, a wide warble.
- **PWM Input** with **PWM Amount:** 0–45% of the cycle per unit of CV [about 22%]. The pulse width stays within 5–95%.
- **Sync Input:** hard sync. The cycle restarts each time the input rises through 0 (patch another oscillator's output here). The restart itself isn't band-limited.

**Noise** (`synth-patch-noise`)
- **Color:** White, Pink (−3 dB/octave), Brown (−6 dB/octave) [White].

**Filter** (`synth-patch-filter`)
- A four-pole (24 dB/octave) ladder: zero-delay-feedback stages, saturation in the feedback, 2× oversampled. **LP Output** is the low-pass; **HP Output** is a 24 dB high-pass mixed from the same stages (as on the Oberheim Xpander), so resonance works on both.
- **Cutoff:** 20 Hz–20 kHz, exponential [632 Hz].
- **Resonance:** 0–1.05 [0.3]. From about 1 it self-oscillates, from silence, at the cutoff.
- **Envelope Amount:** −6 to +6 octaves for a full envelope at Envelope Input, centered at 0 [+3 octaves].
- **Key Track:** 0–1 [0.5]. At 1 the cutoff follows V/Oct Input exactly, so a self-oscillating filter plays in tune.
- **CV Amount:** 0–4 octaves per unit at Cutoff CV Input [1 octave].
- All cutoff changes are smoothed; the CV inputs add.

**VCA** (`synth-patch-vca`)
- Out = In × (CV × CV Amount + Initial Level, kept within 0–1) × Gain. Linear response, DC-coupled, so it works on CV as well as audio.
- **Gain:** 0–2× [1×]. **Initial Level:** 0–1 [0]; with nothing in CV, it sets how much passes (a drone). **CV Amount:** 0–1 [1].
- All three are smoothed.

**Mixer** (`synth-patch-mixer`)
- Four inputs, **Level A–D:** 0–1 each [1], smoothed. DC-coupled, so it mixes CV too. It doesn't boost: full level is unity.

**Speaker** (`synth-patch-speaker`)
- What reaches **Speaker Input** is what you hear, scaled by **Level:** 0–1 [0.8], smoothed. A DC blocker follows, then the page's volume and limiter. Mono.

### Modulation & Timing

**Keyboard** (`synth-patch-keyboard`)
- One octave of keys, played on screen or from the computer keyboard. Mono, last-note priority; every new note retriggers the gate, even played legato.
- **Octave:** C2, C3, C4, C5 [C3], the pitch of the lowest key.
- **Pitch Output** (V/Oct) and **Gate Output** (high while a key is held), with a Gate light.

**Envelope** (`synth-patch-envelope`)
- ADSR. Linear attack; exponential decay and release, like analog envelopes. A new gate restarts the attack from the current level, so there are no clicks.
- **Attack:** 1 ms–5 s [about 5 ms]. **Decay:** 5 ms–5 s [about 0.3 s]. **Sustain:** 0–1 [0.6]. **Release:** 5 ms–8 s [about 0.4 s]. The time knobs are exponential; decay and release times are to within 1% of the target.
- **Gate Input**, **Envelope Output** (0–1).

**LFO** (`synth-patch-lfo`)
- **Shape:** Sine, Triangle, Saw, Square [Sine]. Output −1 to 1.
- **Rate:** 0.05–40 Hz, exponential [about 1.4 Hz].
- **Rate CV Input** with **CV Amount:** 0–3 octaves of rate per unit of CV [about 1 octave].

**Random** (`synth-patch-random`)
- Sample and hold: on each rising clock, **Stepped Output** takes the value at **Sample Input**, or with nothing patched there a new random value (−1 to 1, as from white noise). **Smooth Output** glides to each new value.
- **Rate:** its own clock, 15–960 per minute (0.25–16 Hz), exponential [2 Hz]. Patching **Clock Input** replaces it. The Clock light shows the ticks.
- **Smooth:** 1 ms–2 s, exponential [about 0.1 s].
- Unquantized: send it through the Quantizer for notes in a scale.

**Clock** (`synth-patch-clock`)
- **Tempo:** 20–300 BPM, linear [120 BPM]. One pulse per beat at 50% duty on **Clock Output**; **÷2 Output** and **÷4 Output** rise with it every second and fourth beat.
- **Reset Input:** a rising edge restarts the beat and the divisions together.
- **Run Input:** while patched and low, the clock stops with its outputs low; when it goes high, the clock starts on the beat. Unpatched, it runs.
- The Clock light shows the beat.

**Sequencer** (`synth-patch-sequencer`)
- Up to eight steps, one per rising clock. Each step has a pitch knob, **Step 1–8:** 0–24 semitones (two octaves, snapped to semitones) [0], a **Gate 1–8** button [on] and a light.
- **Length:** 1–8 steps, a stepped knob [8].
- **Gate Length:** 5–100% of the clock period, measured from the clock [50%]. At 100% the gate stays high into the next step (a tie). Until a period is measured, the gate follows the clock. Steps with their gate off advance silently.
- **Tempo:** its own clock, 20–300 BPM, linear [120 BPM], the same range as the Clock. Patching **Clock Input** replaces it.
- **Reset Input:** a rising edge makes the next clock play step 1. A clock that arrived up to 1 ms before the reset counts as arriving with it and plays step 1 at once (as VCV does for a reset and clock sent together).
- **Run Input:** while patched and low, clocks are ignored and the gate stays low. Unpatched, it runs.
- **Pitch Output** (V/Oct, 0 to 2) and **Gate Output**.

### Effects

**Delay** (`synth-patch-delay`)
- **Time:** 10 ms–2 s, exponential [about 0.24 s]. Changing it glides, like tape.
- **Feedback:** 0–95% [42%], saturated so it can't run away. **Mix:** dry to wet [35%], smoothed.

**Reverb** (`synth-patch-reverb`)
- A plate after Dattorro (1997): four input diffusers into a figure-eight tank of two modulated branches, heard through fourteen taps summed to mono.
- **Size:** the decay, short room to long plate [0.6]; stable at full. **Damping:** how fast the highs die [0.4]. **Mix:** dry to wet [30%], smoothed.

### Utilities

**Glide** (`synth-patch-glide`)
- **Glide Output** follows **Glide Input**, taking **Time** to get within 1% of each new value (an exponential, RC-style glide). Patch it between a pitch source and a V/Oct input for portamento, or use it on any CV as a slew limiter.
- **Time:** off to 2 s, exponential [about 70 ms]. Fully left, there's no glide.

**Attenuverter** (`synth-patch-attenuverter`)
- Two channels, A and B. Each output = input × **Amount** + **Offset**, smoothed.
- **Amount A/B:** −1 to +1 [+1]. Below center it inverts.
- **Offset A/B:** −1 to +1 [0]. With nothing in a channel's input, its output is the offset alone, a steady CV (for pitch, 1.0 = one octave).

**Quantizer** (`synth-patch-quantizer`)
- Snaps the pitch at **Quantizer Input** (V/Oct) to the nearest note of a scale and sends it to **Quantizer Output**. Halfway between two notes, it takes the lower one.
- **Scale:** Chromatic, Major, Minor (natural), Major Pentatonic, Minor Pentatonic, Blues [Chromatic].
- **Root:** C to B, a stepped knob [C], the key the scale starts on.

**Code** (`synth-patch-code`, advanced)
- JavaScript that runs once per sample: inputs `a`–`d` (**A–D Input**), knobs `p[0]`–`p[3]` (**P1–P4**, 0–1), `state` (kept between samples), `t` (seconds) and `sr` (sample rate). It returns the output sample, kept within ±4.
- An error, or a loop that runs too long, stops the module with a message on its panel until the code changes.
