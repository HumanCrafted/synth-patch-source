#!/usr/bin/env python3
"""Check, explain and lay out Synth Patch rigs (patchjson/2) and variants (synthjson/2).

    python3 rig.py check RIG.json [--synth PKG.json ...]
    python3 rig.py explain RIG.json [--all] [--synth PKG.json ...]
    python3 rig.py value SLUG "Control Name" TARGET [TARGET ...]
    python3 rig.py controls SLUG [--synth PKG.json ...]
    python3 rig.py layout RIG.json [--gap 120] [--row-width 9000] [--write]
    python3 rig.py check-synth PKG.json [--synth PKG.json ...]

`check` reads a rig the way the Synth Patch app does (docs/rigs.md, "Reading a
rig") and lists its problems, then the Writing-a-rig rules it breaks. Zero
problems and zero errors means the app loads it and it makes a sound path.

The library it knows: the standard modules and Demo One, from
references/library/ (copied from the synth-patch-source repo by
build_reference.py). Pass any other synth or variant with --synth.

Standard library only, Python 3.8+.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
LIBRARY = SKILL / "references" / "library"

# ── The format's tables (docs/patches.md, docs/controls.md) ────────────────

GROUP_OF = {
    "knob": "knobs",
    "slider": "sliders",
    "slider-angled": "slidersAngled",
    "toggle": "toggles",
    "rotary-switch": "rotarySwitches",
    "rotary-encoder": "rotaryEncoders",
    "led": "leds",
    "touch-pad": "touchPads",
    "button": "buttons",
    "wheel": "wheels",
    "joystick": "joysticks",
    "key": "keys",
    "code": "code",
}
TYPE_OF = {group: t for t, group in GROUP_OF.items()}
JACK_TYPES = ["output-jack", "input-jack"]

CABLE_COLORS = {
    "Black": "#000000",
    "Dark Grey": "#3A3A3A",
    "Mid Grey": "#7A7A7A",
    "Light Grey": "#E5E5E3",
    "Signal Orange": "#FF6B35",
    "Control Blue": "#0055A4",
    "Patch Green": "#00A878",
    "Warning Yellow": "#FFB700",
    "Synth Green": "#00FF1A",
    "Oscilloscope Green": "#00FF88",
    "Level Yellow": "#FFD700",
    "Amp Orange": "#FF9D00",
    "Vintage Amber": "#FF8000",
    "Clipping Red": "#FF3333",
    "Frequency Blue": "#00BFFF",
    "Mod Blue": "#00AAFF",
    "Modular Pink": "#FF6EC7",
}

# ── Engine blocks (docs/engine.md, "Block types") ──────────────────────────

BLOCKS = {
    "keyboard": (["transpose"], [], ["pitch", "gate"]),
    "clock": (["bpm"], ["reset", "run"], ["out", "div2", "div4"]),
    "lfo": (["rate", "shape", "rateCvAmount"], ["rateCv"], ["out"]),
    "vco": (["octave", "tune", "fine", "wave", "pulseWidth", "fmAmount", "pwmAmount"], ["pitch", "pitchCv", "pwCv", "sync"], ["out", "saw", "triangle", "square"]),
    "noise": (["color"], [], ["out"]),
    "random": (["smooth"], ["trigger", "sample"], ["stepped", "smooth"]),
    "sequencer": ([f"step{i}" for i in range(1, 9)] + [f"gate{i}" for i in range(1, 9)] + ["length", "gateLength"], ["clock", "reset", "run"], ["pitch", "gate"] + [f"s{i}" for i in range(1, 9)]),
    "ladder": (["cutoff", "resonance", "envAmount", "keyTrack", "cvAmount"], ["in", "pitch", "env", "cutoffCv"], ["out", "hp"]),
    "decay-env": (["decay"], ["gate"], ["out"]),
    "adsr": (["attack", "decay", "sustain", "release"], ["gate"], ["out"]),
    "vca": (["gain", "bias", "cvAmount"], ["in", "cv"], ["out"]),
    "mixer": (["levelA", "levelB", "levelC", "levelD"], ["a", "b", "c", "d"], ["out"]),
    "attenuverter": (["amount", "offset"], ["in"], ["out"]),
    "quantizer": (["scale", "root"], ["in"], ["out"]),
    "slew": (["time"], ["in"], ["out"]),
    "delay": (["time", "feedback", "mix"], ["in"], ["out"]),
    "reverb": (["size", "damping", "mix"], ["in"], ["out"]),
    "gate-or": (["useB"], ["a", "b"], ["out"]),
    "code": (["p1", "p2", "p3", "p4", "code"], ["a", "b", "c", "d"], ["out"]),
}

# Units of block params, for readouts
UNITS = {
    "clock": {"bpm": "BPM"},
    "lfo": {"rate": "Hz", "rateCvAmount": "oct/unit"},
    "vco": {"octave": "oct", "tune": "st", "fine": "st", "fmAmount": "oct/unit", "pulseWidth": "of the cycle", "pwmAmount": "of the cycle/unit"},
    "ladder": {"cutoff": "Hz", "envAmount": "oct", "cvAmount": "oct/unit", "keyTrack": "oct/oct"},
    "decay-env": {"decay": "s"},
    "adsr": {"attack": "s", "decay": "s", "release": "s"},
    "delay": {"time": "s"},
    "random": {"smooth": "s"},
    "slew": {"time": "s"},
    "keyboard": {"transpose": "oct"},
    "vca": {"gain": "×"},
    "sequencer": dict({f"step{i}": "st" for i in range(1, 9)}, length="steps", gateLength="%"),
}
# Params the block rounds to whole numbers
ROUNDED = {"sequencer": lambda p: p.startswith("step") or p in ("length", "gateLength"), "quantizer": lambda p: p == "root"}
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# ── Values ──────────────────────────────────────────────────────────────────


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def is_object(v):
    return isinstance(v, dict)


def describe(v):
    return f'"{v}"' if isinstance(v, str) else json.dumps(v)


def control_entries(cc):
    return [(k, c) for k, c in (cc or {}).items() if k != "cableStyle" and is_object(c) and isinstance(c.get("type"), str)]


def name_of(key, control):
    return control.get("name") or key


def is_bipolar(control):
    rng = (control or {}).get("config", {}).get("valueRange")
    if rng:
        return rng == "bipolar"
    return (control or {}).get("type") in ("slider", "slider-angled", "wheel")


def positions_of(control):
    p = control.get("config", {}).get("positionNames")
    return p if isinstance(p, list) and p else None


def default_value(control):
    config = control.get("config", {}) or {}
    if "default" in config:
        return config["default"]
    t = control.get("type")
    if t in ("toggle", "rotary-switch"):
        return (config.get("positionNames") or [None])[0]
    if t == "led":
        return (config.get("positionNames") or [False])[0]
    if t in ("button", "key", "touch-pad"):
        return False
    if t == "joystick":
        return {"x": 0, "y": 0}
    if t == "code":
        return ""
    return 0


def value_problem(control, value):
    t = control.get("type")
    positions = positions_of(control)
    if t in ("knob", "slider", "slider-angled", "wheel"):
        if not is_number(value):
            return f"{describe(value)} isn't a number"
        lo = -1 if is_bipolar(control) else 0
        return f"{value} is outside {lo} to 1" if value < lo or value > 1 else None
    if t == "rotary-encoder":
        return None if is_number(value) else f"{describe(value)} isn't a number"
    if t in ("toggle", "rotary-switch"):
        if not positions:
            return "has no positions"
        return None if isinstance(value, str) and value in positions else f"{describe(value)} isn't one of: {', '.join(positions)}"
    if t == "led":
        if positions:
            return None if isinstance(value, str) and value in positions else f"{describe(value)} isn't one of: {', '.join(positions)}"
        return None if isinstance(value, bool) else f"{describe(value)} isn't true or false"
    if t in ("button", "key", "touch-pad"):
        return None if isinstance(value, bool) else f"{describe(value)} isn't true or false"
    if t == "joystick":
        if not is_object(value) or ("x" not in value and "y" not in value) or not is_number(value.get("x", 0)) or not is_number(value.get("y", 0)):
            return f'{describe(value)} isn\'t {{ "x": number, "y": number }}'
        x, y = value.get("x", 0), value.get("y", 0)
        square = control.get("config", {}).get("gate") == "square"
        outside = (abs(x) > 1 or abs(y) > 1) if square else math.hypot(x, y) > 1.0001
        return f"({x}, {y}) is outside its {'square' if square else 'circular'} gate" if outside else None
    if t == "code":
        return None if isinstance(value, str) else f"{describe(value)} isn't text"
    return f"a {t} has no value"


def read_controls(controls, cc):
    """A patch's controls read against a synth: values by key, and problems."""
    values, problems = {}, []
    if controls is None:
        return values, problems
    if not is_object(controls):
        return values, ['"controls" must be an object of groups.']
    index = {}
    for key, control in control_entries(cc):
        index.setdefault((control["type"], name_of(key, control)), []).append((key, control))
    for group, entries in controls.items():
        if group == "cables":
            continue
        t = TYPE_OF.get(group)
        if not t:
            problems.append(f'No control group "{group}".')
            continue
        if not is_object(entries):
            problems.append(f'{group} must be an object of "name": value.')
            continue
        for name, raw in entries.items():
            matches = index.get((t, name), [])
            if not matches:
                problems.append(f'{group}: no {t} named "{name}".')
            for key, control in matches:
                problem = value_problem(control, raw)
                if problem:
                    problems.append(f'{group}: "{name}" {problem}.')
                else:
                    values[key] = raw
            if len(matches) > 1:
                problems.append(f'{group}: {len(matches)} controls are named "{name}"; all of them get this value.')
    return values, problems


