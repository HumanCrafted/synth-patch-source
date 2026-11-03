<!-- Copied from docs/rigs.md in synth-patch-source by scripts/build_reference.py. Edit the original. -->

# Rigs (`patchjson/2`)

A rig is a patch for several synths at once: synths and modules placed on a canvas and cabled together. Like every patch, a rig names its synths by slug and stores only their settings and cables. The synths themselves, drawn or generated, are [synth packages](synth-package.md); a rig never carries one.

`patchjson/2` is `patchjson/1` plus rigs. A [one-synth patch](patches.md) is a valid `patchjson/2` file and reads as a rig of one. Everything on this page is about rigs.

The examples: [`examples/rigs`](../examples). Each one reads with no problems and plays.

> Rigs and the sound engine are in preview in the Synth Patch app. The format is stable: rigs written to this page keep working.

## A rig

This is [`wavefolded-bass.json`](../examples/wavefolded-bass.json): a keyboard playing an oscillator, folded by a Code module, through a filter and a VCA, both opened by an envelope.

```json
{
  "format": "patchjson/2",
  "name": "Wavefolded Bass",
  "description": "A triangle wave folded by a Code module into a ladder filter, played from the keyboard.",
  "tags": ["bass", "wavefolder"],
  "instances": [
    {
      "id": "keys",
      "synth": "synth-patch-keyboard",
      "x": 0,
      "y": 0,
      "controls": { "rotarySwitches": { "Octave": "C2" } }
    },
    { "id": "osc", "synth": "synth-patch-oscillator", "x": 2392, "y": 0 },
    {
      "id": "fold",
      "synth": "synth-patch-code",
      "x": 3752,
      "y": 0,
      "controls": {
        "knobs": { "P1": 0.3 },
        "code": { "Code": "// Wavefolder: P1 is the drive\nconst drive = 1 + p[0] * 8;\nreturn Math.sin(a * drive);" }
      }
    },
    {
      "id": "vcf",
      "synth": "synth-patch-filter",
      "x": 5152,
      "y": 0,
      "controls": { "knobs": { "Cutoff": 0.45, "Resonance": 0.5, "Envelope Amount": 0.7 } }
    },
    {
      "id": "env",
      "synth": "synth-patch-envelope",
      "x": 6850,
      "y": 0,
      "controls": { "knobs": { "Decay": 0.4, "Sustain": 0.3 } }
    },
    { "id": "vca", "synth": "synth-patch-vca", "x": 8250, "y": 0 },
    { "id": "out", "synth": "synth-patch-speaker", "x": 9270, "y": 0 }
  ],
  "cables": [
    { "from": "keys/Pitch Output", "to": "osc/V/Oct Input" },
    { "from": "keys/Pitch Output", "to": "vcf/V/Oct Input" },
    { "from": "keys/Gate Output", "to": "env/Gate Input" },
    { "from": "osc/Triangle Output", "to": "fold/A Input" },
    { "from": "fold/Code Output", "to": "vcf/Filter Input", "color": "Signal Orange" },
    { "from": "env/Envelope Output", "to": "vcf/Envelope Input", "color": "Control Blue" },
    { "from": "env/Envelope Output", "to": "vca/CV Input", "color": "Control Blue" },
    { "from": "vcf/LP Output", "to": "vca/VCA Input", "color": "Signal Orange" },
    { "from": "vca/VCA Output", "to": "out/Speaker Input", "color": "Signal Orange" }
  ]
}
```

| Field | Required | Value |
| --- | --- | --- |
| `format` | yes | `"patchjson/2"` |
| `name` | | Up to 255 characters. |
| `description`, `tags`, `notes`, `source` | | As in a [patch](patches.md#a-patch). |
| `instances` | yes | The synths on the canvas (below). A rig has no top-level `synth` or `controls`. |
| `cables` | | Between instances' jacks (below). |

## Instances

| Field | Required | Value |
| --- | --- | --- |
| `id` | yes | Unique in the rig. Lowercase kebab-case by convention (`osc`, `vcf-2`). Cables use it. |
| `synth` | yes | The synth's slug, by [the slug rule](patches.md#the-synth-slug): a [standard module](modules.md)'s slug, or a synth's own slug (`moog-grandmother`, or the app's exact `moog-grandmother-a81c28`). |
| `x`, `y` | | Where the panel's top left sits on the canvas, in the same 288 dpi pixels as the panels. Default 0, so give every instance a position. |
| `scale` | | Reserved for drawing a panel larger or smaller. Readers keep it; the app doesn't use it yet. |
| `controls` | | That synth's control values, exactly as in a [one-synth patch](patches.md#controls): by group, then control name. Left-out controls are at their default. |

