# Synth Patch Source

Open documentation for the file formats behind [Synth Patch](https://synthpatch.io): how a synth is described as a panel and a list of controls, how it sounds, and how a patch for one synth, or a rig of several cabled together, is written down. The synths in the app, and their patches, are kept separately.

![Demo One, the example synth](examples/synths/example-instruments/demo-one/assets/demo1-thumbnail-2268w.png)

## Formats

Version 2.0. Both formats are plain JSON (and SVG).

- **`synthjson/2`, a synth package.** A synth is **drawn** (panel art plus one SVG per control state, for real hardware) or **generated** (rows of controls drawn from a shared parts library, only JSON). Either can have an **engine** that says how it sounds. See [Synth package](docs/synth-package.md), [Controls](docs/controls.md) and [Engine](docs/engine.md).
- **`patchjson/2`, a patch.** A one-synth patch stores knobs, switches and cables by control name, so it can be written by hand from a patch sheet. A **rig** places several synths on a canvas and cables them together. See [Patches](docs/patches.md) and [Rigs](docs/rigs.md).

Every `synthjson/1` and `patchjson/1` file is valid in 2.0. The `format` field carries the version; a change that breaks existing files gets a new number. What changed is in the [changelog](CHANGELOG.md).

## The standard library

- **[Standard modules](docs/modules.md):** 18 generated synths for building rigs (oscillator, filter, envelope, VCA, sequencer, Code and more), each with an engine. In [`modules/`](modules).
- **[Parts](docs/parts.md):** the generic control graphics generated synths are drawn from, `"parts:knob-moog-large"`. In [`parts/`](parts).

## Layout

```
docs/
  synth-package.md     synthjson/2: drawn and generated synths, parts, variants
  controls.md          every control type, its config and its patch value
  engine.md            how a synth sounds: blocks, bindings, signals
  patches.md           one-synth patches: controls, cables, sources, packs
  rigs.md              patchjson/2 rigs: instances and cables between them
  modules.md           the standard modules, every control and jack
  parts.md             the parts library
  figma-template.md    the Figma Community template
modules/synth-patch-*/synth.json                 the standard modules
parts/                                           parts.json and the part SVGs
examples/
  synths/example-instruments/demo-one/           a drawn synth with an engine
  patches/example-instruments/demo-one/          three patches for it
  patches/packs/example-instruments-demo-one.json
  rigs/                                          two rigs
plugins/synth-patch/skills/synth-patch-rigs/     the rig-writing skill (below)
```

## The example synth

Demo One by Example Instruments isn't a real instrument. It was drawn in Figma for these docs, with the same components and conventions as the synths in the app: 17 controls covering knobs, a rotary switch, a toggle, a fader, an encoder, an LED, a button, and a six-jack patch bay. Every file in its package is real output from that build, and its engine and patches pass the same checks as the app's.

See [Demo One](examples/synths/example-instruments/demo-one/README.md) for its controls, placement dots, sound, and how it was built.

## Writing rigs with an assistant

[`synth-patch-rigs`](plugins/synth-patch/skills/synth-patch-rigs/SKILL.md) is a skill that teaches a coding assistant to write rigs from a description ("an acid bassline that plays itself", "a lead I can play from the keyboard"), and module variants when a rig needs one. It carries the module names, values and docs from this repo, worked examples, and `rig.py`, which checks a rig the way the app reads it, explains its values in Hz and seconds, converts units to patch values and lays out the canvas.

In Claude Code, add this repo as a plugin marketplace and install it:

```
/plugin marketplace add HumanCrafted/synth-patch-source
/plugin install synth-patch@synth-patch-source
```

Any tool that reads Agent Skills can use the folder as it is: copy `plugins/synth-patch/skills/synth-patch-rigs` into its skills folder.

## Figma template

**[Synth Patch Source on Figma Community](https://www.figma.com/community/file/1696621078668432467)** is the file Demo One was built in: the panel, a component set for each control type, and the color styles. Duplicate it to see how a drawn synth is put together, or to draw your own. See [Figma template](docs/figma-template.md).

## License

The docs, the format specs, the examples, the modules and the parts (JSON, SVG and PNG files) are licensed under [CC BY 4.0](LICENSE). Use them, adapt them, build on them, including commercially; credit Synth Patch by Human Crafted LLC. The code (`examples/synths/example-instruments/demo-one/source/build_synth_json.py` and the skill's `scripts/`) is under the [MIT License](LICENSE-CODE).

Neither license covers the Synth Patch name or logo.