def find_jack(cc, name, end):
    """A jack by name: `from` prefers an output, `to` an input. Returns (key, type)."""
    order = JACK_TYPES if end == "from" else list(reversed(JACK_TYPES))
    jacks = [(k, c) for k, c in control_entries(cc) if c["type"] in JACK_TYPES]
    for t in order:
        for key, c in jacks:
            if c["type"] == t and name_of(key, c) == name:
                return key, t
    return None, None


def read_color(color):
    if color in (None, "", "default"):
        return None, None
    if not isinstance(color, str):
        return None, "color must be a cable color name or #RRGGBB"
    if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        return color.upper(), None
    if color in CABLE_COLORS:
        return CABLE_COLORS[color], None
    return None, f'no cable color "{color}"'


def base_slug(slug):
    return re.sub(r"-[0-9a-f]{6}$", "", slug)


def resolve_slug(ref, slugs):
    slugs = list(slugs)
    if ref in slugs:
        return ref, None
    matches = [s for s in slugs if s != ref and base_slug(s) == ref]
    if not matches:
        return None, f'No synth "{ref}".'
    if len(matches) > 1:
        return matches[0], f'"{ref}" could be {" or ".join(matches)}; using {matches[0]}.'
    return matches[0], None


def split_jack(ref):
    if is_object(ref) and isinstance(ref.get("instance"), str) and isinstance(ref.get("jack"), str):
        return ref["instance"], ref["jack"]
    if not isinstance(ref, str):
        return None
    i = ref.find("/")
    return (ref[:i], ref[i + 1 :]) if i > 0 else None


# ── Packages and variants (docs/synth-package.md) ───────────────────────────


def slug_for(pkg):
    kebab = lambda v: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", str(v or "").lower()))
    return kebab(pkg.get("slug")) or kebab(f"{pkg.get('manufacturer', '')} {pkg.get('model', '')}") or "synth"


def is_drawn(pkg):
    return isinstance(pkg.get("frame"), str)


