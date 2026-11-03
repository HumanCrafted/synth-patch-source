---
name: synth-patch-rigs
description: Write Synth Patch rigs (patchjson/2), several modules on a canvas cabled into a patch that plays, from a description of a sound or someone's preferences, and variants of a module (synthjson/2) when a rig needs one. Use whenever someone wants a rig, a modular patch or patch JSON for Synth Patch (synthpatch.io), e.g. "make me an acid bassline rig", "patch something generative and ambient", "a lead I can play from my keyboard", "add an LFO on the filter", "a slower LFO module", or names Synth Patch modules (oscillator, filter, VCA, sequencer, Code). Also use it to check, fix or explain a rig that won't load, has problems listed, or makes no sound.
---

# Writing Synth Patch rigs

A rig is one JSON file: synths and modules placed on a canvas (`instances`), each set by control name, and cables between their jacks. The Synth Patch app reads it exactly: a name that's off by one letter or a knob value outside its range is a problem, and that control or cable is dropped. So every name comes from the module packages, every value is checked, and the finished rig goes through `scripts/rig.py check`, which reads it the way the app does.

Rigs and the sound engine are in preview in the app; the format is stable (`patchjson/2`, version 2.0).

## Files

- **`references/module-names.md`**: every standard module's exact control and jack names, value group, range, default, engine mapping, panel size and behavior. Read it before writing any rig; it's the one file you always need.
- `references/docs/rigs.md`: the rig format, how it's read, and the Writing-a-rig checklist.
- `references/docs/engine.md`: signal levels (pitch is 1.0 per octave, 0 = middle C; audio −1 to 1; envelopes 0 to 1; gates 0 or 1) and the engine blocks, for variants.
- `references/docs/synth-package.md` (Variants, Generated synths), `controls.md`, `patches.md`, `modules.md`, `parts.md`: the rest of the 2.0 docs.
- `references/library/`: the module packages, Demo One and the parts manifest, byte for byte from the repo. `rig.py` reads them.
- `references/examples/`: the two example rigs from the docs. `examples/`: worked rigs from prompts; `examples/README.md` says what each shows.
- `scripts/rig.py`: `check`, `explain`, `value`, `controls`, `layout` and `check-synth`. Python 3, standard library only.

Everything in `references/` is regenerated from the repo by `scripts/build_reference.py`; don't edit it by hand.

## Workflow

### 1. Pin down the sound

From the request, decide: what it should sound like (bass, lead, pad, drone, percussion), **how it's played** (from the keys, by a sequence, or by itself), tempo and key if it's rhythmic or melodic, and any effects. Ask one short question only when the answer changes the patch and you can't pick a sensible default (for example, "played from the keyboard, or should it play itself?"). Otherwise choose and say what you chose.

### 2. Sketch the signal path

Rigs are built from a few standard chains. Pick them, then pick modules:

| Job | Patch |
| --- | --- |
| The voice | pitch → Oscillator `V/Oct Input` (and Filter `V/Oct Input` for key tracking); Oscillator `Saw Output` / `Square Output` / `Triangle Output` → Filter `Filter Input`; Filter `LP Output` → VCA `VCA Input` → effects → Speaker `Speaker Input` |
| Note shape | gate → Envelope `Gate Input`; `Envelope Output` → VCA `CV Input` and Filter `Envelope Input` |
| Played from keys | Keyboard `Pitch Output` and `Gate Output`. A rig with a Keyboard module is played only through it. |
| A pattern | Sequencer `Pitch Output` and `Gate Output` (its own clock, 8 steps) |
| Several parts in time | one Clock `Clock Output` → each Sequencer's `Clock Input` (their own Tempo is then ignored). Each plays step 1 on the first clock, so they stay in step. A part on the offbeat: a second Sequencer with only the even steps' gates on. Half time: Clock `÷2 Output`. |
| Plays itself | Clock `Clock Output` → Random `Clock Input` and Envelope `Gate Input`; Random `Stepped Output` → Quantizer → pitch |
| Portamento | Glide between the pitch source and the V/Oct inputs |
| Vibrato | LFO `LFO Output` → Oscillator `FM Input`, FM Amount about 0.02 |
| Filter sweep, wobble | LFO → Filter `Cutoff CV Input`. CV Amount is octaves per unit and the LFO swings ±1, so the default 0.25 (1 octave) sweeps ±1 octave; a wobble wants about 0.5 (±2 octaves) at 1–4 Hz |
| Tremolo | LFO → VCA `CV Input` with Initial Level 0.5 and CV Amount 0.5 |
| Pulse width modulation | LFO → Oscillator `PWM Input`, heard on `Square Output` |
| Drone | VCA `Initial Level` above 0 and no envelope |
| Two sources | Mixer `Input A`–`D` → `Mixer Output` |
| Space | Delay, then Reverb, between the VCA and the Speaker |
| Hats, snares | Noise → Filter `HP Output` → VCA, a short envelope from a Clock |
| Odd jobs | the Code module: per-sample JavaScript (wavefolder, ring mod `a * b`, comparator, divider) |

