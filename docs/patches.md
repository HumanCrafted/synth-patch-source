# Patches (`patchjson`)

A patch is one JSON file: which synth it's for, where each control is set, and which jacks are cabled together. Controls and cables are referenced by **name**, the same names as in the synth's `control_config`, so a patch can be written by hand from a patch sheet.

This page is the one-synth patch, the shape `patchjson/1` defined. `patchjson/2` adds [rigs](rigs.md): several synths on a canvas, cabled together, each set the way this page describes. A one-synth patch is a valid `patchjson/2` file, and a rig reads it as a rig of one. The app writes one-synth patches as `patchjson/1` and rigs as `patchjson/2`; readers accept either version string on either shape.

The examples: [`examples/patches/example-instruments/demo-one`](../examples/patches/example-instruments/demo-one).

## Folder

```
patches/<manufacturer>/<model>/          same path as the synth's package
  <patch-slug>.json
  audio/<patch-slug>.<ext>               optional recording
patches/packs/<manufacturer>-<model>.json
```

## A patch

```json
{
  "format": "patchjson/1",
  "name": "Clocked Pluck",
  "synth": "example-instruments-demo-one",
  "description": "A pitched pluck that retriggers from the clock and sweeps its own pitch. Source: Demo One Owner's Guide, by A. Example.",
  "tags": ["pluck", "sequence"],
  "controls": {
    "knobs": { "Oscillator Pitch": -0.25, "Filter Cutoff": 0.556, "Filter Envelope Amount": -0.4 },
    "rotarySwitches": { "Oscillator Range": "8'" },
    "toggles": { "Oscillator Wave": "Square" },
    "sliders": { "Filter Envelope Decay": 0.15 },
    "rotaryEncoders": { "Tempo": 2.5 },
    "buttons": { "Hold": true },
    "leds": { "Clock Indicator": "On" }
  },
  "cables": [
    { "from": "Envelope Output", "to": "Pitch CV Input", "color": "Signal Orange" },
    { "from": "Oscillator Output", "to": "Cutoff CV Input", "color": "Control Blue" }
  ],
  "notes": "With **Hold** on, the clock keeps retriggering the envelope at the **Tempo** rate.",
  "source": {
    "title": "Demo One Owner's Guide, Patch Ideas: Clocked Pluck (p. 12)",
    "url": "https://example.com/demo-one/owners-guide.pdf",
    "author": "A. Example",
    "license": "CC-BY-4.0",
    "attribution": "Patch idea from the Demo One Owner's Guide, by A. Example (CC BY 4.0).",
    "retrieved": "2026-10-19"
  }
}
```

| Field         | Required                   | Value                                                                                                                                                                                                                         |
| ------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `format`      | yes                        | `"patchjson/1"` or `"patchjson/2"`                                                                                                                                                                                            |
| `name`        | yes                        | Up to 255 characters.                                                                                                                                                                                                         |
| `synth`       | yes                        | The synth's slug ([below](#the-synth-slug)).                                                                                                                                                                                  |
| `description` | yes                        | One line for patch lists, up to 1000 characters. For a patch from somewhere else, end with where it came from: `Source: Demo One Owner's Guide, by A. Example.` Leave out the "by" part when the author is the source itself. |
| `tags`        |                            | Lowercase strings.                                                                                                                                                                                                            |
| `controls`    |                            | Control values by group, then by name (below).                                                                                                                                                                                |
| `cables`      |                            | Connections between jacks (below).                                                                                                                                                                                            |
| `notes`       |                            | Markdown. How to play it, what to tweak.                                                                                                                                                                                      |
| `audio`       |                            | Recordings of the patch (below).                                                                                                                                                                                              |
| `source`      | for patches from elsewhere | Where it came from and the right to use it (below).                                                                                                                                                                           |
| `about`       |                            | What the app adds when it copies a patch: `created_with`, `created_at`, `updated_at`, `created_by`, `remixed_from`, `is_public`. Readers ignore it.                                                                           |

## The synth slug

The app writes a synth's exact slug, with the id suffix it has in the app: `"synth": "moog-grandmother-a81c28"`. A plain slug without the suffix (`"moog-grandmother"`, the package's own `slug`) also works. It matches a synth with exactly that slug first, and otherwise the synth whose slug minus its `-xxxxxx` suffix is the same. If more than one synth matches, the reader takes the first one and says so.

## Controls

Each group holds `"Control Name": value` pairs:

| Group | Control type | Value |
| --- | --- | --- |
| `knobs` | `knob` | 0 to 1, or −1 to 1 when the knob is `bipolar` |
| `rotaryEncoders` | `rotary-encoder` | number of turns, any value |
| `sliders` | `slider` | 0 to 1, or −1 to 1 when `bipolar` |
| `slidersAngled` | `slider-angled` | 0 to 1, or −1 to 1 when `bipolar` |
| `wheels` | `wheel` | 0 to 1, or −1 to 1 when `bipolar` |
| `joysticks` | `joystick` | `{ "x": n, "y": n }`, each −1 to 1, +x right, +y up |
| `toggles` | `toggle` | one of its `positionNames` |
| `rotarySwitches` | `rotary-switch` | one of its `positionNames` |
| `buttons` | `button` | `true` / `false` |
| `keys` | `key` | `true` / `false` |
| `leds` | `led` | one of its `positionNames`, or `true` / `false` |
| `touchPads` | `touch-pad` | `true` / `false` |
| `code` | `code` | the code, as a string (new in 2.0) |

**Leave out controls at their default.** Ranges and encoders default to 0 (fully counterclockwise for a unipolar knob, centered for a bipolar one), switches and LEDs to their first position, joysticks to center, code empty, and everything else to off, unless the synth gives a control its own `default`. A loaded patch sets every control the file doesn't mention to its default.