Values are patch values, not engine units: knobs 0 to 1 (−1 to 1 when bipolar), switches by position name, buttons `true` or `false`, and code as a string in the `code` group. Each synth's [engine](engine.md) turns them into Hz, octaves and seconds, so a rig reads like a patch sheet. The [module reference](modules.md#module-reference) says what each knob's travel covers.

**Positions.** Panels are big: the Keyboard module is 2272 px wide, Demo One 2268, the Oscillator 1240. Place instances left to right in signal order, with a gap of about 120 px, or in rows. The [module table](modules.md#the-modules) lists every module's panel size.

## Cables

In a rig, a jack is `"<instance id>/<jack name>"`:

```json
{ "from": "osc/Triangle Output", "to": "fold/A Input", "color": "Signal Orange" }
```

The instance ID is everything before the first `/`; the rest is the jack name, which may contain `/` itself (`"osc/V/Oct Input"`). The object form is also accepted, for tools that build cables:

```json
{ "from": { "instance": "osc", "jack": "Triangle Output" }, "to": { "instance": "fold", "jack": "A Input" } }
```

Otherwise cables are as in a [one-synth patch](patches.md#cables): `from` is an output jack, `to` an input jack, and `color` is optional (a name from the color table, or `#RRGGBB`). One output can feed any number of inputs, and two cables into one input add. A cable can join two jacks on the same instance (a synth's envelope into its own pitch input).

A one-synth patch read as a rig puts its synth in an instance called `main`, and its cables become `main/<jack>`.

## Sound

A rig plays when its synths have [engines](engine.md). Each instance's engine runs as its package describes, and a cable between instances carries the same signal as one inside a synth. Synths run in signal order, so a cable from one to the next arrives in the same sample; a cable that loops back arrives one sample late.

- **What you hear** is every synth's engine `output`, summed. Among the standard modules only the Speaker has one, so a rig of modules is heard through a Speaker. A drawn synth with its own `output` (Demo One) is heard directly, until its output jack is cabled: then it's heard only through the cable, as on hardware.
- **Notes** from the computer keyboard or a MIDI device go to the synths with keys on their panel: a Keyboard module, or a synth with a keybed. Only when no synth in the rig has keys do they go to every synth with a `keyboard` block. So a rig with a Keyboard module plays the modules it's cabled to through their V/Oct and gate inputs, and doesn't also play them directly.
- **Normals** make a module work before it's fully patched: the Sequencer and Random run on their own clocks, Random samples its own noise, and the VCA's Initial Level can pass sound with nothing in its CV.

An instance whose synth has no engine still shows and can be cabled, but makes no sound. [`demo-one-echo.json`](../examples/demo-one-echo.json) mixes the two kinds: Demo One, a drawn synth, played from the computer keyboard through a Delay module and a Speaker, with an LFO module sweeping its filter.

## Reading a rig

Reading is exact, as for [one-synth patches](patches.md#reading-a-patch), instance by instance. These are problems:

- a file with both `instances` and a top-level `synth`
- an instance without an `id`, or two with the same `id`
- an instance whose `synth` isn't a string (a rig can't define a synth), or names a synth the reader doesn't know
- a control or value that doesn't match the instance's synth exactly
- a cable that doesn't name `"instance/Jack Name"` at both ends, names an instance that isn't in the rig or a jack that isn't on it, or has both ends on one jack
- a cable color that isn't a name from the table or `#RRGGBB`

Pasting a rig loads the rest: an instance it can't read is left out with its cables, a bad value leaves that control at its default. Saving a rig to the app refuses one with any problem.

Fields a reader doesn't use (`tags`, `source`, …) are kept as they are.

## Writing a rig

A checklist for writing a rig by hand or with an assistant:

1. Pick synths by slug. For modules, use the [module table](modules.md#the-modules); for other synths, use the slug from their package.
2. Give every instance a short unique `id` and an `x`/`y`, laid out in signal order.
3. Use control and jack names **exactly** as the synth's package spells them, including case, spaces and slashes ("V/Oct Input", "LP Output"). Every module's names are in the [module table](modules.md#the-modules).
4. Write values as patch values: knob travel 0 to 1, switch position names from the package, booleans for buttons. Leave out controls at their default.
5. Cable from an output jack to an input jack. Send pitch to V/Oct inputs, gates to Gate inputs, audio onward, and end at a Speaker.
6. If the rig should be played from a keyboard, add a Keyboard module and cable its Pitch Output and Gate Output.

## Not in 2.0

- **The canvas view** (zoom and center) isn't stored; a rig opens fitted to the window.
- **Packs of rigs.** Packs are "every patch for one synth"; a rig spans synths.
- **Polyphony.** Every engine is monophonic.