Every rig of modules ends at a Speaker; it's the only module you hear. Pitch goes to V/Oct inputs and gates to Gate, Clock and Run inputs, never the other way round.

### 3. Write it with exact names

Look up each module's card in `references/module-names.md` (or run `python3 scripts/rig.py controls <slug>`) and copy names exactly, including case, spaces, slashes and symbols: `V/Oct Input`, `LP Output`, `÷2 Output`, `Envelope Amount`.

```json
{
  "format": "patchjson/2",
  "name": "Short Name",
  "description": "One line: what it is and how it plays.",
  "tags": ["bass"],
  "instances": [
    { "id": "osc", "synth": "synth-patch-oscillator", "controls": { "rotarySwitches": { "Octave": "16'" } } }
  ],
  "cables": [{ "from": "osc/Saw Output", "to": "vcf/Filter Input", "color": "Signal Orange" }],
  "notes": "How to play it and what to turn."
}
```

- `id`: short, unique, lowercase kebab-case (`osc`, `vcf`, `osc-2`).
- `controls`: by group (`knobs`, `rotarySwitches`, `toggles`, `buttons`, `code`, …; the card names the group), then control name. **Leave out every control at its default.** Never set `keys` or `leds`; the player and the engine set those.
- Cables: `"<id>/<Jack Name>"`, from an output to an input. One output can feed many inputs; two cables into one input add. Color is optional; the examples use Signal Orange for audio, Control Blue for CV and Patch Green for clocks and gates.
- Put how to play it and what to tweak in `notes`.

### 4. Set values as patch values

Knobs are their travel: 0 to 1, or −1 to 1 when bipolar. Switches are position names, buttons `true`/`false`, code a string. Never write engine units (Hz, seconds, BPM) as values. Convert with:

```bash
python3 scripts/rig.py value synth-patch-filter Cutoff 800          # → 0.534
python3 scripts/rig.py value synth-patch-sequencer "Step 3" 7       # 7 semitones → 0.2917
python3 scripts/rig.py value synth-patch-delay Time 0.35            # seconds
```

Quote control names with spaces. Without the script, use the card's Engine column: a knob at `n` gives `lo + n × (hi − lo)`, or `lo × (hi / lo)^n` for exp; invert it, and for a bipolar knob write `2n − 1`. Round to 4 decimals.

Musical details that trip people up:

- **Sequencer:** one step per clock beat, so **Tempo** is steps per minute (20–300). Eighth notes at 128 BPM is Tempo 256; sixteenths only fit up to 75 BPM. Steps are 0–24 semitones above the oscillator's pitch (value = semitones ÷ 24). Rests are `"Gate N": false`. Length is a stepped knob: n steps is (n − 1) ÷ 7.
- **Pitch:** 0 is middle C. The Oscillator's Octave switch (32′ to 4′) and Tune (±12 semitones, bipolar: value = semitones ÷ 12) move it. The Keyboard's Octave sets its lowest key.
- **Key and root:** a Sequencer's steps count up from the oscillator's pitch, so set the root on the Oscillator (and any other oscillator it plays): A is Tune −3 (−0.25), F is +5. Then write steps from the scale: minor 0, 2, 3, 5, 7, 8, 10, 12; major 0, 2, 4, 5, 7, 9, 11, 12; minor pentatonic 0, 3, 5, 7, 10. For random or edited notes that must stay in key, put a Quantizer between the pitch source and the oscillators instead.
- **Random** spans −1 to 1, an octave either side, until a Quantizer snaps it to a scale (Root C to B is a 12-step knob: value = semitone ÷ 11).
- **VCA** Gain defaults to 1× at 0.5; its CV clamps at 0, so it can't ring-modulate (use Code for that).

