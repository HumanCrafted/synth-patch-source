# Parts

The parts library: generic control graphics that a [synth package](synth-package.md#parts) can name instead of shipping its own SVGs. Every [standard module](modules.md) is drawn from it. The files are in [`parts/`](../parts): one SVG per state, and `parts.json`, the manifest that turns a part name into files.

The library holds primitives rather than one part per instrument (a drum pad is a square button, an encoder is a knob): round, square, rect and triangle buttons; Moog-style, solid, ring and trim knobs; and so on. Real synths keep their own exact controls in their packages' `assets/`.

All art is at 288 dpi, the same scale as synth frames, in the Synth Patch colors.

## Names

- **Part names** say what a part is, not how big it's drawn: `<type>-<style>[-<size or positions>]`, like `knob-moog-large`, `toggle-slide-2pos`, `jack-hex-small`. A redraw at a new size keeps the name, and a name never changes once packages use it.
- **Packages** refer to a part as `"parts:<name>"`, or `"parts:<name>:<variant>"` for a variant other than the default (`parts:led-round:green`, `parts:button-round:dark`).
- **Files** are named after the Figma component set and variant, `<set>=<variant>.svg`, with sets named `sp-<part>-<size>w` (`sp-knob-moog-212w=default.svg`), plus `-<h>h` for parts that aren't square (`sp-wheel-89w-1239h`).

Readers also accept the names the first drafts used: `knob-large`, `knob-small`, `jack`, `toggle-3`, `rotary-switch-4`, `led` and `button` mean `knob-moog-large`, `knob-solid-small`, `jack-hex-small`, `toggle-bat-3pos`, `rotary-switch-pointer-4pos`, `led-round` and `button-square`.

## `parts.json`

```jsonc
"led-round": {
  "type": "led",                       // the control type it's for
  "set": "sp-led-round-52w",           // the Figma component set
  "size": 52,                          // the control's size: the graphic's long side
  "states": ["inactive", "active"],    // the order of the files
  "variants": { "red": ["sp-led-round-52w=inactive, color=default.svg", "sp-led-round-52w=active, color=red.svg"], "...": [] },
  "default": "red",
  "from": "demo1-led-52w (as gm-led-52w)"   // the synth component it was drawn from
}
```

- Parts with a single look have `files` (one per state) instead of `variants` and `default`.
- Keys and other parts that aren't square have a `height`.
- `config` holds control settings the graphic implies, like a wheel's window and travel or a joystick's travel radius. A control's own config wins.
- A jack part has two files, `input` and `output`; the control's type picks one.
- Two types aren't app controls yet: `connector` (rear-panel MIDI and USB, which synths draw as jacks) and `graphic` (the speaker grill, used by the [`graphic`](controls.md#graphic) control).

## The library

| Part | Type | Size | States | Variants | Copied from |
|---|---|---|---|---|---|
| `knob-moog-large` | knob | 212 | default | | demo1-knob-212w (as gm-knob-212w) |
| `knob-moog-small` | knob | 138 | default | | muse-knob-138w |
| `knob-solid-large` | knob | 153 | default | | edge-knob-153w |
| `knob-solid-small` | knob | 91 | default | | demo1-knob-91w (as gm-knob-91w) |
| `knob-ring-large` | knob | 153 | default | | coast-knob-153w |
| `knob-ring-small` | knob | 117 | default | | strega-knob-117w |
| `knob-trim` | knob | 48 | default | | min-knob-45w |
| `rotary-switch-pointer-4pos` | rotary-switch | 224 | neg45, neg15, 15, 45 | | demo1-rotary-switch-224w (as gm-rotary-switch-224w) |
| `rotary-switch-pointer-6pos` | rotary-switch | 224 | neg75 … 75 | | m-6pos-rotary-switch-224w |
| `button-square` | button | 76 | inactive, active | light, grey, dark, lit-amber | demo1-button-76w |
| `button-round` | button | 96 | inactive, active | light, grey, dark, lit-amber | sub37-round-button-96w |
| `button-rect` | button | 132 | inactive, active | light, grey, dark, lit-amber | sub37-button-132w-76h |
| `button-triangle` | button | 102 | inactive, active | each color, left and right | m32-button-102w |
| `touch-round` | touch-pad | 137 | inactive, active | | strega-touch-137w |
| `touch-square` | touch-pad | 107 | inactive, active | | strega-touch-107w |
| `toggle-bat-3pos` | toggle | 96 | left, middle, right | | demo1-toggle-96w (as gm-toggle-96w) |
| `toggle-bat-2pos` | toggle | 96 | left, right | | the same, without the middle |
| `toggle-slide-3pos` | toggle | 123 | up, middle, down | | 2600-toggle-48w-122h (the house slide switch) |
| `toggle-slide-2pos` | toggle | 123 | up, down | | the same, without the middle |
| `toggle-mini-2pos` | toggle | 40 | up, down | | edge-toggle-40w |
| `toggle-rocker` | toggle | 256 | left or bottom pressed, right or top pressed | black, blue, orange; horizontal and vertical | redrawn from the Minimoog Model D's d-toggle-256w |
| `slider` | slider | 198 | default | | demo1-slider-198w (as gm-slider-198w); the cap only |
| `wheel` | wheel | 89 × 1239 | default | | gm-wheel-slider-89w-1239h |
| `joystick` | joystick | 80 | default | | mlxd-joystick-79w; the cap only |
| `jack-hex-small` | jack | 106 | input, output | | demo1-jack-106w (as gm-jack-106w), 3.5 mm |
| `jack-hex-large` | jack | 150 | input, output | | gm-jack-150w, 1/4″ |
| `jack-round-small` | jack | 81 | input, output | | mf-jack-81w |
| `jack-round-large` | jack | 138 | input, output | | mf-jack-138w |
| `jack-solid` | jack | 98 | input, output | | edge-jack-98w |
| `jack-pin` | jack | 21 | input, output | | Bastl Kastle Arp (pin socket) |
| `connector-midi` | connector | 194 | default | | gm-jack-midi-194w |
| `connector-usb-a` | connector | 160 | default | | muse-jack-usb-a-160w |
| `connector-usb-b` | connector | 150 | default | | gm-jack-usb-150w |
| `connector-usb-c` | connector | 110 | default | | messenger-jack-usb-110w |
| `led-round` | led | 52 | inactive, active | red, amber, yellow, green, blue | demo1-led-52w (as gm-led-52w) |
| `led-square` | led | 87 | inactive, active | red, amber, yellow, green, blue | coast-led-dynamics-87w |
| `led-bar` | led | 23 × 106 | inactive, active | red, amber, yellow, green, blue | control-led-23w-106h |
| `key-natural-cut-left` / `-cut-right` / `-cut-both` / `-full` | key | 270 × 1596 | inactive, active | | gm-natural-key-270w-1596h |
| `key-accidental` | key | 135 × 1046 | inactive, active | | gm-accidental-key-135w-1046h |
| `speaker-grill` | graphic | 400 | default | round, square | new |

### Notes

- **Colors:** buttons press to a flat fill 50% toward white (dark presses to Mid Grey); `lit-amber` lights up with the LED recipe instead, like the Sub 37's lit buttons. LEDs are flat fills in the Pure Red, Amber, Warm Glow, Oscilloscope Green and Cool Blue styles over a Light Grey off state.
- **Rockers:** each variant is named for its pressed side, which is flat at body width. The raised side reads as nearer the eye: its face (the darker tone) widens from the pivot to a light ridge line, then the far end narrows back to body width, since it's on the same plane as the body. The Model D's own `d-toggle-256w` still uses the old three-band art.
- **Encoders** use any knob part; only the behavior differs.
- **Angled sliders** (the app's `slider-angled`) use `slider` plus an `angle`.
- **Not in the library yet:** a 3-position mini toggle, the slider track (the slider is only the cap, so a module panel has no track to draw), and lit fader caps.
- **Speaker grill:** a field of round holes, hex-packed (22 px holes at a 32 px pitch) with no outline, in a round or square field. It follows the grill on Auxy's keyboard and the Dieter Rams / Braun look; no other synth in the library has a speaker. The Speaker module uses the round grill at the top of its panel.

## The Figma components

The parts are Figma component sets in Synth Patch's working file, each with `placement` and `empty` variants like every synth component. Every other variant is exported as an SVG. The [Figma template](figma-template.md) shows the same conventions on Demo One's components.
