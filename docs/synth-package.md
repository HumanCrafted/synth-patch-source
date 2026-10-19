# Synth package (`synthjson/1`)

A synth package is a folder. `synth.json` describes the synth and lists every control. `assets/` holds the panel art and the control graphics.

The example: [`examples/synths/example-instruments/demo-one`](../examples/synths/example-instruments/demo-one).

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

Folder names are lowercase kebab-case. Only `synth.json` and `assets/` are part of the format. `source/` and the README are for whoever builds the synth.

## synth.json

```json
{
  "format": "synthjson/1",
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
  "control_config": { "circle_1": { "...": "..." }, "cableStyle": { "...": "..." } }
}
```

| Field                               | Required | Value                                                                                                                                                                                                     |
| ----------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `format`                            | yes      | `"synthjson/1"`                                                                                                                                                                                           |
| `slug`                              |          | `<manufacturer>-<model>`, lowercase kebab-case. Patches name their synth by this slug.                                                                                                                    |
| `name`                              | yes      | Display name: manufacturer and model.                                                                                                                                                                     |
| `manufacturer`, `model`             | yes      |                                                                                                                                                                                                           |
| `description`                       |          | One line, facts only, in the form "X with A, B and C". Usually the manual's cover subtitle.                                                                                                               |
| `category`                          |          | `Synthesizer`, `Semi-Modular`, `Modular`, `Drum Machine`, `Sequencer` or `Other`.                                                                                                                         |
| `tags`                              |          | Lowercase strings. In use so far: `analog`, `hybrid`, `monophonic`, `duophonic`, `paraphonic`, `polyphonic`, `semi-modular`, `eurorack`, `sequencer`, `percussion`, `drums`, `bass`, `looper`, `classic`. |
| `manufacturer_url`                  |          | The product page.                                                                                                                                                                                         |
| `manual_url`                        |          | The user manual, or `null` when the maker publishes none (say why in `source.no_manual`).                                                                                                                 |
| `is_listed`, `verified`, `featured` |          | App listing flags. New synths start with all three `false`.                                                                                                                                               |
| `frame`, `thumbnail`                | yes      | Paths into `assets/` (see [Assets](#assets)).                                                                                                                                                             |
| `placement`                         |          | Path into `assets/`.                                                                                                                                                                                      |
| `created_at`, `updated_at`          |          | ISO 8601 timestamps. Present on packages exported from the app.                                                                                                                                           |
| `source`                            |          | Where the package came from. Free-form; see below.                                                                                                                                                        |
| `control_config`                    | yes      | The controls (see [Control config](#control-config)).                                                                                                                                                     |

`source` takes one of two shapes so far. A synth built in Figma records where its art lives (`figma_file`, `figma_section`, `placement_node`). A package exported from the app records its database record: `db_id`, `db_slug` (the slug plus the database's short ID, like `example-instruments-demo-one-a1b2c3`), `exported_from` and `exported_at`. Either can carry `no_manual`.

A package is rejected on import when:

- `format` isn't `synthjson/1`
- `name`, `manufacturer` or `model` is missing or blank
- `frame` or `thumbnail` isn't a path starting with `assets/` (or contains `..`)
- `control_config` is missing or has no controls
- a control has no numeric `x`/`y` or no `name`
- `tags` isn't a list of strings

## Coordinates

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

Inside `control_config`, a graphic is an object with the path relative to the package folder and the file name:

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

`control_config` is an object. Each control sits under a key `circle_1`, `circle_2`, and so on, plus one `cableStyle` entry:

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

- **Keys** follow the placement dots' numbering (above). They identify a control within the package; their order means nothing else.
- **`name`** must be unique within its type. Patches find controls by type and name, so **never rename a control once people have saved patches for the synth.** Names are the section and the parameter, with abbreviations spelled out: "Filter Cutoff", "Oscillator Range", "Clock Indicator". Jacks end in Input or Output: "Pitch CV Input", "Main Output".
- **`type`** is one of the 14 control types in [Controls](controls.md). `config` depends on it.
- **`cableStyle`** sets how patch cables look on this synth: `color` (hex), `width` (stroke in frame pixels, 1 to 50) and `curvature` (0 for straight to 10 for a high arch). The usual is `{ "color": "#000000", "width": 22, "curvature": 6 }`. A cable drawn in the default color follows the theme: black in light mode, white in dark.

## Updating a package

A package for a synth that's already live is imported as an update. The app compares every asset by content (SHA-256), keeps the ones that didn't change, and uploads the rest. It reports each control as added, removed, renamed, retyped, moved or reconfigured.

Keep keys and names stable. Moving a control or changing its graphic is safe. Renaming it orphans that control's value in every saved patch.