### 5. Lay it out

Give every instance an `x`/`y` (288 dpi pixels, the panel's top left). Let the script place them, in list order, left to right with a 120 px gap, wrapping into rows:

```bash
python3 scripts/rig.py layout rig.json --row-width 7000 --write
```

So list instances in signal order: sources, voice, modulation, effects, Speaker last.

### 6. Check it

```bash
python3 scripts/rig.py check rig.json
python3 scripts/rig.py explain rig.json      # every value in Hz, s, BPM, semitones
```

`check` must end `OK` with 0 problems and 0 errors. **Problems** are what the app's reader reports (unknown names, values out of range, bad cables). **Errors** are rigs that load but can't sound (nothing reaches a Speaker, a cable joining two outputs). Fix warnings too unless they're intended (a control left at its default, panels overlapping, an envelope with no gate, a cable running input to output). Then read `explain` and confirm the numbers are what you meant.

If you can't run Python, check by hand: every slug is in `module-names.md`; every control is in its card under the right group with a value in range; every cable end is `id/Exact Jack Name`, from an output to an input; audio reaches a Speaker; every Envelope has a gate; every instance has `x`/`y`.

### 7. Hand it over

Give the rig as a `.json` file (named after the rig, kebab-case) or a JSON block, then say in a few lines what it does and what to turn. To load it in Synth Patch: open the Play canvas, then **Patch Data → Paste**, and paste the JSON. A rig with a variant needs the variant added first (below).

## Variants

A variant is a small package that `extends` a standard module and lists only what differs: one more output, a different range. Write one only when composing standard modules can't do the job. An Attenuverter gives offsets, inversion and scaling. A Sequencer with one gate on divides a clock. The Code module covers most per-sample logic.

The rules (`references/docs/synth-package.md`, Variants; `examples/slow-lfo.synth.json` is a complete one):

- `"format": "synthjson/2"`, `"extends": "<module slug>"`, and its own identity: `slug`, `name`, `manufacturer`, `model`, `description`. Use the person's name or `Custom` as manufacturer and a slug that doesn't start with `synth-patch-` (that prefix is the library's own): `custom-slow-lfo`.
- `control_config`: entries added or replaced **by key** (the module's keys are its names in kebab-case: `lfo-output`); `null` removes one. A new jack is `{ "name": "Unipolar Output", "type": "output-jack", "config": { "type": "output", "graphic": "parts:jack-hex-small" } }`; a new knob uses `"parts:knob-moog-large"` or another part from `references/library/parts.json`.
- `panel` replaces the base's whole panel: list every control, the new ones included.
- `engine.blocks` is an object keyed by block `id`. A block's fields replace the base block's, so `params` lists every param it keeps. A new id adds a block, with its `type`. `null` removes one. Block types, params, inputs and outputs are in `references/docs/engine.md`. Internal connections are `"block.port"` (`"lfo.out"`).
- Removing a control means removing whatever in the engine uses it.

Check it, then check the rig against it:

```bash
python3 scripts/rig.py check-synth my-variant.synth.json
python3 scripts/rig.py check rig.json --synth my-variant.synth.json
```

Hand over both files. In the Play canvas, the variant goes in first with **Add module → Paste synth JSON** (it's kept in that browser), then the rig with Patch Data → Paste. The rig names the variant by its slug.

## Other synths

A rig can include any synth the app has, by slug (`moog-grandmother`, or the app's exact `moog-grandmother-a81c28`). This skill knows the standard modules and Demo One only. For another synth, get its `synth.json` (or exact control and jack names) from the person, and pass it with `--synth` so `check` can verify the names. Without it, `check` warns that the instance is unchecked; say so when you hand the rig over. A drawn synth with its own engine output is heard directly until its output jack is cabled; one without an engine shows but is silent.

## Fixing a rig

Run `check` on it and fix each line. The usual causes are a jack name off by case or spacing, a value in engine units (`"Cutoff": 800`), a control in the wrong group (a switch under `knobs`), a cable from an input, or no Speaker. `check` suggests the closest jack name. For "it loads but it's silent", run `explain` and follow the chain from the pitch and gate sources to the Speaker.
