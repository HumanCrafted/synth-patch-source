<!-- Copied from docs/synth-package.md in synth-patch-source by scripts/build_reference.py. Edit the original. -->

# Synth package (`synthjson/2`)

A synth package is a folder. `synth.json` describes the synth and lists every control. A synth comes one of two ways:

- **Drawn:** panel art (a frame SVG) with every control placed on it by `x`/`y`, and the control graphics in `assets/`. This is how real hardware is built, where the panel art is the point.
- **Generated:** no panel art. `panel` lists the controls in rows, the app lays them out, and the graphics come from the shared [parts library](parts.md). A generated synth is only `synth.json`, so a person, a script or an assistant can write one, and change it by editing JSON.

Either kind can have an [`engine`](engine.md) that says how it sounds.

The examples: [Demo One](https://github.com/HumanCrafted/synth-patch-source/blob/main/examples/synths/example-instruments/demo-one), a drawn synth with an engine, and the [standard modules](../library/modules), all generated.

## Versions

`synthjson/2` is `synthjson/1` plus generated synths, parts, variants, the `code` and `graphic` control types and the `engine` section. Every `synthjson/1` package is a valid `synthjson/2` package, and readers of `/2` accept both. The version moved to 2 because a generated package (no frame) breaks readers that only know `/1`.

| | `synthjson/1` | `synthjson/2` |
| --- | --- | --- |
| `frame`, `thumbnail` | required | required for a drawn synth; absent for a generated one |
| Control `x`, `y` | required | required with a frame; absent without one |
| Control keys | `circle_1`, `circle_2`, … | any stable ID; drawn synths keep `circle_N` |
| Graphics | paths into `assets/` | paths into `assets/`, or a part like `"parts:knob-moog-large"` |
| `panel` | | generated synths: sections and rows |
| `extends` | | [variants](#variants) of a generated synth |
| `engine` | | optional: [how it sounds](engine.md) |
| Control types | 14 | 16: adds [`code`](controls.md#code) and [`graphic`](controls.md#graphic) |

## Folder

```
synths/<manufacturer>/<model>/
  synth.json
  assets/
    demo1-frame-2268w.svg
    demo1-placement-2268w.svg
    demo1-thumbnail-2268w.png
    demo1-thumbnail-2268w-dark.png
    demo1-knob-212w=default.svg
    ...
  source/      optional: manuals, working files, the script that writes synth.json
  README.md    optional: notes and a build log
```

Folder names are lowercase kebab-case. Only `synth.json` and `assets/` are part of the format. `source/` and the README are for whoever builds the synth. A generated synth that uses only parts has no `assets/`:

```
modules/synth-patch-filter/
  synth.json
```

## synth.json

```json
{
  "format": "synthjson/2",
  "slug": "example-instruments-demo-one",
  "name": "Example Instruments Demo One",
  "manufacturer": "Example Instruments",
  "model": "Demo One",
  "description": "Fictional Semi-Modular Synthesizer with One Oscillator, Low-Pass Filter, Decay Envelope and 6-Point Patch Bay",
  "category": "Semi-Modular",
  "tags": ["analog", "semi-modular"],
  "manufacturer_url": "https://example.com/demo-one",
  "manual_url": null,
  "is_listed": false,
  "verified": false,
  "featured": false,
  "frame": "assets/demo1-frame-2268w.svg",
  "thumbnail": "assets/demo1-thumbnail-2268w.png",
  "placement": "assets/demo1-placement-2268w.svg",
  "source": { "figma_section": "Demo One", "no_manual": "Fictional synth; there is no manual." },
  "control_config": { "circle_1": { "...": "..." }, "cableStyle": { "...": "..." } },
  "engine": { "...": "..." }
}
```

| Field                               | Required | Value                                                                                                                                                                                                     |
| ----------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `format`                            | yes      | `"synthjson/2"` (or `"synthjson/1"` for a package with none of the `/2` additions)                                                                                                                       |
| `slug`                              |          | `<manufacturer>-<model>`, lowercase kebab-case. Patches name their synth by this slug ([the slug rule](patches.md#the-synth-slug)).                                                                       |
| `name`                              | yes      | Display name: manufacturer and model.                                                                                                                                                                     |
| `manufacturer`, `model`             | yes      |                                                                                                                                                                                                           |
| `description`                       |          | One line, facts only, in the form "X with A, B and C". Usually the manual's cover subtitle.                                                                                                               |
| `category`                          |          | `Synthesizer`, `Semi-Modular`, `Modular`, `Drum Machine`, `Sequencer` or `Other`.                                                                                                                         |
| `tags`                              |          | Lowercase strings. In use so far: `analog`, `hybrid`, `monophonic`, `duophonic`, `paraphonic`, `polyphonic`, `semi-modular`, `eurorack`, `sequencer`, `percussion`, `drums`, `bass`, `looper`, `classic`. |
| `manufacturer_url`                  |          | The product page.                                                                                                                                                                                         |
| `manual_url`                        |          | The user manual, or `null` when the maker publishes none (say why in `source.no_manual`).                                                                                                                 |
| `is_listed`, `verified`, `featured` |          | App listing flags. New synths start with all three `false`.                                                                                                                                               |
| `frame`, `thumbnail`                | drawn    | Paths into `assets/` (see [Assets](#assets)). Both or neither: a package without them is generated.                                                                                                       |
| `placement`                         |          | Path into `assets/`. Drawn synths only.                                                                                                                                                                   |
| `panel`                             | generated | The layout (see [Generated synths](#generated-synths)).                                                                                                                                                  |
| `extends`                           |          | The slug of the generated synth this one is a [variant](#variants) of.                                                                                                                                    |
| `created_at`, `updated_at`          |          | ISO 8601 timestamps. Present on packages exported from the app.                                                                                                                                           |
| `source`                            |          | Where the package came from. Free-form; see below.                                                                                                                                                        |
| `control_config`                    | yes      | The controls (see [Control config](#control-config)).                                                                                                                                                     |
| `engine`                            |          | How it sounds (see [Engine](engine.md)).                                                                                                                                                                  |

`source` takes one of two shapes so far. A synth built in Figma records where its art lives (`figma_file`, `figma_section`, `placement_node`). A package exported from the app records its database record: `db_id`, `db_slug` (the slug plus the database's short ID, like `example-instruments-demo-one-a1b2c3`), `exported_from` and `exported_at`. Either can carry `no_manual`.

The rules for rejecting a package are under [Reading a package](#reading-a-package).

## Coordinates

Drawn and generated synths share one scale, **288 dpi**, so a generated module sits next to a drawn synth at true relative size.

The frame is drawn at **288 dpi**, so 1 px is 1/288 in. Its width is the manufacturer's spec width: mm ÷ 25.4 × 288. Demo One is 200 mm wide, so 2268 px.

- The origin is the top left, with y pointing down. Units are frame pixels (the frame SVG's `viewBox`).
- A control's `x`, `y` is its **center**. The app draws each graphic centered on that point.
- The frame is the whole unit as the manual draws it: end caps or cheeks, the panel, and the rear connector panel if it has one. Keyboard synths are drawn from the top, keybed included.

## Assets

| File | What it is |
| --- | --- |
| `<prefix>-frame-<W>w.svg` | The panel art with no controls. |
| `<prefix>-placement-<W>w.svg` | The panel art plus one 15 px `#FF00FF` dot at each control's center. |
| `<prefix>-thumbnail-<W>w.png` | The panel with every control in its default state, at frame width, transparent background. |
| `<prefix>-thumbnail-<W>w-dark.png` | The same on `#0A0A0A`, for dark mode. Not referenced from `synth.json`. |
| `<variant name>.svg` | One file per control state. |

**The frame is plain outlines and specific filled areas.** Mid Grey strokes and fills on a transparent background, text converted to outlines, no white fills or panel backgrounds. The app's own background shows through, so one frame works in light and dark mode. Labels printed on a solid bar are knocked out of the bar rather than drawn in white.

**The placement SVG is where control positions come from.** The app's upload wizard finds the magenta dots by color and creates one control per dot, numbered top to bottom and then left to right (dots less than 10 px apart vertically count as one row). So the dots must sit exactly on the control centers, and `x`/`y` in `synth.json` match them.

**Control graphics are drawn on their own canvas, centered.** Knobs, jacks, toggles, buttons, rotary switches, encoders, joysticks and sliders are drawn in a `size` × `size` square (see [Size is a square](controls.md#size-is-a-square)). LEDs, touch pads, keys and wheels have their own width and height.

### File names

Control graphics are named after their Figma component variant:

```
<prefix>-<part>-<W>w[-<H>h]=<variant>.svg

demo1-knob-212w=default.svg
demo1-jack-106w=input.svg
demo1-toggle-96w=left.svg
demo1-rotary-switch-224w=neg45.svg
demo1-button-76w=active, color=grey.svg
```

- `<prefix>` is a short name for the synth (`demo1`, `dfam`, `m32`). Shared parts keep the prefix of the synth they were drawn for.
- `<W>w` is the canvas width in frame pixels, and `<H>h` the height when it differs.
- After `=` comes the variant: `default`, `input`/`output`, `inactive`/`active`, `left`/`middle`/`right`, `up`/`middle`/`down`, a rotary switch's angle (`neg45`, `neg15`, `15`, `45`), or several properties separated by commas (`active, color=grey`, `full, State=inactive`).

Spaces, commas and `=` are fine in file names. `synth.json` references them exactly.

### Graphic references

Inside `control_config`, a graphic is a [part](#parts), or an object with the path relative to the package folder and the file name:

```json
"graphic": { "url": "assets/demo1-knob-212w=default.svg", "filename": "demo1-knob-212w=default.svg" }
```

Older packages use a plain path string (`"graphic": "assets/LED unlit.svg"`). Both are valid. When the app imports a package, it uploads each file and swaps `url` for the uploaded file's address.

### Colors

| Name | Hex | Used for |
| --- | --- | --- |
| Mid Grey | `#7A7A7A` | All panel art in the frame |
| Dark Grey | `#3A3A3A` | Knob, jack, switch and fader bodies |
| Light Grey | `#E5E5E3` | Knob caps, unlit LEDs |
| Placement Dot | `#FF00FF` | Placement dots only |
| Off White - Dark | `#0A0A0A` | Background of the dark thumbnail |

A pressed button's `active` graphic is the same shape with a flat fill 50% toward white (`#939393` → `#C9C9C9`). A black body goes to Mid Grey. A shadow alone isn't enough to read as pressed.

## Control config

`control_config` is an object. Each control sits under a key, plus one `cableStyle` entry. A drawn synth's keys are `circle_1`, `circle_2`, and so on:

```json
"control_config": {
  "circle_2": {
    "x": 470,
    "y": 330,
    "name": "Oscillator Pitch",
    "type": "knob",
    "config": {
      "size": 212,
      "graphic": { "url": "assets/demo1-knob-212w=default.svg", "filename": "demo1-knob-212w=default.svg" },
      "minDegree": -150,
      "maxDegree": 150,
      "sensitivity": 0.005,
      "valueRange": "bipolar"
    }
  },
  "circle_6": {
    "x": 1760,
    "y": 330,
    "name": "Pitch CV Input",
    "type": "input-jack",
    "config": { "size": 106, "type": "input", "graphic": { "url": "assets/demo1-jack-106w=input.svg", "filename": "demo1-jack-106w=input.svg" } }
  },
  "cableStyle": { "color": "#000000", "width": 22, "curvature": 6 }
}
```

- **Keys** identify a control within the package. A drawn synth's follow the placement dots' numbering (above). A generated synth's are any stable ID; the standard modules use the name in kebab-case (`"cutoff"`, `"filter-input"`). Patches never use keys.
- **`name`** must be unique within its type. Patches find controls by type and name, so **never rename a control once people have saved patches for the synth.** Names are the section and the parameter, with abbreviations spelled out: "Filter Cutoff", "Oscillator Range", "Clock Indicator". Jacks end in Input or Output: "Pitch CV Input", "Main Output".
- **`type`** is one of the 16 control types in [Controls](controls.md). `config` depends on it. Any control can set a `default` in its config: the value it takes when a patch leaves it out.
- **`cableStyle`** sets how patch cables look on this synth: `color` (hex), `width` (stroke in frame pixels, 1 to 50) and `curvature` (0 for straight to 10 for a high arch). The usual is `{ "color": "#000000", "width": 22, "curvature": 6 }`. A cable drawn in the default color follows the theme: black in light mode, white in dark.

## Generated synths

A generated synth has no `frame`, `thumbnail`, `placement` or control `x`/`y`. The app draws a plain faceplate (outline, title, printed labels) and places the controls from `panel`. This is the Synth Patch Filter, shortened:

```json
{
  "format": "synthjson/2",
  "slug": "synth-patch-filter",
  "name": "Synth Patch Filter",
  "manufacturer": "Synth Patch",
  "model": "Filter",
  "category": "Modular",
  "tags": ["module"],
  "panel": {
    "sections": [
      { "rows": [["Cutoff", "Resonance", "Envelope Amount"], ["Key Track", "CV Amount"]] },
      { "rows": [["Filter Input", "V/Oct Input", "Envelope Input", "Cutoff CV Input", "LP Output", "HP Output"]] }
    ]
  },
  "control_config": {
    "cutoff": {
      "name": "Cutoff",
      "type": "knob",
      "config": { "graphic": "parts:knob-moog-large", "minDegree": -150, "maxDegree": 150, "sensitivity": 0.005, "default": 0.5 }
    },
    "filter-input": { "name": "Filter Input", "type": "input-jack", "config": { "type": "input", "graphic": "parts:jack-hex-small" } },
    "lp-output": { "name": "LP Output", "type": "output-jack", "config": { "type": "output", "graphic": "parts:jack-hex-small" } },
    "cableStyle": { "color": "#000000", "width": 22, "curvature": 6 }
  },
  "engine": { "...": "..." }
}
```

The whole file is [`modules/synth-patch-filter/synth.json`](../library/modules/synth-patch-filter.json).

### `panel`

| Field | Value |
| --- | --- |
| `sections` | A list, drawn top to bottom. |
| `sections[].label` | Optional. Printed as a section heading. |
| `sections[].rows` | A list of rows; each row is a list of control **names**, drawn left to right and centered. |

- Controls the panel doesn't list are added in a last row, in `control_config` order. A control listed twice is placed at its first spot.
- Each control's size comes from its part, unless its `config` sets `size`. The app spaces the controls from their sizes and labels.
- The control's `name` is printed below it (above, for jacks). Toggles print their `printedLabels` above; rotary switches and stepped knobs print them around the control. A `graphic` prints nothing.
- A row of only `key` controls is a keybed: naturals side by side, each accidental on the line after the natural a semitone below it (by `note`).
- A row of only `code` controls gives each one the panel's full width.

A generated synth has no thumbnail file; the app draws its panel wherever one is shown.

### Parts

A graphic can name a part from the [parts library](parts.md) instead of shipping its own SVG: `"parts:<name>"`, or `"parts:<name>:<variant>"` for a variant other than the part's default.

```json
"graphic": "parts:knob-moog-large",
"graphics": "parts:led-round:green"
```

A part name stands for every state of the part, so `"graphics": "parts:toggle-bat-3pos"` replaces the whole list of files. A jack part picks its input or output drawing from the jack's type. Parts carry their size, so a control that uses one needs no `size`.

Generated synths use parts for every graphic. Drawn synths can use them too, for controls that match, but real hardware usually has its own exact controls in `assets/`.

### Variants

A small change to a generated synth (one more input, a different range) doesn't need a full copy. A variant is a package of its own, with its own identity, that `extends` a generated synth and lists only what differs:

```json
{
  "format": "synthjson/2",
  "slug": "synth-patch-filter-lp",
  "name": "Synth Patch Filter LP",
  "manufacturer": "Synth Patch",
  "model": "Filter LP",
  "extends": "synth-patch-filter",
  "control_config": { "hp-output": null },
  "panel": {
    "sections": [
      { "rows": [["Cutoff", "Resonance", "Envelope Amount"], ["Key Track", "CV Amount"]] },
      { "rows": [["Filter Input", "V/Oct Input", "Envelope Input", "Cutoff CV Input", "LP Output"]] }
    ]
  },
  "engine": {
    "blocks": {
      "vcf": { "outputs": { "out": "LP Output" } }
    }
  }
}
```

- `extends` names the base package's slug. Identity fields (`slug`, `name`, `manufacturer`, `model`, `description`, …) are the variant's own; the rest come from the base.
- `control_config` entries are added or replaced by key; `null` removes one.
- `panel`, when given, replaces the base's panel. A variant that removes a control the base's panel lists needs its own `panel`.
- `engine.blocks` is an object keyed by block `id`: a block's fields replace the base block's (so `inputs` lists every input it keeps), `null` removes the block, and a new `id` adds a block at the end. `engine.leds` and `engine.output`, when given, replace the base's.
- Removing a control means removing whatever in the engine uses it too. A binding or jack left behind is a problem when the package is read.
- Only generated synths can be extended. A drawn synth's controls are tied to its artwork.

Patches name a variant by its own slug, like any synth.

## Reading a package

A package is rejected when:

- `format` isn't `synthjson/1` or `synthjson/2`
- `name`, `manufacturer` or `model` is missing or blank
- it has a `frame` but no `thumbnail`, or the other way round, or either isn't a path starting with `assets/` (or contains `..`)
- it has a `frame` and a control has no numeric `x`/`y`
- `control_config` is missing or has no controls, or a control has no `name`
- `tags` isn't a list of strings
- a graphic names a part, or a part variant, that isn't in the [parts library](parts.md)
- `panel` names a control that doesn't exist
- the `engine` names a block type that doesn't exist, binds a control that doesn't exist, or names a jack in a block's `inputs` that isn't an input jack, or in its `outputs` that isn't an output jack
- it `extends` a drawn synth or a slug the reader doesn't have

## Updating a package

A package for a synth that's already live is imported as an update. The app compares every asset by content (SHA-256), keeps the ones that didn't change, and uploads the rest. It reports each control as added, removed, renamed, retyped, moved or reconfigured.

Keep keys and names stable. Moving a control or changing its graphic is safe. Renaming it orphans that control's value in every saved patch and rig.

Adding an `engine` to a synth that has none is a safe update: it changes no control names, so saved patches keep working and start making sound.