def apply_variant(base, variant):
    cc = dict(base.get("control_config") or {})
    for key, control in (variant.get("control_config") or {}).items():
        if control is None:
            cc.pop(key, None)
        else:
            cc[key] = control
    engine = base.get("engine")
    if engine and variant.get("engine"):
        blocks = [dict(b) for b in engine.get("blocks", [])]
        for bid, change in (variant["engine"].get("blocks") or {}).items():
            if change is None:
                blocks = [b for b in blocks if b.get("id") != bid]
            elif any(b.get("id") == bid for b in blocks):
                blocks = [dict(b, **change, id=bid) if b.get("id") == bid else b for b in blocks]
            else:
                blocks.append(dict({"type": ""}, **change, id=bid))
        engine = dict(engine, blocks=blocks)
        if variant["engine"].get("leds") is not None:
            engine["leds"] = variant["engine"]["leds"]
        if variant["engine"].get("output") is not None:
            engine["output"] = variant["engine"]["output"]
    identity = {k: v for k, v in variant.items() if k not in ("extends", "control_config", "panel", "engine")}
    out = dict(base, **identity)
    out.update(format=base.get("format"), control_config=cc, panel=variant.get("panel") or base.get("panel"))
    if engine is not None:
        out["engine"] = engine
    out["_base"] = base.get("_base") or slug_for(base)
    return out


def load_parts():
    path = LIBRARY / "parts.json"
    return json.loads(path.read_text())["parts"] if path.exists() else {}


PART_RENAMED = {"jack": "jack-hex-small", "led": "led-round", "button": "button-square"}


def part_problem(ref, parts):
    if not (isinstance(ref, str) and ref.startswith("parts:")):
        return None
    given, _, variant = ref[6:].partition(":")
    entry = parts.get(PART_RENAMED.get(given, given))
    if not entry:
        return f'no part "{given}"'
    if variant and variant not in (entry.get("variants") or {}):
        return f'part "{given}" has no variant "{variant}"'
    if not entry.get("files") and not (entry.get("variants") or {}).get(variant or entry.get("default", "")):
        return f'part "{given}" has no default variant'
    return None


def check_package(pkg, raw=None):
    """A resolved package's problems (docs/synth-package.md, "Reading a package"),
    then warnings for block params, inputs and ports the engine doesn't have."""
    problems, warnings = [], []
    raw = raw or pkg
    if pkg.get("format") not in ("synthjson/1", "synthjson/2"):
        problems.append(f"format is {describe(pkg.get('format'))}, not synthjson/2.")
    for field in ("name", "manufacturer", "model"):
        if not isinstance(pkg.get(field), str) or not pkg[field].strip():
            problems.append(f'"{field}" is missing or blank.')
    if "extends" in raw:
        for field in ("slug", "name", "manufacturer", "model"):
            if field not in raw:
                warnings.append(f'The variant has no "{field}" of its own, so it shows the base\'s.')
    if ("frame" in pkg) != ("thumbnail" in pkg):
        problems.append('A drawn synth needs both "frame" and "thumbnail".')
    for field in ("frame", "thumbnail"):
        v = pkg.get(field)
        if v is not None and (not isinstance(v, str) or not v.startswith("assets/") or ".." in v):
            problems.append(f'"{field}" must be a path starting with assets/.')
    if not isinstance(pkg.get("tags", []), list) or not all(isinstance(t, str) for t in pkg.get("tags", [])):
        problems.append('"tags" must be a list of strings.')
    controls = control_entries(pkg.get("control_config"))
    if not is_object(pkg.get("control_config")) or not controls:
        problems.append('"control_config" is missing or has no controls.')
    names = set()
    parts = load_parts()
    for key, c in controls:
        if not c.get("name"):
            problems.append(f'Control "{key}" has no name.')
            continue
        names.add(c["name"])
        if is_drawn(pkg) and not (is_number(c.get("x")) and is_number(c.get("y"))):
            problems.append(f'"{c["name"]}" needs a numeric x and y on a drawn synth.')
        config = c.get("config") or {}
        refs = [config.get("graphic")] + (config.get("graphics") if isinstance(config.get("graphics"), list) else [config.get("graphics")])
        for ref in refs:
            p = part_problem(ref, parts)
            if p:
                problems.append(f'"{c["name"]}": {p}.')
    inputs = {name_of(k, c) for k, c in controls if c["type"] == "input-jack"}
    outputs = {name_of(k, c) for k, c in controls if c["type"] == "output-jack"}
    for section in (pkg.get("panel") or {}).get("sections", []):
        for row in section.get("rows", []):
            for name in row:
                if name not in names:
                    problems.append(f'Panel lists "{name}", which isn\'t a control.')
    engine = pkg.get("engine")
    if engine:
        if engine.get("kind", "blocks") != "blocks":
            warnings.append(f'Engine kind "{engine.get("kind")}" is reserved; the synth reads as silent.')
        blocks = engine.get("blocks", [])
        ports = {}
        for b in blocks:
            if b.get("type") in BLOCKS:
                ports[b.get("id")] = BLOCKS[b["type"]][2]
        def port_ok(ref):
            bid, _, port = str(ref).partition(".")
            return bid in ports and port in ports[bid]
        ids = set()
        for b in blocks:
            bid, t = b.get("id"), b.get("type")
            if bid in ids:
                problems.append(f'Two blocks are called "{bid}".')
            ids.add(bid)
            if t not in BLOCKS:
                problems.append(f'Block "{bid}": no block type "{t}".')
                continue
            params, block_inputs, block_outputs = BLOCKS[t]
            for param, binding in (b.get("params") or {}).items():
                if is_object(binding) and binding.get("control") not in names:
                    problems.append(f'Block "{bid}" {param}: no control "{binding.get("control")}".')
                if param not in params:
                    warnings.append(f'Block "{bid}": a {t} block has no param "{param}" ({", ".join(params) or "none"}).')
                if is_object(binding) and binding.get("curve") == "exp" and binding.get("range") and min(binding["range"]) <= 0:
                    warnings.append(f'Block "{bid}" {param}: an exp range needs both ends above 0.')
            for port, spec in (b.get("inputs") or {}).items():
                if port not in block_inputs:
                    warnings.append(f'Block "{bid}": a {t} block has no input "{port}" ({", ".join(block_inputs) or "none"}).')
                if is_object(spec):
                    if spec.get("jack") not in inputs:
                        problems.append(f'Block "{bid}": no input jack "{spec.get("jack")}".')
                    if spec.get("normal") is not None and not port_ok(spec["normal"]):
                        warnings.append(f'Block "{bid}" {port}: normal "{spec["normal"]}" isn\'t a block port.')
                elif not port_ok(spec):
                    warnings.append(f'Block "{bid}" {port}: "{spec}" isn\'t a block port.')
            for port, jack in (b.get("outputs") or {}).items():
                if jack not in outputs:
                    problems.append(f'Block "{bid}": no output jack "{jack}".')
                if port not in block_outputs:
                    warnings.append(f'Block "{bid}": a {t} block has no output "{port}" ({", ".join(block_outputs)}).')
        for ref in engine.get("output") if isinstance(engine.get("output"), list) else ([engine["output"]] if engine.get("output") else []):
            if not port_ok(ref):
                warnings.append(f'Engine output "{ref}" isn\'t a block port.')
        for led, spec in (engine.get("leds") or {}).items():
            if led not in names:
                problems.append(f'LED "{led}" isn\'t a control.')
            if is_object(spec) and not port_ok(spec.get("source")):
                warnings.append(f'LED "{led}": source "{spec.get("source")}" isn\'t a block port.')
    return problems, warnings


