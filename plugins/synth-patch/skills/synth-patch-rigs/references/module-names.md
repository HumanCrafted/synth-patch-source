<!-- Built from modules/*/synth.json and docs/modules.md by scripts/build_reference.py. Don't edit. -->

# Standard modules: exact names

Every control and jack as rigs must spell them, the group each control's value goes in, its patch value and
default, and what the engine makes of it. Engine ranges are end to end of the knob's travel: a knob at `n`
(0 to 1) gives `lo + n × (hi − lo)`, or `lo × (hi / lo)^n` when it says exp. A bipolar knob at `v` (−1 to 1)
is at `n = (v + 1) / 2`. `scripts/rig.py value <slug> "<Control>" <target>` does the sums.

Panel sizes are in 288 dpi px, for placing instances. Below each table, the module's behavior from the
module reference.

## Sound

### Oscillator · `synth-patch-oscillator`

Panel 1240 × 1239 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Octave | `rotarySwitches` | `32'`, `16'`, `8'`, `4'` | `"8'"` (octave 0 oct) | octave 32'=-2, 16'=-1, 8'=0, 4'=1 |
| Tune | `knobs` | −1 to 1 | `0` (tune 0 st) | tune -12 → 12 st |
| Fine | `knobs` | −1 to 1 | `0` (fine 0 st) | fine -0.5 → 0.5 st |
| Pulse Width | `knobs` | 0 to 1 | `0` (pulseWidth 50% of the cycle) | pulseWidth 0.5 → 0.95 of the cycle |
| FM Amount | `knobs` | 0 to 1 | `0.1` (fmAmount 0.1 oct/unit) | fmAmount 0 → 1 oct/unit |
| PWM Amount | `knobs` | 0 to 1 | `0.5` (pwmAmount 22% of the cycle per unit) | pwmAmount 0 → 0.45 of the cycle/unit |

Inputs: `V/Oct Input`, `FM Input`, `PWM Input`, `Sync Input`  
Outputs: `Saw Output`, `Triangle Output`, `Square Output`

- Saw, Triangle and Square outputs, all at once (no wave switch). Saw and square are band-limited (PolyBLEP), the triangle's corners too (PolyBLAMP).
- **Octave:** 32′, 16′, 8′, 4′ [8′]. At 8′ with nothing in V/Oct, it plays middle C (261.63 Hz).
- **Tune:** ±12 semitones [0]. **Fine:** ±50 cents [0].
- **Pulse Width:** 50–95% [50%], for the Square output.
- **V/Oct Input:** pitch, never scaled (1.0 = one octave).
- **FM Input** with **FM Amount:** 0–1 octave per unit of CV [0.1]. An LFO there gives vibrato; turned up, a wide warble.
- **PWM Input** with **PWM Amount:** 0–45% of the cycle per unit of CV [about 22%]. The pulse width stays within 5–95%.
- **Sync Input:** hard sync. The cycle restarts each time the input rises through 0 (patch another oscillator's output here). The restart itself isn't band-limited.

### Noise · `synth-patch-noise`

Panel 520 × 634 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Color | `toggles` | `White`, `Pink`, `Brown` | `"White"` (color 0) | color White=0, Pink=1, Brown=2 |

Inputs: –  
Outputs: `Noise Output`

- **Color:** White, Pink (−3 dB/octave), Brown (−6 dB/octave) [White].

### Filter · `synth-patch-filter`

Panel 1575 × 1021 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Cutoff | `knobs` | 0 to 1 | `0.5` (cutoff 632 Hz) | cutoff 20 → 20000 Hz, exp |
| Resonance | `knobs` | 0 to 1 | `0.3` (resonance 0.32) | resonance 0 → 1.05 |
| Envelope Amount | `knobs` | −1 to 1 | `0.5` (envAmount +3 oct) | envAmount -6 → 6 oct |
| Key Track | `knobs` | 0 to 1 | `0.5` (keyTrack 0.5 oct/oct) | keyTrack 0 → 1 oct/oct |
| CV Amount | `knobs` | 0 to 1 | `0.25` (cvAmount 1 oct/unit) | cvAmount 0 → 4 oct/unit |

Inputs: `Filter Input`, `V/Oct Input`, `Envelope Input`, `Cutoff CV Input`  
Outputs: `LP Output`, `HP Output`

- A four-pole (24 dB/octave) ladder: zero-delay-feedback stages, saturation in the feedback, 2× oversampled. **LP Output** is the low-pass; **HP Output** is a 24 dB high-pass mixed from the same stages (as on the Oberheim Xpander), so resonance works on both.
- **Cutoff:** 20 Hz–20 kHz, exponential [632 Hz].
- **Resonance:** 0–1.05 [0.3]. From about 1 it self-oscillates, from silence, at the cutoff.
- **Envelope Amount:** −6 to +6 octaves for a full envelope at Envelope Input, centered at 0 [+3 octaves].
- **Key Track:** 0–1 [0.5]. At 1 the cutoff follows V/Oct Input exactly, so a self-oscillating filter plays in tune.
- **CV Amount:** 0–4 octaves per unit at Cutoff CV Input [1 octave].
- All cutoff changes are smoothed; the CV inputs add.

### VCA · `synth-patch-vca`

Panel 896 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Gain | `knobs` | 0 to 1 | `0.5` (gain 1 ×) | gain 0 → 2 × |
| Initial Level | `knobs` | 0 to 1 | `0` (bias 0) | bias 0 → 1 |
| CV Amount | `knobs` | 0 to 1 | `1` (cvAmount 1) | cvAmount 0 → 1 |

Inputs: `VCA Input`, `CV Input`  
Outputs: `VCA Output`

- Out = In × (CV × CV Amount + Initial Level, kept within 0–1) × Gain. Linear response, DC-coupled, so it works on CV as well as audio.
- **Gain:** 0–2× [1×]. **Initial Level:** 0–1 [0]; with nothing in CV, it sets how much passes (a drone). **CV Amount:** 0–1 [1].
- All three are smoothed.

### Mixer · `synth-patch-mixer`

Panel 1280 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Level A | `knobs` | 0 to 1 | `1` (levelA 1) | levelA 0 → 1 |
| Level B | `knobs` | 0 to 1 | `1` (levelB 1) | levelB 0 → 1 |
| Level C | `knobs` | 0 to 1 | `1` (levelC 1) | levelC 0 → 1 |
| Level D | `knobs` | 0 to 1 | `1` (levelD 1) | levelD 0 → 1 |

Inputs: `Input A`, `Input B`, `Input C`, `Input D`  
Outputs: `Mixer Output`

- Four inputs, **Level A–D:** 0–1 each [1], smoothed. DC-coupled, so it mixes CV too. It doesn't boost: full level is unity.

### Speaker · `synth-patch-speaker`

Panel 592 × 1222 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Level | `knobs` | 0 to 1 | `0.8` (gain 0.8 ×) | gain 0 → 1 × |

Inputs: `Speaker Input`  
Outputs: –

- What reaches **Speaker Input** is what you hear, scaled by **Level:** 0–1 [0.8], smoothed. A DC blocker follows, then the page's volume and limiter. Mono.

## Modulation & Timing

### Keyboard · `synth-patch-keyboard`

Panel 2272 × 2200 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Octave | `rotarySwitches` | `C2`, `C3`, `C4`, `C5` | `"C3"` (transpose 0 oct) | transpose C2=-1, C3=0, C4=1, C5=2 |

Inputs: –  
Outputs: `Pitch Output`, `Gate Output`

Set by the engine or the player, so rigs leave them out: Gate (led), C3 (key), C#3 (key), D3 (key), D#3 (key), E3 (key), F3 (key), F#3 (key), G3 (key), G#3 (key), A3 (key), A#3 (key), B3 (key), C4 (key).

- One octave of keys, played on screen or from the computer keyboard. Mono, last-note priority; every new note retriggers the gate, even played legato.
- **Octave:** C2, C3, C4, C5 [C3], the pitch of the lowest key.
- **Pitch Output** (V/Oct) and **Gate Output** (high while a key is held), with a Gate light.

### Envelope · `synth-patch-envelope`

Panel 1280 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Attack | `knobs` | 0 to 1 | `0.2` (attack 0.005 s) | attack 0.001 → 5 s, exp |
| Decay | `knobs` | 0 to 1 | `0.6` (decay 0.32 s) | decay 0.005 → 5 s, exp |
| Sustain | `knobs` | 0 to 1 | `0.6` (sustain 0.6) | sustain 0 → 1 |
| Release | `knobs` | 0 to 1 | `0.6` (release 0.42 s) | release 0.005 → 8 s, exp |

Inputs: `Gate Input`  
Outputs: `Envelope Output`

- ADSR. Linear attack; exponential decay and release, like analog envelopes. A new gate restarts the attack from the current level, so there are no clicks.
- **Attack:** 1 ms–5 s [about 5 ms]. **Decay:** 5 ms–5 s [about 0.3 s]. **Sustain:** 0–1 [0.6]. **Release:** 5 ms–8 s [about 0.4 s]. The time knobs are exponential; decay and release times are to within 1% of the target.
- **Gate Input**, **Envelope Output** (0–1).

### LFO · `synth-patch-lfo`

Panel 948 × 762 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Rate | `knobs` | 0 to 1 | `0.5` (rate 1.41 Hz) | rate 0.05 → 40 Hz, exp |
| Shape | `rotarySwitches` | `Sine`, `Triangle`, `Saw`, `Square` | `"Sine"` (shape 0) | shape Sine=0, Triangle=1, Saw=2, Square=3 |
| CV Amount | `knobs` | 0 to 1 | `0.33` (rateCvAmount 0.99 oct/unit) | rateCvAmount 0 → 3 oct/unit |

Inputs: `Rate CV Input`  
Outputs: `LFO Output`

- **Shape:** Sine, Triangle, Saw, Square [Sine]. Output −1 to 1.
- **Rate:** 0.05–40 Hz, exponential [about 1.4 Hz].
- **Rate CV Input** with **CV Amount:** 0–3 octaves of rate per unit of CV [about 1 octave].

### Random · `synth-patch-random`

Panel 1140 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Rate | `knobs` | 0 to 1 | `0.5` (bpm 120 BPM) | bpm 15 → 960 BPM, exp |
| Smooth | `knobs` | 0 to 1 | `0.3` (smooth 0.01 s) | smooth 0.001 → 2 s, exp |

Inputs: `Clock Input`, `Sample Input`  
Outputs: `Stepped Output`, `Smooth Output`

Set by the engine or the player, so rigs leave them out: Clock (led).

- Sample and hold: on each rising clock, **Stepped Output** takes the value at **Sample Input**, or with nothing patched there a new random value (−1 to 1, as from white noise). **Smooth Output** glides to each new value.
- **Rate:** its own clock, 15–960 per minute (0.25–16 Hz), exponential [2 Hz]. Patching **Clock Input** replaces it. The Clock light shows the ticks.
- **Smooth:** 1 ms–2 s, exponential [about 0.1 s].
- Unquantized: send it through the Quantizer for notes in a scale.

### Clock · `synth-patch-clock`

Panel 760 × 956 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Tempo | `knobs` | 0 to 1 | `0.357` (bpm 120 BPM) | bpm 20 → 300 BPM |

Inputs: `Run Input`, `Reset Input`  
Outputs: `Clock Output`, `÷2 Output`, `÷4 Output`

Set by the engine or the player, so rigs leave them out: Clock (led).

- **Tempo:** 20–300 BPM, linear [120 BPM]. One pulse per beat at 50% duty on **Clock Output**; **÷2 Output** and **÷4 Output** rise with it every second and fourth beat.
- **Reset Input:** a rising edge restarts the beat and the divisions together.
- **Run Input:** while patched and low, the clock stops with its outputs low; when it goes high, the clock starts on the beat. Unpatched, it runs.
- The Clock light shows the beat.

### Sequencer · `synth-patch-sequencer`

Panel 1712 × 1509 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Tempo | `knobs` | 0 to 1 | `0.357` (bpm 120 BPM) | bpm 20 → 300 BPM |
| Length | `knobs` | 0 to 1, 8 steps | `1` (length 8 steps) | length 1 → 8 steps |
| Gate Length | `knobs` | 0 to 1 | `0.4737` (gateLength 50 %) | gateLength 5 → 100 % |
| Step 1 | `knobs` | 0 to 1 | `0` (step1 0 st) | step1 0 → 24 st |
| Step 2 | `knobs` | 0 to 1 | `0` (step2 0 st) | step2 0 → 24 st |
| Step 3 | `knobs` | 0 to 1 | `0` (step3 0 st) | step3 0 → 24 st |
| Step 4 | `knobs` | 0 to 1 | `0` (step4 0 st) | step4 0 → 24 st |
| Step 5 | `knobs` | 0 to 1 | `0` (step5 0 st) | step5 0 → 24 st |
| Step 6 | `knobs` | 0 to 1 | `0` (step6 0 st) | step6 0 → 24 st |
| Step 7 | `knobs` | 0 to 1 | `0` (step7 0 st) | step7 0 → 24 st |
| Step 8 | `knobs` | 0 to 1 | `0` (step8 0 st) | step8 0 → 24 st |
| Gate 1 | `buttons` | `true` / `false` | `true` (gate1 1) | gate1 1 when true, 0 when false |
| Gate 2 | `buttons` | `true` / `false` | `true` (gate2 1) | gate2 1 when true, 0 when false |
| Gate 3 | `buttons` | `true` / `false` | `true` (gate3 1) | gate3 1 when true, 0 when false |
| Gate 4 | `buttons` | `true` / `false` | `true` (gate4 1) | gate4 1 when true, 0 when false |
| Gate 5 | `buttons` | `true` / `false` | `true` (gate5 1) | gate5 1 when true, 0 when false |
| Gate 6 | `buttons` | `true` / `false` | `true` (gate6 1) | gate6 1 when true, 0 when false |
| Gate 7 | `buttons` | `true` / `false` | `true` (gate7 1) | gate7 1 when true, 0 when false |
| Gate 8 | `buttons` | `true` / `false` | `true` (gate8 1) | gate8 1 when true, 0 when false |

Inputs: `Clock Input`, `Reset Input`, `Run Input`  
Outputs: `Pitch Output`, `Gate Output`

Set by the engine or the player, so rigs leave them out: 1 (led), 2 (led), 3 (led), 4 (led), 5 (led), 6 (led), 7 (led), 8 (led).

- Up to eight steps, one per rising clock. Each step has a pitch knob, **Step 1–8:** 0–24 semitones (two octaves, snapped to semitones) [0], a **Gate 1–8** button [on] and a light.
- **Length:** 1–8 steps, a stepped knob [8].
- **Gate Length:** 5–100% of the clock period, measured from the clock [50%]. At 100% the gate stays high into the next step (a tie). Until a period is measured, the gate follows the clock. Steps with their gate off advance silently.
- **Tempo:** its own clock, 20–300 BPM, linear [120 BPM], the same range as the Clock. Patching **Clock Input** replaces it.
- **Reset Input:** a rising edge makes the next clock play step 1. A clock that arrived up to 1 ms before the reset counts as arriving with it and plays step 1 at once (as VCV does for a reset and clock sent together).
- **Run Input:** while patched and low, clocks are ignored and the gate stays low. Unpatched, it runs.
- **Pitch Output** (V/Oct, 0 to 2) and **Gate Output**.

## Effects

### Delay · `synth-patch-delay`

Panel 988 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Time | `knobs` | 0 to 1 | `0.6` (time 0.24 s) | time 0.01 → 2 s, exp |
| Feedback | `knobs` | 0 to 1 | `0.42` (feedback 0.4) | feedback 0 → 0.95 |
| Mix | `knobs` | 0 to 1 | `0.35` (mix 0.35) | mix 0 → 1 |

Inputs: `Delay Input`  
Outputs: `Delay Output`

- **Time:** 10 ms–2 s, exponential [about 0.24 s]. Changing it glides, like tape.
- **Feedback:** 0–95% [42%], saturated so it can't run away. **Mix:** dry to wet [35%], smoothed.

### Reverb · `synth-patch-reverb`

Panel 988 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Size | `knobs` | 0 to 1 | `0.6` (size 0.6) | size 0 → 1 |
| Damping | `knobs` | 0 to 1 | `0.4` (damping 0.4) | damping 0 → 1 |
| Mix | `knobs` | 0 to 1 | `0.3` (mix 0.3) | mix 0 → 1 |

Inputs: `Reverb Input`  
Outputs: `Reverb Output`

- A plate after Dattorro (1997): four input diffusers into a figure-eight tank of two modulated branches, heard through fourteen taps summed to mono.
- **Size:** the decay, short room to long plate [0.6]; stable at full. **Damping:** how fast the highs die [0.4]. **Mix:** dry to wet [30%], smoothed.

## Utilities

### Glide · `synth-patch-glide`

Panel 591 × 750 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Time | `knobs` | 0 to 1 | `0.6` (time 0.072 s) | time 0.0005 → 2 s, exp |

Inputs: `Glide Input`  
Outputs: `Glide Output`

- **Glide Output** follows **Glide Input**, taking **Time** to get within 1% of each new value (an exponential, RC-style glide). Patch it between a pitch source and a V/Oct input for portamento, or use it on any CV as a slew limiter.
- **Time:** off to 2 s, exponential [about 70 ms]. Fully left, there's no glide.

### Attenuverter · `synth-patch-attenuverter`

Panel 637 × 1348 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Amount A | `knobs` | −1 to 1 | `1` (amount 1) | amount -1 → 1 |
| Offset A | `knobs` | −1 to 1 | `0` (offset 0) | offset -1 → 1 |
| Amount B | `knobs` | −1 to 1 | `1` (amount 1) | amount -1 → 1 |
| Offset B | `knobs` | −1 to 1 | `0` (offset 0) | offset -1 → 1 |

Inputs: `A Input`, `B Input`  
Outputs: `A Output`, `B Output`

- Two channels, A and B. Each output = input × **Amount** + **Offset**, smoothed.
- **Amount A/B:** −1 to +1 [+1]. Below center it inverts.
- **Offset A/B:** −1 to +1 [0]. With nothing in a channel's input, its output is the offset alone, a steady CV (for pitch, 1.0 = one octave).

### Quantizer · `synth-patch-quantizer`

Panel 973 × 762 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Scale | `rotarySwitches` | `Chromatic`, `Major`, `Minor`, `Major Pentatonic`, `Minor Pentatonic`, `Blues` | `"Chromatic"` (scale 0) | scale Chromatic=0, Major=1, Minor=2, Major Pentatonic=3, Minor Pentatonic=4, Blues=5 |
| Root | `knobs` | 0 to 1, 12 steps | `0` (root C) | root 0 → 11 |

Inputs: `Quantizer Input`  
Outputs: `Quantizer Output`

- Snaps the pitch at **Quantizer Input** (V/Oct) to the nearest note of a scale and sends it to **Quantizer Output**. Halfway between two notes, it takes the lower one.
- **Scale:** Chromatic, Major, Minor (natural), Major Pentatonic, Minor Pentatonic, Blues [Chromatic].
- **Root:** C to B, a stepped knob [C], the key the scale starts on.

### Code · `synth-patch-code`

Panel 1280 × 1004 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| P1 | `knobs` | 0 to 1 | `0` (p1 0) | p1 0 → 1 |
| P2 | `knobs` | 0 to 1 | `0` (p2 0) | p2 0 → 1 |
| P3 | `knobs` | 0 to 1 | `0` (p3 0) | p3 0 → 1 |
| P4 | `knobs` | 0 to 1 | `0` (p4 0) | p4 0 → 1 |
| Code | `code` | code, a string | a wavefolder | code, the source |

Inputs: `A Input`, `B Input`, `C Input`, `D Input`  
Outputs: `Code Output`

- JavaScript that runs once per sample: inputs `a`–`d` (**A–D Input**), knobs `p[0]`–`p[3]` (**P1–P4**, 0–1), `state` (kept between samples), `t` (seconds) and `sr` (sample rate). It returns the output sample, kept within ±4.
- An error, or a loop that runs too long, stops the module with a message on its panel until the code changes.

## Drawn synths

Demo One is the docs' example drawn synth (it isn't a real instrument). It has its own keys block and its
own output, so in a rig it's heard directly until its Main Output is cabled.

### Demo One · `example-instruments-demo-one`

Panel 2268 × 1020 px.

| Control | Group | Value | Default | Engine |
| --- | --- | --- | --- | --- |
| Oscillator Range | `rotarySwitches` | `32'`, `16'`, `8'`, `4'` | `"32'"` (octave -2 oct) | octave 32'=-2, 16'=-1, 8'=0, 4'=1 |
| Oscillator Pitch | `knobs` | −1 to 1 | `0` (tune 0 st) | tune -12 → 12 st |
| Filter Cutoff | `knobs` | 0 to 1 | `0` (cutoff 20 Hz) | cutoff 20 → 20480 Hz, exp |
| Filter Resonance | `knobs` | 0 to 1 | `0` (resonance 0) | resonance 0 → 1.05 |
| Tempo | `rotaryEncoders` | turns | `0` (bpm 120 BPM) | bpm 120 + 40 per turn BPM, 30 to 300 |
| Oscillator Wave | `toggles` | `Saw`, `Triangle`, `Square` | `"Saw"` (wave 0) | wave Saw=0, Triangle=1, Square=2 |
| Oscillator Pulse Width | `knobs` | 0 to 1 | `0` (pulseWidth 50% of the cycle) | pulseWidth 0.5 → 0.95 of the cycle |
| Filter Envelope Amount | `knobs` | −1 to 1 | `0` (envAmount 0 oct) | envAmount -6 → 6 oct |
| Filter Envelope Decay | `sliders` | 0 to 1 | `0` (decay 0.05 s) | decay 0.05 → 8 s, exp |
| Hold | `buttons` | `true` / `false` | `false` (useB 0) | useB 1 when true, 0 when false |

Inputs: `Pitch CV Input`, `Cutoff CV Input`, `Gate Input`  
Outputs: `Oscillator Output`, `Envelope Output`, `Main Output`

Set by the engine or the player, so rigs leave them out: Clock Indicator (led).