Each control type, its range and how to convert clock positions from a patch sheet are in [Controls](controls.md).

## Cables

```json
"cables": [
  { "from": "Envelope Output", "to": "Pitch CV Input", "color": "Signal Orange" },
  { "from": "Envelope Output", "to": "Cutoff CV Input" }
]
```

`from` names an output jack and `to` names an input jack. A synth can use one name for several control types (a Trigger button, a Trigger input and a Trigger output), and the jack type decides which is meant. Two cables into one input is allowed but worth a second look: on the hardware it needs a mult or stackable cables.

`color` is optional. Leave it out to use the synth's `cableStyle` color, which follows the light or dark theme. Otherwise use one of the app's named colors:

| Name | Hex | Name | Hex |
| --- | --- | --- | --- |
| Black | `#000000` | Synth Green | `#00FF1A` |
| Dark Grey | `#3A3A3A` | Oscilloscope Green | `#00FF88` |
| Mid Grey | `#7A7A7A` | Level Yellow | `#FFD700` |
| Light Grey | `#E5E5E3` | Amp Orange | `#FF9D00` |
| Signal Orange | `#FF6B35` | Vintage Amber | `#FF8000` |
| Control Blue | `#0055A4` | Clipping Red | `#FF3333` |
| Patch Green | `#00A878` | Frequency Blue | `#00BFFF` |
| Warning Yellow | `#FFB700` | Mod Blue | `#00AAFF` |
| | | Modular Pink | `#FF6EC7` |

## Audio

```json
"audio": [
  {
    "file": "audio/clocked-pluck.mp3",
    "author": "A. Example",
    "license": "CC-BY-4.0",
    "source": "Recorded for Synth Patch"
  }
]
```

`file` is relative to the patch file. Every recording needs its own `author` and `license`, separate from the patch's.

## Source

`source` is required for any patch you didn't make yourself. A patch needs a clear right to use it before it's added.

| Field | Required | |
| --- | --- | --- |
| `title` | yes | The work and the page: `Demo One Owner's Guide, Patch Ideas: Clocked Pluck (p. 12)`. |
| `url` | yes | Where to find it. |
| `author` | yes | Who made the patch. |
| `license` | yes | An [SPDX ID](https://spdx.org/licenses/) (`CC0-1.0`, `CC-BY-4.0`, `MIT`), or `permission` when the owner granted it directly. |
| `permission` | with `permission` | A link or note showing the grant. |
| `attribution` | when the license asks | The credit text the patch page must show. |
| `retrieved` | yes | The date it was copied, `YYYY-MM-DD`. |

## Packs

A pack bundles every patch for one synth into one file, so a whole set imports at once:

```json
{
  "format": "patchjson/1",
  "name": "Example Instruments Demo One patches",
  "synth": "example-instruments-demo-one",
  "description": "3 patches for the Example Instruments Demo One from https://example.com/demo-one/owners-guide.pdf.",
  "authors": ["A. Example"],
  "patches": [ { "format": "patchjson/1", "name": "Basic Bass", "...": "..." } ]
}
```

- `patches` holds full patch files, at most 100 per pack.
- `synth` is the synth's slug, by [the slug rule](#the-synth-slug), so the import picks the synth by itself. A patch without its own `synth` takes the pack's.
- `description` and `authors` are for people reading the pack.

The import keeps each patch's name, description, notes, controls and cables, and drops `tags` and `source`. The patch page shows notes rather than the description, so in a pack each patch's notes start with the description's summary and end with a linked source line, and the credit survives the import:

```
Source: [Demo One Owner's Guide](https://example.com/demo-one/owners-guide.pdf), p. 12, by A. Example.
```

Build packs from the patch files rather than editing them by hand. [The example pack](../examples/patches/packs/example-instruments-demo-one.json) was built that way.

## Reading a patch

Patches come mostly from the app itself, from packs we prepare and from agents, so reading is exact:

- **Names match exactly.** A control's name must match one in its group's control type, and a jack's name must match a jack. Case, spacing and control keys (`circle_12`) don't count. `from` looks for an output first and `to` for an input first, so a synth with an input and an output of the same name still works.
- **Values must fit.** A knob, fader or wheel is a number in its range, a switch or a multi-state LED is one of its `positionNames`, buttons, keys, touch pads and plain LEDs are `true` or `false`, a joystick is inside its gate, and code is a string. Nothing is clamped or guessed.
- **Cable colors** are a name from the table or `#RRGGBB`.

Anything else is a problem: an unknown group, name, jack or color, or a value that doesn't fit. The app lists the problems. Pasting a patch loads the rest, with each of those controls at its default and each of those cables left out. Saving through the app's API (the admin import, saving a rig) refuses anything with problems.

Off-panel cables (to a labeled point above the panel) are being retired in favor of [rigs](rigs.md). They can't be named by jack, so Copy JSON writes them as `{ "from": "Main Output", "to": "To mixer", "external": true }`, and pasting skips them with a note.

### Older shapes the app wrote

Patches the app wrote before this format settled still read:

- `"synthesizer"` instead of `"synth"`, `"format": "patchmd/1"`, and `name` and `notes` inside a `"patch": { ... }` object.
- The app's saved form: values wrapped as `{ "value": 0.5, "key": "circle_3" }`, `{ "pressed": true }` or `{ "active": true }` (some wheels wrapped several times over), joysticks as `{ "x", "y", "key" }`, and cables kept inside `controls` with `fromKey` and `toKey` control keys and a `customColor` hex.
- A cable color that's the synth's own cable color (or black or white when it has none) means the default color, since older exports wrote it on every cable.
- A cable from an input to an output. The app writes output first.