class Registry:
    """Every synth this script knows, by slug: the library plus --synth files."""

    def __init__(self, extra=()):
        self.synths, self.notes = {}, []
        for folder in ("modules", "synths"):
            for path in sorted((LIBRARY / folder).glob("*.json")):
                pkg = json.loads(path.read_text())
                self.synths[slug_for(pkg)] = pkg
        for path in extra:
            self.add(Path(path))

    def add(self, path):
        data = json.loads(Path(path).read_text())
        pkg, problem = self.resolve(data)
        if problem:
            raise SystemExit(f"{path}: {problem}")
        self.synths[slug_for(pkg)] = pkg
        return pkg, data

    def resolve(self, data):
        if not is_object(data):
            return None, "A synth must be a package (a JSON object)."
        if isinstance(data.get("extends"), str):
            base = self.synths.get(data["extends"])
            if not base:
                return None, f'No synth "{data["extends"]}" to extend.'
            if is_drawn(base):
                return None, f'"{data["extends"]}" is drawn; only generated synths can be extended.'
            return apply_variant(base, data), None
        if not data.get("name") or not is_object(data.get("control_config")):
            return None, "A synth package needs a name and control_config."
        return data, None


def family(pkg):
    """The standard module a package is, or extends ("synth-patch-filter"), or None."""
    slug = pkg.get("_base") or slug_for(pkg)
    return slug if slug.startswith("synth-patch-") else None


def panel_size(pkg):
    sizes = json.loads((LIBRARY / "panels.json").read_text())
    return sizes.get(family(pkg) or slug_for(pkg))


# ── Engine readouts ─────────────────────────────────────────────────────────


def bindings_of(pkg, control_name):
    out = []
    for b in (pkg.get("engine") or {}).get("blocks", []):
        for param, binding in (b.get("params") or {}).items():
            if is_object(binding) and binding.get("control") == control_name:
                out.append((b, param, binding))
    return out


def map_binding(binding, control, value):
    if isinstance(value, str) and not binding.get("steps"):
        return value
    if binding.get("steps"):
        return binding["steps"].get(str(value), 0)
    if isinstance(value, bool):
        return 1 if value else 0
    v = value if is_number(value) else 0
    if binding.get("turns"):
        t = binding["turns"]
        return min(max(t["base"] + v * t["perTurn"], t.get("min", -math.inf)), t.get("max", math.inf))
    if binding.get("range"):
        lo, hi = binding["range"]
        n = (v + 1) / 2 if is_bipolar(control) else v
        return lo * (hi / lo) ** n if binding.get("curve") == "exp" else lo + n * (hi - lo)
    return v


def fmt_number(v, block_type, param):
    if (ROUNDED.get(block_type) or (lambda p: False))(param):
        v = round(v)
        if block_type == "quantizer" and param == "root":
            return NOTE_NAMES[v % 12]
        return str(v)
    a = abs(v)
    text = f"{v:.0f}" if a >= 100 else f"{v:.1f}" if a >= 10 else f"{v:.3f}" if a < 0.1 else f"{v:.2f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def readout(pkg, control, value):
    """What a control's value means in engine units, from its bindings."""
    parts = []
    for block, param, binding in bindings_of(pkg, control.get("name")):
        mapped = map_binding(binding, control, value)
        if isinstance(mapped, str):
            continue
        unit = UNITS.get(block["type"], {}).get(param, "")
        text = fmt_number(mapped, block["type"], param)
        if block["type"] in ("vco", "ladder") and param in ("tune", "fine", "envAmount", "octave") and mapped > 0:
            text = "+" + text
        if unit.startswith("of the cycle"):
            text = f"{mapped * 100:.0f}%"
            unit = "of the cycle" + (" per unit" if unit.endswith("/unit") else "")
        parts.append(f"{param} {text}{(' ' + unit) if unit else ''}".strip())
    return "; ".join(parts)


# ── Rigs ────────────────────────────────────────────────────────────────────

# Inputs a module needs something in before it does anything
MAIN_INPUTS = {
    "synth-patch-filter": ["Filter Input"],
    "synth-patch-vca": ["VCA Input"],
    "synth-patch-delay": ["Delay Input"],
    "synth-patch-reverb": ["Reverb Input"],
    "synth-patch-glide": ["Glide Input"],
    "synth-patch-quantizer": ["Quantizer Input"],
    "synth-patch-envelope": ["Gate Input"],
    "synth-patch-mixer": ["Input A", "Input B", "Input C", "Input D"],
}
# Outputs at audio rate: not pitch, not gates
AUDIO_OUTPUTS = {
    "synth-patch-oscillator": {"Saw Output", "Triangle Output", "Square Output"},
    "synth-patch-noise": {"Noise Output"},
    "synth-patch-filter": {"LP Output", "HP Output"},
    "synth-patch-delay": {"Delay Output"},
    "synth-patch-reverb": {"Reverb Output"},
}
GATE_INPUTS = {"Gate Input", "Clock Input", "Reset Input", "Run Input", "Sync Input"}


class Report:
    def __init__(self):
        self.problems, self.errors, self.warnings = [], [], []

    @property
    def ok(self):
        return not self.problems and not self.errors


