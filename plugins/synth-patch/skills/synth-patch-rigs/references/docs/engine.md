<!-- Copied from docs/engine.md in synth-patch-source by scripts/build_reference.py. Edit the original. -->

# Engine

A synth package's optional `engine` section says how the synth sounds. Without one, a synth is interactive but silent. With one, it plays wherever the app shows it, and in [rigs](rigs.md) its jacks carry real signals to other synths.

An engine is data, not code. It lists signal **blocks** (an oscillator, a ladder filter, an envelope…), binds the synth's controls to their parameters, and says which jacks reach which block inputs and outputs. The blocks themselves are Synth Patch's own DSP, described below. So a module with one more input is a JSON edit.

The examples: [Demo One](../library/synths/example-instruments-demo-one.json), a drawn synth with an engine, and the [standard modules](modules.md), each a generated synth with one.

## The `engine` section

```json
"engine": {
  "kind": "blocks",
  "blocks": [
    { "id": "keys", "type": "keyboard" },
    {
      "id": "vco",
      "type": "vco",
      "params": {
        "octave": { "control": "Oscillator Range", "steps": { "32'": -2, "16'": -1, "8'": 0, "4'": 1 } },
        "tune": { "control": "Oscillator Pitch", "range": [-12, 12] },
        "wave": { "control": "Oscillator Wave", "steps": { "Saw": 0, "Triangle": 1, "Square": 2 } }
      },
      "inputs": {
        "pitch": "keys.pitch",
        "pitchCv": { "jack": "Pitch CV Input" }
      },
      "outputs": { "out": "Oscillator Output" }
    }
  ],
  "leds": {},
  "output": "vco.out"
}
```

