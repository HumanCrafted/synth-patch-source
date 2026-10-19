# Controls

Every entry in `control_config` (except `cableStyle`) is a control:

```json
"circle_14": { "x": 470, "y": 720, "name": "Oscillator Pulse Width", "type": "knob", "config": { } }
```

`x`, `y` is the control's center in frame pixels. `type` is one of the 14 types below, and `config` depends on it. Each type also says what a [patch](patches.md) stores for it, and under which group name.

| Type | Patch group | Patch value |
| --- | --- | --- |
| [`knob`](#knob) | `knobs` | number, 0 to 1 or −1 to 1 |
| [`rotary-encoder`](#rotary-encoder) | `rotaryEncoders` | number of turns |
| [`slider`](#slider) | `sliders` | number, 0 to 1 or −1 to 1 |
| [`slider-angled`](#slider-angled) | `slidersAngled` | number, 0 to 1 or −1 to 1 |
| [`wheel`](#wheel) | `wheels` | number, 0 to 1 or −1 to 1 |
| [`joystick`](#joystick) | `joysticks` | `{ "x": n, "y": n }` |
| [`toggle`](#toggle) | `toggles` | position name |
| [`rotary-switch`](#rotary-switch) | `rotarySwitches` | position name |
| [`button`](#button) | `buttons` | `true` / `false` |
| [`key`](#key) | `keys` | `true` / `false` |
| [`led`](#led) | `leds` | state name, or `true` / `false` |
| [`touch-pad`](#touch-pad) | `touchPads` | `true` / `false` |
| [`input-jack`](#jacks) | (cables) | |
| [`output-jack`](#jacks) | (cables) | |

## Size is a square

Knobs, encoders, sliders, toggles, rotary switches, buttons, jacks and joysticks draw their graphic into a `size` × `size` square (`width` for sliders), centered on the control. The graphic is scaled to fit, so `size` is the graphic's **long side**. A 48 × 123 slide switch with `size` 48 renders at 39%.

LEDs, touch pads, keys and wheels have separate width and height fields instead.

## Graphics

`graphic` is one image. `graphics` is a list, one image per state, in the order the states are listed. Each entry is `{ "url", "filename" }` or a plain path string; see [Graphic references](synth-package.md#graphic-references).

The examples use Demo One's files where it has that control. For the types it doesn't have (wheel, joystick, key, touch pad, angled fader), the file names are made up.

---

## knob

```json
"config": {
  "size": 212,
  "graphic": { "url": "assets/demo1-knob-212w=default.svg", "filename": "demo1-knob-212w=default.svg" },
  "minDegree": -150,
  "maxDegree": 150,
  "valueRange": "unipolar",
  "sensitivity": 0.005
}
```

| Field | Default | |
| --- | --- | --- |
| `size` | | Canvas size in frame pixels. |
| `graphic` | | The knob drawn pointing at 12 o'clock. |
| `minDegree`, `maxDegree` | −135, 135 | Rotation at each end of travel, in degrees clockwise from 12 o'clock. Measured from the panel's scale. ±150° is the most common. |
| `valueRange` | `unipolar` | `unipolar` (0 to 1) or `bipolar` (−1 to 1, 0 at center). Bipolar is for knobs whose center is zero: tuning, ± amount or depth, attenuverters. |
| `sensitivity` | 0.005 | Value change per pixel of drag. |

The knob turns to `minDegree + n × (maxDegree − minDegree)`, where `n` is the value for unipolar knobs and `(value + 1) / 2` for bipolar ones.

**Patch value:** a number from 0 to 1, or −1 to 1 for bipolar knobs. Default 0.

### From a patch sheet

Patch sheets usually give clock positions. Each hour on the clock is 30°, so for a knob at angle `a` (degrees clockwise from 12):

```
value = (a − minDegree) / (maxDegree − minDegree)          unipolar
value = 2 × (a − minDegree) / (maxDegree − minDegree) − 1  bipolar
```

For the common ±150° knob, which runs 7:00 to 5:00:

| Clock | 7:00 | 8:00 | 9:00 | 10:00 | 11:00 | 12:00 | 1:00 | 2:00 | 3:00 | 4:00 | 5:00 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Unipolar | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1 |
| Bipolar | −1 | −0.8 | −0.6 | −0.4 | −0.2 | 0 | 0.2 | 0.4 | 0.6 | 0.8 | 1 |

A knob with a 0 to 10 dial is just value = dial ÷ 10.

## rotary-encoder

An endless knob.

```json
"config": {
  "size": 91,
  "graphic": { "url": "assets/demo1-knob-91w=default.svg", "filename": "demo1-knob-91w=default.svg" },
  "sensitivity": 0.005
}
```

**Patch value:** a number of turns. 1 is one full turn clockwise (360°), and it can go past 1 or below 0. Default 0.

## slider

A fader. The track is panel art in the frame; the component is just the cap.

```json
"config": {
  "width": 198,
  "graphic": { "url": "assets/demo1-slider-198w=default.svg", "filename": "demo1-slider-198w=default.svg" },
  "orientation": "vertical",
  "travelRange": 255,
  "valueRange": "unipolar"
}
```

| Field | Default | |
| --- | --- | --- |
| `width` | | The cap's square canvas. |
| `graphic` | | The cap, centered on its canvas. |
| `orientation` | | `vertical` or `horizontal`. |
| `travelRange` | | How far the cap's center moves end to end, in frame pixels: the track length minus the cap length. |
| `valueRange` | `bipolar` | `unipolar` or `bipolar`. Bipolar is for center-zero faders like fine tune and pan. |

`x`, `y` is the middle of the travel. Positive values move the cap up (vertical) or right (horizontal), so a unipolar fader at 0 sits at the bottom or left end.

**Patch value:** a number from 0 to 1, or −1 to 1 for bipolar faders. Default 0.

## slider-angled

A fader on a diagonal.

```json
"config": {
  "width": 57,
  "graphic": "assets/demo1-slider-angled-57w.svg",
  "travelRange": 214,
  "angle": 20
}
```

Like `slider`, plus `angle`: degrees from horizontal, counterclockwise positive. A displacement `d` along the track puts the cap at `x + d·cos(angle)`, `y − d·sin(angle)`. `valueRange` defaults to `bipolar`.

**Patch value:** as for `slider`.

## wheel

A pitch or mod wheel: a tall wheel graphic that slides behind a fixed window.

```json
"config": {
  "graphic": { "url": "assets/demo1-wheel-89w-1239h=default.svg", "filename": "demo1-wheel-89w-1239h=default.svg" },
  "graphicWidth": 89,
  "graphicHeight": 1239,
  "windowWidth": 92,
  "windowHeight": 625,
  "maskRadius": 18,
  "travelRange": 534,
  "sensitivity": 0.005,
  "springReturn": false,
  "valueRange": "bipolar"
}
```

| Field | |
| --- | --- |
| `graphic`, `graphicWidth`, `graphicHeight` | The wheel's full surface, taller than the window. |
| `windowWidth`, `windowHeight`, `maskRadius` | The visible window, with rounded corners. `x`, `y` is its center. |
| `travelRange` | Total travel of the graphic in frame pixels. It moves `value × travelRange / 2`, up for positive values. |
| `springReturn` | Return to center on release. Keep it `false` so a patch can show the wheel held. |
| `valueRange` | Defaults to `bipolar`. Pitch wheels are bipolar, mod wheels unipolar. |

**Patch value:** a number from 0 to 1, or −1 to 1. Default 0.

## joystick

```json
"config": {
  "size": 80,
  "graphic": { "url": "assets/demo1-joystick-80w=default.svg", "filename": "demo1-joystick-80w=default.svg" },
  "travelRadius": 102,
  "gate": "circle",
  "axes": {
    "x": { "name": "Pitch", "springReturn": false },
    "y": { "name": "Mod", "springReturn": false }
  }
}
```

| Field | Default | |
| --- | --- | --- |
| `size`, `graphic` | | The cap only. The base ring is panel art, and `x`, `y` is its center. |
| `travelRadius` | 50 | Distance from center to the cap's center at full throw: (ring diameter − cap diameter) / 2. |
| `gate` | `circle` | `circle` or `square`, the shape the stick can move within. |
| `axes` | | A label and `springReturn` for each axis. Labels can change later; patches store `x` and `y`. |

The app draws a stem from the base center to the cap.

**Patch value:** `{ "x": 0.3, "y": -0.5 }`, each −1 to 1, with +x right and +y up. In a circular gate, x² + y² must be at most 1. A missing axis is 0. Default `{ "x": 0, "y": 0 }`.

## toggle

A two- or three-position switch.

```json
"config": {
  "size": 96,
  "positions": 3,
  "positionNames": ["Saw", "Triangle", "Square"],
  "graphics": [
    { "url": "assets/demo1-toggle-96w=left.svg", "filename": "demo1-toggle-96w=left.svg" },
    { "url": "assets/demo1-toggle-96w=middle.svg", "filename": "demo1-toggle-96w=middle.svg" },
    { "url": "assets/demo1-toggle-96w=right.svg", "filename": "demo1-toggle-96w=right.svg" }
  ]
}
```

`positions` is 2 or 3. `positionNames` are the panel's labels, in the same order as `graphics` (left to right, or top to bottom). A click flips a two-position toggle; a three-position toggle steps first → middle → last → middle.

**Patch value:** one of the `positionNames`. Default the first.

## rotary-switch

A stepped selector.

```json
"config": {
  "size": 224,
  "positions": 4,
  "positionNames": ["32'", "16'", "8'", "4'"],
  "switchMode": "reciprocating",
  "graphics": [
    { "url": "assets/demo1-rotary-switch-224w=neg45.svg", "filename": "demo1-rotary-switch-224w=neg45.svg" },
    { "url": "assets/demo1-rotary-switch-224w=neg15.svg", "filename": "demo1-rotary-switch-224w=neg15.svg" },
    { "url": "assets/demo1-rotary-switch-224w=15.svg", "filename": "demo1-rotary-switch-224w=15.svg" },
    { "url": "assets/demo1-rotary-switch-224w=45.svg", "filename": "demo1-rotary-switch-224w=45.svg" }
  ]
}
```

Each position has its own pre-rotated graphic, named by its angle. `positionNames` go counterclockwise first, matching `graphics`. `switchMode` is `reciprocating` (1 → 2 → 3 → 4 → 3 → 2, like a real stepped switch) or `continuous` (1 → 2 → 3 → 4 → 1).

**Patch value:** one of the `positionNames`. Default the first.

## button

```json
"config": {
  "size": 76,
  "buttonType": "latching",
  "graphics": [
    { "url": "assets/demo1-button-76w=inactive, color=grey.svg", "filename": "demo1-button-76w=inactive, color=grey.svg" },
    { "url": "assets/demo1-button-76w=active, color=grey.svg", "filename": "demo1-button-76w=active, color=grey.svg" }
  ]
}
```

`graphics` is `[inactive, active]`. `buttonType` is `latching` (click to toggle) or `momentary` (pressed only while held).

**Patch value:** `true` for pressed. Default `false`.

## key

One keyboard key. Each key is its own control.

```json
"config": {
  "keyType": "natural",
  "keyWidth": 270,
  "keyHeight": 1596,
  "behaviorType": "latching",
  "graphics": [
    { "url": "assets/demo1-natural-key-270w-1596h=cut-right, State=inactive.svg", "filename": "demo1-natural-key-270w-1596h=cut-right, State=inactive.svg" },
    { "url": "assets/demo1-natural-key-270w-1596h=cut-right, State=active.svg", "filename": "demo1-natural-key-270w-1596h=cut-right, State=active.svg" }
  ]
}
```

`keyType` is `natural` or `accidental`. Accidentals are drawn on top of naturals. A natural key's outline depends on its note: C and F are `cut-right`; D, G and A `cut-both`; E and B `cut-left`; a top C is `full`. `behaviorType` is `latching` (so a patch can show held notes) or `momentary`. Keys are named by note and octave, counting octaves from 0: `C0`, `C#0`, `D0`.

**Patch value:** `true` for held. Default `false`.

## led

```json
"config": {
  "width": 52,
  "height": 52,
  "ledMode": "continuous",
  "numStates": 2,
  "positionNames": ["Off", "On"],
  "graphics": [
    { "url": "assets/demo1-led-52w=inactive.svg", "filename": "demo1-led-52w=inactive.svg" },
    { "url": "assets/demo1-led-52w=active.svg", "filename": "demo1-led-52w=active.svg" }
  ]
}
```

One graphic per state, unlit first. `numStates` is 2 or 3, with a name for each (`["Off", "On"]`, `["Off", "Dim", "On"]`, `["Off", "Green", "Red"]`). A click steps through the states: `continuous` wraps around, `reciprocating` bounces back (Off → Dim → On → Dim).

Older packages use `size` in place of `width`/`height`, or a single `graphic` with a `color` (a CSS color) drawn over it when lit.

**Patch value:** one of the `positionNames`, or `true`/`false` for an LED without them. Default the first state.

## touch-pad

```json
"config": {
  "width": 137,
  "height": 137,
  "graphics": [
    { "url": "assets/demo1-touch-pad-137w=inactive.svg", "filename": "demo1-touch-pad-137w=inactive.svg" },
    { "url": "assets/demo1-touch-pad-137w=active.svg", "filename": "demo1-touch-pad-137w=active.svg" }
  ]
}
```

`graphics` is `[inactive, active]`. Older packages use `size`, or a single `graphic` with an `activeColor`.

**Patch value:** `true` for touched. Default `false`.

## Jacks

`input-jack` and `output-jack` share one config:

```json
"config": {
  "size": 106,
  "type": "output",
  "graphic": { "url": "assets/demo1-jack-106w=output.svg", "filename": "demo1-jack-106w=output.svg" }
}
```

`type` repeats the control type: `input` or `output`. MIDI and USB ports are jacks too: MIDI In is an input; MIDI Out/Thru and USB are outputs.

Jacks have no value. A patch connects them with [cables](patches.md#cables), from an output to an input.