def patch_as_rig(data):
    """A one-synth patch as a rig of one, like the app reads it."""
    synth = data.get("synth", data.get("synthesizer"))
    cables = []
    for c in data.get("cables") or []:
        if is_object(c) and not c.get("external"):
            c = dict(c)
            for end in ("from", "to"):
                if isinstance(c.get(end), str):
                    c[end] = f"main/{c[end]}"
            cables.append(c)
    rig = {k: v for k, v in data.items() if k not in ("synth", "synthesizer", "controls", "cables")}
    rig["instances"] = [{"id": "main", "synth": synth, "controls": data.get("controls")}]
    rig["cables"] = cables
    return rig


def check_rig(data, registry):
    r = Report()
    if not is_object(data):
        r.problems.append("Expected a JSON object.")
        return r, None
    fmt = data.get("format")
    if fmt is not None and not (isinstance(fmt, str) and (fmt.startswith("patchjson/") or fmt.startswith("patchmd/"))):
        r.problems.append(f"Unsupported format {describe(fmt)} (expected patchjson/2).")
        return r, None
    if isinstance(data.get("instances"), list):
        if "synth" in data or "synthesizer" in data:
            r.problems.append('A rig has "instances", not a top-level "synth".')
            return r, None
        raw = data
        if fmt != "patchjson/2":
            r.warnings.append('Write "format": "patchjson/2" on a rig.')
    elif isinstance(data.get("patches"), list):
        r.problems.append("That's a pack of patches, not a rig.")
        return r, None
    elif isinstance(data.get("synth", data.get("synthesizer")), str):
        raw = patch_as_rig(data)
    else:
        r.problems.append('Expected "instances" (a rig) or "synth" (a one-synth patch).')
        return r, None
    if not raw.get("name"):
        r.warnings.append('Give the rig a "name".')

    instances = []  # (id, pkg or None for unchecked, doc, values)
    seen = set()
    for i, inst in enumerate(raw["instances"]):
        if not is_object(inst) or not isinstance(inst.get("id"), str) or not inst["id"]:
            r.problems.append(f'Instance {i + 1} needs an "id".')
            continue
        iid = inst["id"]
        if iid in seen:
            r.problems.append(f'Two instances are called "{iid}".')
            continue
        if not isinstance(inst.get("synth"), str):
            r.problems.append(f'Instance "{iid}" defines a synth inside the patch; patches name synths by slug. Skipped.')
            continue
        slug, problem = resolve_slug(inst["synth"], registry.synths.keys())
        pkg = registry.synths.get(slug) if slug else None
        if not slug:
            if inst["synth"].startswith("synth-patch-") or inst["synth"].startswith("example-instruments-"):
                r.problems.append(f'Instance "{iid}": {problem} Skipped.')
                continue
            r.warnings.append(
                f'Instance "{iid}": "{inst["synth"]}" isn\'t in this skill\'s library, so its controls and jacks are unchecked. '
                "Pass its synth.json with --synth, or make sure the app has a synth with that slug."
            )
        elif problem:
            r.problems.append(f'Instance "{iid}": {problem}')
        seen.add(iid)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", iid):
            r.warnings.append(f'Instance id "{iid}" isn\'t lowercase kebab-case.')
        if not (is_number(inst.get("x")) and is_number(inst.get("y"))) and raw is data:
            r.warnings.append(f'Instance "{iid}" has no x/y, so it sits at 0, 0. Run `rig.py layout`.')
        values = {}
        if pkg is None:
            if inst.get("controls") is not None and not (is_object(inst["controls"]) and all(is_object(v) for v in inst["controls"].values())):
                r.problems.append(f'Instance "{iid}": "controls" must be an object of groups.')
        else:
            values, problems = read_controls(inst.get("controls"), pkg.get("control_config"))
            r.problems.extend(f'Instance "{iid}": {p}' for p in problems)
            cc = pkg.get("control_config")
            for key, value in values.items():
                c = cc[key]
                if c["type"] in ("key", "led"):
                    r.warnings.append(f'Instance "{iid}": leave out {GROUP_OF[c["type"]]} "{name_of(key, c)}"; the engine sets it while playing.')
                elif value == default_value(c) and not (isinstance(value, bool) != isinstance(default_value(c), bool)):
                    r.warnings.append(f'Instance "{iid}": {GROUP_OF[c["type"]]} "{name_of(key, c)}" is at its default ({describe(value)}); leave it out.')
        instances.append((iid, pkg, inst, values))

    by_id = {iid: (pkg, inst, values) for iid, pkg, inst, values in instances}
    cables = []  # (from_id, from_jack, from_type, to_id, to_jack, to_type)
    raw_cables = raw.get("cables", [])
    if not isinstance(raw_cables, list):
        r.problems.append('"cables" must be a list.')
        raw_cables = []
    seen_cables = set()
    for i, c in enumerate(raw_cables):
        label = f"Cable {i + 1}"
        if not is_object(c):
            r.problems.append(f'{label} isn\'t an object with "from" and "to".')
            continue
        ends = [split_jack(c.get("from")), split_jack(c.get("to"))]
        if not ends[0] or not ends[1]:
            r.problems.append(f'{label} needs "from" and "to" as "instance/Jack Name".')
            continue
        ok, resolved = True, []
        for e, (iid, jack) in enumerate(ends):
            if iid not in by_id:
                ok = False
                r.problems.append(f'{label}: no instance "{iid}".')
                continue
            pkg = by_id[iid][0]
            if pkg is None:
                resolved.append((iid, jack, None))
                continue
            key, jtype = find_jack(pkg.get("control_config"), jack, "from" if e == 0 else "to")
            if not key:
                ok = False
                hint = close_jacks(pkg, jack)
                r.problems.append(f'{label}: no jack "{jack}" on {iid}.{hint}')
            else:
                resolved.append((iid, jack, jtype))
        if not ok:
            continue
        (fi, fj, ft), (ti, tj, tt) = resolved
        if (fi, fj, ft) == (ti, tj, tt):
            r.problems.append(f"{label} has both ends on the same jack.")
            continue
        hex_, problem = read_color(c.get("color"))
        if problem:
            r.problems.append(f"{label}: {problem}; it follows the theme.")
        if ft == "input-jack" and tt == "output-jack":
            r.warnings.append(f'{label} runs from an input to an output; write the output as "from" ({ti}/{tj} → {fi}/{fj}).')
            (fi, fj, ft), (ti, tj, tt) = (ti, tj, tt), (fi, fj, ft)
        elif ft == tt and ft is not None:
            kind = "outputs" if ft == "output-jack" else "inputs"
            r.errors.append(f"{label} joins two {kind} ({fi}/{fj}, {ti}/{tj}); it carries nothing.")
            continue
        if (fi, fj, ti, tj) in seen_cables:
            r.warnings.append(f"{label} repeats an earlier cable; two cables into one input add, so it doubles the signal.")
        seen_cables.add((fi, fj, ti, tj))
        cables.append((fi, fj, ti, tj))

    rig_rules(r, instances, by_id, cables)
    return r, {"doc": raw, "instances": instances, "cables": cables}


