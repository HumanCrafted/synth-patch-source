# Changelog

## Unreleased

- **Rig-writing skill:** [`synth-patch-rigs`](plugins/synth-patch/skills/synth-patch-rigs/SKILL.md), installable as the `synth-patch` plugin from this repo's marketplace. Writes rigs and module variants from a description, with the module names and docs copied from this repo by `scripts/build_reference.py`, four worked examples, and `scripts/rig.py` to check, explain and lay out rigs. No format changes.

## 2.0.0 (2026-10-26)

`synthjson/2` and `patchjson/2`. Every `synthjson/1` and `patchjson/1` file is still valid.

### Synth packages (`synthjson/2`)

- **Generated synths:** a package without panel art. `panel` lists the controls in sections and rows, and the app lays them out at 288 dpi, the same scale as drawn synths.
- **Parts:** a graphic can name a part from the parts library, `"parts:<name>"` or `"parts:<name>:<variant>"`, instead of shipping its own SVGs.
- **Variants:** a package that `extends` a generated synth and lists only what differs.
- **Engines:** an optional `engine` section says how a synth sounds, from signal blocks bound to its controls and jacks. `"kind": "module"` (a manufacturer's own engine) is reserved.
- **Controls:** two new types, `code` and `graphic`. Any control can set a `default`. Knobs can be stepped (`steps`), switches and stepped knobs can print short labels (`printedLabels`), and keys and buttons can play a `note`.
- Control keys can be any stable ID; drawn synths keep `circle_N`.

### Patches (`patchjson/2`)

- **Rigs:** several synths on a canvas (`instances`) with cables between them (`"instance/Jack Name"`). A one-synth patch reads as a rig of one.
- **The synth slug rule:** `synth` is a synth's exact slug or its plain slug without the app's id suffix, everywhere (patches, packs, rig instances).
- New `code` control group; an `about` field for what the app adds when it copies a patch.
- Reading is exact: names must match and values must fit, and anything else is listed as a problem. The older shapes the app wrote still read. Packs drop `synthesizer`.

### Library and examples

- The 18 standard modules, in `modules/`, and the parts library (43 parts), in `parts/`.
- Demo One has an engine.
- Two example rigs.
- Docs: [Engine](docs/engine.md), [Rigs](docs/rigs.md), [Standard modules](docs/modules.md), [Parts](docs/parts.md) and the [Figma template](docs/figma-template.md).

## 1.0.0 (2026-10-19)

`synthjson/1` and `patchjson/1`: drawn synth packages, 14 control types, one-synth patches and packs, and the Demo One example.