| Field | Required | Value |
| --- | --- | --- |
| `kind` | | `"blocks"`, the default. `"module"` is [reserved](#reserved-manufacturer-engines). |
| `blocks` | yes | The blocks, run in list order once per sample (below). |
| `leds` | | LEDs lit by signals (below). |
| `output` | | What reaches the speakers: `"block.port"`, or a list of them, summed. |

### Blocks

| Field | Required | Value |
| --- | --- | --- |
| `id` | yes | Unique within the synth. Other blocks refer to its ports as `"<id>.<port>"`. |
| `type` | yes | A [block type](#block-types). |
| `params` | | Block parameter → a fixed number, or a [binding](#bindings) to a control. Parameters left out keep the block's default. |
| `inputs` | | Block input → `"block.port"` for a fixed internal connection, or `{ "jack": "<input jack name>", "normal": "block.port" }` for one that can be patched. |
| `outputs` | | Block output → the name of the output jack it appears on. |

**Inputs.** A jack input hears whatever is cabled into the jack. With nothing cabled, it hears its `normal`, or 0 when it has none. A cable into the jack replaces the normal, as on hardware. Two cables into one input add together. Demo One's envelope is normalled to its keyboard-and-clock trigger, so it plays with no cables, and a cable into Gate Input takes over.

**Order.** Blocks run in list order. An input that reads a block later in the list gets its value one sample late, which is how feedback works. In a rig, synths run in signal order, so a cable from one synth to the next arrives in the same sample.

### Bindings

A binding turns a control's patch value (see [Controls](controls.md)) into a block parameter, in the block's own units:

| Binding | For | Result |
| --- | --- | --- |
| `{ "control": "Cutoff", "range": [20, 20000], "curve": "exp" }` | knobs, faders, wheels | The control's travel mapped onto the range: 0 to 1, or −1 to 1 for a bipolar control. `curve` is `linear` (default) or `exp` (equal ratios per step, for frequencies and times; both ends must be above 0). |
| `{ "control": "Octave", "steps": { "8'": 0, "4'": 1 } }` | switches, multi-state LEDs | The number for the control's position name. A position not listed gives 0. |
| `{ "control": "Tempo", "turns": { "base": 120, "perTurn": 40, "min": 30, "max": 300 } }` | rotary encoders | `base + turns × perTurn`, kept within `min` and `max`. |
| `{ "control": "Hold" }` | buttons, keys, touch pads, plain LEDs | `true` is 1, `false` is 0. |
| `{ "control": "Code" }` | `code` | The code, as a string. |
| `{ "control": "Rate" }` | any number | The patch value unchanged. |
| `0.5` | | A fixed value. |

The `control` is a control **name**, as in patches. A stepped knob (`steps` in its config) still binds with `range`: Sequencer's Length knob has 8 steps and binds `"range": [1, 8]`.

### LEDs

`leds` lights LED controls from signals:

```json
"leds": { "Clock Indicator": { "source": "clock.out", "on": "On", "off": "Off" } }
```

The LED shows its `on` position while `source` is above 0.5, and `off` otherwise.

### Output

`output` names what reaches the speakers. A synth with its own speaker (most hardware) sets it; a module that's only heard through its jacks (a filter, an LFO) leaves it out, and only the Speaker module sets it among the [standard modules](modules.md).

When an `output` source also appears on an output jack and that jack is cabled, it stops going to the speakers directly: as on hardware, it's heard only through the cable. Demo One sends `vca.out` to the speakers and to its Main Output jack, so cabling Main Output into a delay sends it through the delay only.

What reaches the speakers then passes through a DC blocker, the page's volume and a limiter, none of which an engine can change.

### Notes

A `keyboard` block takes notes from the computer keyboard, a MIDI device, and the synth's own keys:

- A `key` control plays its `note` (a MIDI note number, 60 = middle C). Without one, a key named like `C0` or `F#1` plays from C3 up: `C0` is MIDI 48, `C1` is 60.
- A `button` with a `note` in its config plays that note too, for synths whose keys are buttons. While it has a `note` it acts as a held key and patches don't store it.

In a rig, notes go to the synths that have keys on their panel (a Keyboard module, a synth with a keybed). Only when no synth in the rig has keys do they go to every synth with a `keyboard` block. See [Rigs: sound](rigs.md#sound).

### Reserved: manufacturer engines

`"kind": "module"` is reserved for a manufacturer's own engine shipped inside the package: an AudioWorklet module that the package maps the panel onto with the same bindings. It would only load from packages Synth Patch has reviewed, from makers who share their engines. No reader loads one in 2.0: a synth whose engine has `"kind": "module"` reads as silent. The shape will be set in a later version.

## Signals

Every input and output carries one number per sample, with the same levels on every block, so any cable does what you'd expect.

| Signal | Level | Hardware equivalent |
| --- | --- | --- |
| Pitch (V/Oct) | 1.0 per octave, 0 = middle C (C4, 261.63 Hz) | 1 V/oct, 0 V = C4 |
| Audio | −1 to 1 | about ±5 V |
| Bipolar CV (LFO, Random) | −1 to 1 | ±5 V |
| Unipolar CV (envelopes) | 0 to 1 | 0 to 10 V |
| Gates, triggers, clocks | 0 or 1; read as high above 0.5, acting on the rising edge | 0 / 10 V |

- **Pitch inputs add,** so a CV of 1 into a pitch input shifts it up an octave. V/Oct inputs are never scaled; other CV inputs have an amount parameter.
- **Two cables into one input add,** like a passive mixer. One output can feed any number of inputs.
- Level parameters (gains, mixes, amounts) are smoothed over a few milliseconds, so turning a knob doesn't step the sound.

## Block types

Parameters are in the block's units (Hz, seconds, octaves), which is what a binding should produce. Defaults apply to parameters an engine leaves out.

### `keyboard`

Notes from the computer keyboard, MIDI and the synth's keys. Monophonic, last-note priority. A new note drops the gate for one sample, so envelopes retrigger even when playing legato. Before any note it holds middle C, so a keyboard nobody plays adds nothing to a pitch input it feeds.

| Param | Default | |
| --- | --- | --- |
| `transpose` | 0 | octaves added to `pitch`; bind it to an Octave switch |

| Output | |
| --- | --- |
| `pitch` | the current note plus `transpose` |
| `gate` | 1 while any key is held |

### `clock`

One pulse per beat at 50% duty, with divided outputs that rise with it.

| Param | Default | |
| --- | --- | --- |
| `bpm` | 120 | beats per minute |

| Input | |
| --- | --- |
| `reset` | a rising edge restarts the beat and the divisions |
| `run` | while patched and low, the clock stops with its outputs low; it starts on the beat when `run` goes high. Unpatched, it runs. |

| Output | |
| --- | --- |
| `out` | the beat |
| `div2`, `div4` | every second and fourth beat |

### `lfo`

| Param | Default | |
| --- | --- | --- |
| `rate` | 2 | Hz |
| `shape` | 0 | 0 sine, 1 triangle, 2 saw, 3 square |
| `rateCvAmount` | 1 | octaves of rate per unit at `rateCv` |

Input `rateCv`; output `out`, −1 to 1.

### `vco`

Saw, triangle and pulse. The saw and pulse edges are band-limited (PolyBLEP), the triangle's corners too (PolyBLAMP).

| Param | Default | |
| --- | --- | --- |
| `octave` | 0 | octaves added to the pitch |
| `tune`, `fine` | 0 | semitones added to the pitch |
| `wave` | 0 | which wave `out` carries: 0 saw, 1 triangle, 2 pulse |
| `pulseWidth` | 0.5 | fraction of the cycle, for the pulse |
| `fmAmount` | 1 | octaves per unit at `pitchCv` |
| `pwmAmount` | 1 | fraction of the cycle per unit at `pwCv` |

| Input | |
| --- | --- |
| `pitch` | V/Oct, never scaled |
| `pitchCv` | added to the pitch, scaled by `fmAmount` |
| `pwCv` | added to the pulse width, scaled by `pwmAmount`; the width stays within 5–95% |
| `sync` | hard sync: the cycle restarts each time it rises through 0 |

| Output | |
| --- | --- |
| `out` | the wave `wave` selects, for synths with a wave switch |
| `saw`, `triangle`, `square` | each wave on its own |

At `octave` 0 with nothing at `pitch`, it plays middle C.

### `noise`

| Param | Default | |
| --- | --- | --- |
| `color` | 0 | 0 white, 1 pink (−3 dB/octave), 2 brown (−6 dB/octave) |

Output `out`, about −1 to 1.

### `random`

Sample and hold. On each rising `trigger` it takes the `sample` input, or with nothing patched there a new random value from −1 to 1. Give `trigger` a clock as its normal so it runs on its own until something is patched in.

| Param | Default | |
| --- | --- | --- |
| `smooth` | 0.1 | seconds for `smooth` to get within 1% of each new value |

| Output | |
| --- | --- |
| `stepped` | the value, held until the next trigger |
| `smooth` | the same value, gliding |

### `sequencer`

Up to eight steps, one per rising `clock`. The first clock plays step 1.

| Param | Default | |
| --- | --- | --- |
| `step1`–`step8` | 0 | semitones, rounded |
| `gate1`–`gate8` | 1 | 1 plays the step, 0 rests |
| `length` | 8 | steps, 1 to 8 |
| `gateLength` | 50 | percent of the clock period the gate stays high; 100 ties into the next step. Until a period is measured, the gate follows the clock. |

| Input | |
| --- | --- |
| `clock` | advances a step on each rising edge |
| `reset` | a rising edge makes the next clock play step 1; a clock up to 1 ms before the reset counts as arriving with it |
| `run` | while patched and low, clocks are ignored and the gate stays low |

| Output | |
| --- | --- |
| `pitch` | the current step in octaves (semitones ÷ 12); add it to a pitch input |
| `gate` | high on steps that play |
| `s1`–`s8` | 1 on the current step, for step lights |

### `ladder`

A four-pole (24 dB/octave) ladder: zero-delay-feedback stages with saturation in the feedback, at 2× oversampling. It self-oscillates, in tune, from `resonance` about 1.

| Param | Default | |
| --- | --- | --- |
| `cutoff` | 1000 | Hz |
| `resonance` | 0 | 0 to about 1.05 |
| `envAmount` | 0 | octaves of cutoff per unit at `env`; negative closes the filter |
| `keyTrack` | 1 | octaves of cutoff per octave at `pitch`; 1 tracks exactly |
| `cvAmount` | 3 | octaves of cutoff per unit at `cutoffCv` |

| Input | |
| --- | --- |
| `in` | audio |
| `pitch` | for key tracking |
| `env` | scaled by `envAmount` |
| `cutoffCv` | scaled by `cvAmount` |

| Output | |
| --- | --- |
| `out` | low-pass |
| `hp` | 24 dB high-pass, mixed from the same stages, so resonance works on both |

### `decay-env`

Fires on a rising gate: a 2 ms attack, then an exponential fall.

| Param | Default | |
| --- | --- | --- |
| `decay` | 0.5 | seconds to fall to 1% |

Input `gate`; output `out`, 0 to 1.

### `adsr`

Linear attack; exponential decay and release. A new gate restarts the attack from the current level.

| Param | Default | |
| --- | --- | --- |
| `attack` | 0.005 | seconds |
| `decay` | 0.3 | seconds to get within 1% of `sustain` |
| `sustain` | 0.6 | 0 to 1 |
| `release` | 0.4 | seconds to get within 1% of 0 |

Input `gate`; output `out`, 0 to 1.

### `vca`

`out = in × (cv × cvAmount + bias, kept within 0 to 1) × gain`. Linear and DC-coupled, so it works on CV as well as audio. It doesn't ring-modulate: the CV stops at 0.

| Param | Default | |
| --- | --- | --- |
| `gain` | 1 | |
| `bias` | 0 | added to the scaled CV; 1 opens the VCA with nothing patched |
| `cvAmount` | 1 | |

Inputs `in`, `cv`; output `out`.

### `mixer`

Inputs `a`, `b`, `c`, `d`; params `levelA`–`levelD` (default 1); output `out`, the weighted sum. DC-coupled.

### `attenuverter`

`out = in × amount + offset`. Below 0, `amount` inverts. With nothing patched in, `out` is the offset alone, a steady CV.

| Param | Default | |
| --- | --- | --- |
| `amount` | 1 | −1 to 1 |
| `offset` | 0 | −1 to 1 |

Input `in`; output `out`.

### `quantizer`

Snaps the pitch at `in` to the nearest note of a scale. Halfway between two notes, it takes the lower one.

| Param | Default | |
| --- | --- | --- |
| `scale` | 0 | 0 chromatic, 1 major, 2 natural minor, 3 major pentatonic, 4 minor pentatonic, 5 blues |
| `root` | 0 | the key, 0 (C) to 11 (B), rounded |

Input `in`; output `out`.

### `slew`

Glide: `out` follows `in`, taking `time` to get within 1% of each new value. Put it between a pitch source and a pitch input for portamento.

| Param | Default | |
| --- | --- | --- |
| `time` | 0 | seconds; 0 passes `in` straight through |

### `delay`

Up to 2 seconds, with saturated feedback so it can't run away. Changing `time` glides, like tape.

| Param | Default | |
| --- | --- | --- |
| `time` | 0.3 | seconds |
| `feedback` | 0.4 | 0 to 0.95 |
| `mix` | 0.35 | 0 dry to 1 wet |

Input `in`; output `out`.

### `reverb`

A plate after Dattorro (1997): four input diffusers into a figure-eight tank of two modulated branches, summed to mono.

| Param | Default | |
| --- | --- | --- |
| `size` | 0.6 | 0 to 1, the decay |
| `damping` | 0.4 | 0 to 1, how fast the highs die away |
| `mix` | 0.3 | 0 dry to 1 wet |

Input `in`; output `out`.

### `gate-or`

Output `out` is high while `a` is high, or `b` is high and `useB` is 1 (default 1). Demo One uses it for its Hold button: the keyboard or the clock triggers the envelope.

### `code`

Runs code once per sample. Bind `code` to a [`code` control](controls.md#code).

| | |
| --- | --- |
| Inputs | `a`, `b`, `c`, `d` |
| Params | `p1`–`p4` (default 0; usually knobs, 0 to 1), `code` (the source; default `return a;`) |
| Output | `out`, kept within −4 to 4 |

The code is the body of a JavaScript function of `(a, b, c, d, p, state, t, sr)`, and returns the output sample:

| Name | |
| --- | --- |
| `a`–`d` | this sample's inputs |
| `p` | `[p1, p2, p3, p4]` |
| `state` | an object that keeps its values between samples, reset when the code changes |
| `t` | seconds since the block started |
| `sr` | the sample rate |

```js
// 16-step sequencer: one step per rising clock edge into a
const notes = [0, 3, 7, 10, 12, 7, 3, 15, 0, 5, 7, 12, 10, 7, 3, 5];
if (a > 0.5 && !state.high) state.step = ((state.step ?? -1) + 1) % 16;
state.high = a > 0.5;
return notes[state.step ?? 0] / 12; // octaves
```

The code runs in the audio thread: no page, no network, no timers. Safeguards:

- A syntax or runtime error stops the block (it outputs 0) and the error is shown on the control until the code changes.
- Every loop gets a check in its header. Once loops have run for 250 ms in one block of samples, the block stops with "A loop ran too long, so this module stopped."
- `eval`, `Function` (and the other function constructors) and `WebAssembly` aren't available, so code can't make new, unchecked code while it runs.
- Volume and the limiter are on the page's audio graph, after the engine, where code can't reach them. If the engine stops answering for about a second, the page cuts it off from the speakers.

## Not in 2.0

Blocks a recreation of real hardware will want: a state-variable filter (low, band and high pass), a wavefolder, ring modulation, AD/ASD envelope modes, a clock divider beyond ÷4, and polyphony (a `voices` setting). Each is an addition: engines written for 2.0 keep working.