def close_jacks(pkg, jack):
    names = [name_of(k, c) for k, c in control_entries(pkg.get("control_config")) if c["type"] in JACK_TYPES]
    want = jack.lower().replace(" ", "")
    near = [n for n in names if n.lower().replace(" ", "") == want or want in n.lower().replace(" ", "")]
    return f' Did you mean "{near[0]}"?' if near else f" Its jacks: {', '.join(names)}."


def rig_rules(r, instances, by_id, cables):
    """The Writing-a-rig checklist (docs/rigs.md) as checks."""
    fed = {}
    used = set()
    for fi, fj, ti, tj in cables:
        fed.setdefault((ti, tj), []).append((fi, fj))
        used.update([fi, ti])

    speakers = [iid for iid, pkg, _, _ in instances if pkg and family(pkg) == "synth-patch-speaker"]
    own_output = [iid for iid, pkg, _, _ in instances if pkg and not family(pkg) and (pkg.get("engine") or {}).get("output")]
    unchecked = [iid for iid, pkg, _, _ in instances if pkg is None]
    heard = [s for s in speakers if fed.get((s, "Speaker Input"))]
    if not instances:
        r.errors.append("The rig has no instances.")
    elif not heard and not own_output and not unchecked:
        r.errors.append("Nothing is heard: cable the audio into a Speaker's Speaker Input (synth-patch-speaker).")
    for s in speakers:
        if not fed.get((s, "Speaker Input")):
            r.errors.append(f'Speaker "{s}" has nothing in its Speaker Input.')

    for iid, pkg, inst, values in instances:
        if pkg is None:
            continue
        fam = family(pkg)
        if len(instances) > 1 and iid not in used:
            r.warnings.append(f'Instance "{iid}" isn\'t cabled to anything.')
        named = {name_of(k, pkg["control_config"][k]): v for k, v in values.items()}
        needs = MAIN_INPUTS.get(fam, [])
        if needs and not any(fed.get((iid, j)) for j in needs):
            if fam == "synth-patch-filter" and named.get("Resonance", 0.3) >= 0.95:
                pass  # a self-oscillating filter needs no input
            else:
                r.warnings.append(f'{iid} ({fam}) has nothing in {" or ".join(needs)}, so it does nothing.')
        if fam == "synth-patch-vca" and fed.get((iid, "VCA Input")) and not fed.get((iid, "CV Input")) and not named.get("Initial Level"):
            r.warnings.append(f"{iid}: the VCA has nothing in CV Input and Initial Level at 0, so it stays closed.")
        if fam == "synth-patch-keyboard":
            for jack in ("Pitch Output", "Gate Output"):
                if not any(f == (iid, jack) for srcs in fed.values() for f in srcs):
                    r.warnings.append(f"{iid}: the Keyboard's {jack} isn't cabled, so the keys don't reach the voice.")

    for (ti, tj), sources in fed.items():
        for fi, fj in sources:
            fpkg = by_id[fi][0]
            ffam = family(fpkg) if fpkg else None
            if tj.endswith("V/Oct Input") and fj in AUDIO_OUTPUTS.get(ffam, ()):
                r.warnings.append(f"{fi}/{fj} is audio, cabled into {ti}/{tj}: V/Oct inputs want pitch (a Keyboard, Sequencer, Quantizer or Glide output).")
            if tj in GATE_INPUTS and fj == "Pitch Output":
                r.warnings.append(f"{fi}/{fj} is pitch, cabled into {ti}/{tj}, which wants a gate or clock.")
            if tj == "Speaker Input" and fj in ("Envelope Output", "Pitch Output", "Gate Output", "Clock Output", "LFO Output"):
                r.warnings.append(f"{fi}/{fj} is a control signal, cabled straight into the Speaker.")

    # Panels shouldn't overlap
    rects = []
    for iid, pkg, inst, _ in instances:
        size = panel_size(pkg) if pkg else None
        if size and is_number(inst.get("x", 0)) and is_number(inst.get("y", 0)):
            rects.append((iid, inst.get("x", 0), inst.get("y", 0), size[0], size[1]))
    for a in range(len(rects)):
        for b in range(a + 1, len(rects)):
            ia, xa, ya, wa, ha = rects[a]
            ib, xb, yb, wb, hb = rects[b]
            if xa < xb + wb and xb < xa + wa and ya < yb + hb and yb < ya + ha:
                r.warnings.append(f'Panels "{ia}" and "{ib}" overlap on the canvas. Run `rig.py layout`.')


# ── Commands ────────────────────────────────────────────────────────────────


def dumps(value, indent=0, col=None, width=120):
    """JSON in the docs' style: objects and lists on one line when they fit.
    `indent` is the line's indent, `col` the column the value starts at."""
    col = indent if col is None else col
    if is_object(value) and value:
        flat = "{ " + ", ".join(f"{json.dumps(k, ensure_ascii=False)}: {dumps(v, 0, 0, 10**6)}" for k, v in value.items()) + " }"
    else:
        flat = json.dumps(value, ensure_ascii=False, separators=(", ", ": "))
    if col + len(flat) <= width or not isinstance(value, (dict, list)) or not value:
        return flat
    pad = " " * (indent + 2)
    if isinstance(value, list):
        items = [pad + dumps(v, indent + 2, None, width) for v in value]
    else:
        items = []
        for k, v in value.items():
            key = f"{json.dumps(k, ensure_ascii=False)}: "
            items.append(pad + key + dumps(v, indent + 2, indent + 2 + len(key), width))
    open_, close = ("[", "]") if isinstance(value, list) else ("{", "}")
    return open_ + "\n" + ",\n".join(items) + "\n" + " " * indent + close


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: not valid JSON: {e}")


def print_report(r, label):
    for kind, items in (("problem", r.problems), ("error", r.errors), ("warning", r.warnings)):
        for item in items:
            print(f"  {kind}: {item}")
    status = "OK" if r.ok else "FAIL"
    print(f"{status} {label}: {len(r.problems)} problems, {len(r.errors)} errors, {len(r.warnings)} warnings")


def cmd_check(args):
    registry = Registry(args.synth)
    failed = False
    for path in args.rig:
        r, _ = check_rig(load_json(path), registry)
        print_report(r, path)
        failed |= not r.ok
    return 1 if failed else 0


def cmd_explain(args):
    registry = Registry(args.synth)
    r, rig = check_rig(load_json(args.rig), registry)
    if rig is None:
        print_report(r, args.rig)
        return 1
    doc = rig["doc"]
    print(f"{doc.get('name', '(no name)')}")
    if doc.get("description"):
        print(f"  {doc['description']}")
    for iid, pkg, inst, values in rig["instances"]:
        where = f" at {inst.get('x', 0)}, {inst.get('y', 0)}"
        if pkg is None:
            print(f"\n{iid}: {inst['synth']} (unchecked){where}")
            continue
        size = panel_size(pkg)
        print(f"\n{iid}: {pkg.get('name')} ({slug_for(pkg)}){where}" + (f", {size[0]} × {size[1]}" if size else ""))
        for key, c in control_entries(pkg.get("control_config")):
            if c["type"] not in GROUP_OF or c["type"] in ("key", "led"):
                continue
            set_ = key in values
            if not set_ and not args.all:
                continue
            value = values[key] if set_ else default_value(c)
            shown = value if not isinstance(value, str) or c["type"] != "code" else f"<{len(value.splitlines())} lines of code>"
            meaning = readout(pkg, c, value)
            print(f"  {'' if set_ else '(default) '}{name_of(key, c)} = {json.dumps(shown, ensure_ascii=False)}" + (f"  →  {meaning}" if meaning else ""))
    print("\nCables")
    for fi, fj, ti, tj in rig["cables"]:
        print(f"  {fi}/{fj} → {ti}/{tj}")
    speakers = [iid for iid, pkg, _, _ in rig["instances"] if pkg and family(pkg) == "synth-patch-speaker"]
    keys = [iid for iid, pkg, _, _ in rig["instances"] if pkg and any(c["type"] == "key" for _, c in control_entries(pkg.get("control_config")))]
    print(f"\nHeard through: {', '.join(speakers) or 'synths with their own output'}")
    print(f"Played from: {', '.join(keys) if keys else 'no keys on any panel; notes go to every synth with a keyboard block'}")
    print()
    print_report(r, args.rig)
    return 0 if r.ok else 1


def find_control(pkg, name):
    matches = [(k, c) for k, c in control_entries(pkg.get("control_config")) if name_of(k, c) == name and c["type"] in GROUP_OF]
    if not matches:
        names = [name_of(k, c) for k, c in control_entries(pkg.get("control_config")) if c["type"] in GROUP_OF]
        raise SystemExit(f'{slug_for(pkg)} has no control "{name}". Its controls: {", ".join(names)}')
    return matches[0][1]


def to_value(pkg, control, target):
    """A target in engine units (800 for 800 Hz, a position name) → the patch value."""
    positions = positions_of(control)
    if positions:
        if target in positions:
            return target, ""
        raise SystemExit(f'"{control["name"]}" is a switch: one of {", ".join(positions)}')
    if control["type"] in ("button", "key", "touch-pad"):
        return target.lower() in ("1", "true", "on", "yes"), ""
    for block, param, binding in bindings_of(pkg, control["name"]):
        if not binding.get("range"):
            continue
        lo, hi = binding["range"]
        x = float(target)
        if binding.get("curve") == "exp":
            if x <= 0:
                raise SystemExit("An exponential range only covers values above 0.")
            n = math.log(x / lo) / math.log(hi / lo)
        else:
            n = (x - lo) / (hi - lo)
        steps = control.get("config", {}).get("steps")
        if steps and steps > 1:
            n = round(n * (steps - 1)) / (steps - 1)
        v = 2 * n - 1 if is_bipolar(control) else n
        lo_v = -1 if is_bipolar(control) else 0
        note = ""
        if v < lo_v - 1e-9 or v > 1 + 1e-9:
            note = f"out of range: the knob covers {lo}–{hi} {UNITS.get(block['type'], {}).get(param, '')}".rstrip()
            v = min(max(v, lo_v), 1)
        return round(v, 4), note
    raise SystemExit(f'"{control["name"]}" has no range binding; write its value as 0 to 1 directly.')


def cmd_value(args):
    registry = Registry(args.synth)
    slug, problem = resolve_slug(args.slug, registry.synths.keys())
    if not slug:
        raise SystemExit(problem)
    pkg = registry.synths[slug]
    control = find_control(pkg, args.control)
    for target in args.target:
        value, note = to_value(pkg, control, target)
        meaning = readout(pkg, control, value)
        print(f'"{control["name"]}": {json.dumps(value, ensure_ascii=False)}' + (f"  ({meaning})" if meaning else "") + (f"  [{note}]" if note else ""))
    return 0


def module_card(pkg, heading=True):
    """One synth's exact names and value ranges, as markdown."""
    lines = []
    slug = slug_for(pkg)
    size = panel_size(pkg)
    if heading:
        lines.append(f"### {pkg.get('model') or pkg.get('name')} · `{slug}`")
        lines.append("")
    lines.append(f"Panel {size[0]} × {size[1]} px." if size else "Panel size: see the package.")
    lines.append("")
    rows = []
    shown_only = []
    for key, c in control_entries(pkg.get("control_config")):
        t = c["type"]
        if t not in GROUP_OF:
            continue
        name = name_of(key, c)
        if t in ("key", "led"):
            shown_only.append(f"{name} ({t})")
            continue
        positions = positions_of(c)
        steps = c.get("config", {}).get("steps")
        if positions:
            kind = ", ".join(f"`{p}`" for p in positions)
        elif t == "code":
            kind = "code, a string"
        elif t in ("button", "touch-pad"):
            kind = "`true` / `false`"
        elif t == "rotary-encoder":
            kind = "turns"
        else:
            kind = ("−1 to 1" if is_bipolar(c) else "0 to 1") + (f", {steps} steps" if steps else "")
        d = default_value(c)
        if t == "code":
            d_text = "a wavefolder" if "Wavefolder" in str(d) else "empty"
        else:
            d_text = f"`{json.dumps(d, ensure_ascii=False)}`"
            meaning = readout(pkg, c, d)
            if meaning:
                d_text += f" ({meaning})"
        maps = []
        for block, param, binding in bindings_of(pkg, name):
            unit = UNITS.get(block["type"], {}).get(param, "")
            if binding.get("range"):
                lo, hi = binding["range"]
                maps.append(f"{param} {lo} → {hi}{(' ' + unit) if unit else ''}{', exp' if binding.get('curve') == 'exp' else ''}")
            elif binding.get("steps"):
                maps.append(f"{param} " + ", ".join(f"{k}={v}" for k, v in binding["steps"].items()))
            elif binding.get("turns"):
                tr = binding["turns"]
                maps.append(f"{param} {tr['base']} + {tr['perTurn']} per turn{(' ' + unit) if unit else ''}, {tr.get('min', '–')} to {tr.get('max', '–')}")
            elif t in ("button", "key", "touch-pad", "led"):
                maps.append(f"{param} 1 when true, 0 when false")
            elif t == "code":
                maps.append(f"{param}, the source")
        rows.append(f"| {name} | `{GROUP_OF[t]}` | {kind} | {d_text} | {'; '.join(maps) or '–'} |")
    if rows:
        lines += ["| Control | Group | Value | Default | Engine |", "| --- | --- | --- | --- | --- |"] + rows + [""]
    inputs = [name_of(k, c) for k, c in control_entries(pkg.get("control_config")) if c["type"] == "input-jack"]
    outputs = [name_of(k, c) for k, c in control_entries(pkg.get("control_config")) if c["type"] == "output-jack"]
    lines.append(f"Inputs: {', '.join(f'`{j}`' for j in inputs) or '–'}  ")
    lines.append(f"Outputs: {', '.join(f'`{j}`' for j in outputs) or '–'}")
    if shown_only:
        lines.append("")
        lines.append(f"Set by the engine or the player, so rigs leave them out: {', '.join(shown_only)}.")
    return "\n".join(lines)


def cmd_controls(args):
    registry = Registry(args.synth)
    slug, problem = resolve_slug(args.slug, registry.synths.keys())
    if not slug:
        raise SystemExit(problem)
    print(module_card(registry.synths[slug]))
    return 0


def cmd_layout(args):
    registry = Registry(args.synth)
    data = load_json(args.rig)
    if not isinstance(data.get("instances"), list):
        raise SystemExit("Not a rig: no instances.")
    x = y = row_h = 0
    for inst in data["instances"]:
        slug, _ = resolve_slug(inst.get("synth", ""), registry.synths.keys())
        size = panel_size(registry.synths[slug]) if slug else None
        if not size:
            print(f'  note: no panel size for "{inst.get("synth")}"; assuming 2400 × 1200.', file=sys.stderr)
            size = [2400, 1200]
        if args.row_width and x > 0 and x + size[0] > args.row_width:
            x, y, row_h = 0, y + row_h + args.gap, 0
        # x and y right after synth, as the docs write them
        placed = {}
        for k, v in inst.items():
            if k in ("x", "y"):
                continue
            placed[k] = v
            if k == "synth":
                placed["x"], placed["y"] = x, y
        inst.clear()
        inst.update(placed)
        x += size[0] + args.gap
        row_h = max(row_h, size[1])
    text = dumps(data) + "\n"
    if args.write:
        Path(args.rig).write_text(text)
        for inst in data["instances"]:
            print(f"  {inst['id']}: {inst['x']}, {inst['y']}")
    else:
        sys.stdout.write(text)
    return 0


def cmd_check_synth(args):
    registry = Registry(args.synth)
    data = load_json(args.package)
    pkg, problem = registry.resolve(data)
    if problem:
        print(f"  problem: {problem}\nFAIL {args.package}")
        return 1
    problems, warnings = check_package(pkg, data)
    r = Report()
    r.problems, r.warnings = problems, warnings
    if "extends" in data:
        print(f"Variant of {data['extends']} → {slug_for(pkg)}")
    print_report(r, args.package)
    return 0 if r.ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    synth_arg = dict(action="append", default=[], metavar="PKG.json", help="another synth package or variant (repeatable)")

    s = sub.add_parser("check", help="check rigs as the app reads them")
    s.add_argument("rig", nargs="+")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("explain", help="every control in engine units, and the cables")
    s.add_argument("rig")
    s.add_argument("--all", action="store_true", help="also show controls left at their default")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_explain)

    s = sub.add_parser("value", help="engine units (800 Hz, 0.3 s, 7 semitones) → patch value")
    s.add_argument("slug")
    s.add_argument("control")
    s.add_argument("target", nargs="+")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_value)

    s = sub.add_parser("controls", help="a synth's exact control and jack names")
    s.add_argument("slug")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_controls)

    s = sub.add_parser("layout", help="place instances left to right in list order")
    s.add_argument("rig")
    s.add_argument("--gap", type=int, default=120)
    s.add_argument("--row-width", type=int, default=0, help="start a new row past this width (0: one row)")
    s.add_argument("--write", action="store_true", help="write the positions into the file")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_layout)

    s = sub.add_parser("check-synth", help="check a synth package or variant")
    s.add_argument("package")
    s.add_argument("--synth", **synth_arg)
    s.set_defaults(fn=cmd_check_synth)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
