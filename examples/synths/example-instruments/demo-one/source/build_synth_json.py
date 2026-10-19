#!/usr/bin/env python3
"""Write synth.json for the Demo One example package.

Each control is (x, y, type, name, config). x and y are the placement dot
centers in frame pixels (288 dpi), read from demo1-placement-2268w.svg.

    python3 examples/synths/example-instruments/demo-one/source/build_synth_json.py
"""
import functools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent


def asset(filename):
    return {"url": f"assets/{filename}", "filename": filename}


KNOB_212 = {"size": 212, "graphic": asset("demo1-knob-212w=default.svg"), "minDegree": -150, "maxDegree": 150, "sensitivity": 0.005}
KNOB_91 = {"size": 91, "graphic": asset("demo1-knob-91w=default.svg"), "minDegree": -150, "maxDegree": 150, "sensitivity": 0.005}
INPUT = {"size": 106, "type": "input", "graphic": asset("demo1-jack-106w=input.svg")}
OUTPUT = {"size": 106, "type": "output", "graphic": asset("demo1-jack-106w=output.svg")}

CONTROLS = [
    (200, 330, "rotary-switch", "Oscillator Range", {
        "size": 224,
        "graphics": [asset(f"demo1-rotary-switch-224w={p}.svg") for p in ("neg45", "neg15", "15", "45")],
        "positions": 4,
        "positionNames": ["32'", "16'", "8'", "4'"],
        "switchMode": "reciprocating",
    }),
    (470, 330, "knob", "Oscillator Pitch", {**KNOB_212, "valueRange": "bipolar"}),
    (200, 720, "toggle", "Oscillator Wave", {
        "size": 96,
        "graphics": [asset(f"demo1-toggle-96w={p}.svg") for p in ("left", "middle", "right")],
        "positions": 3,
        "positionNames": ["Saw", "Triangle", "Square"],
    }),
    (470, 720, "knob", "Oscillator Pulse Width", {**KNOB_91, "valueRange": "unipolar"}),
    (775, 330, "knob", "Filter Cutoff", {**KNOB_212, "valueRange": "unipolar"}),
    (1065, 330, "knob", "Filter Resonance", {**KNOB_212, "valueRange": "unipolar"}),
    (775, 720, "knob", "Filter Envelope Amount", {**KNOB_91, "valueRange": "bipolar"}),
    (1065, 720, "slider", "Filter Envelope Decay", {
        "width": 198,
        "graphic": asset("demo1-slider-198w=default.svg"),
        "orientation": "vertical",
        "travelRange": 255,  # track 393 px minus cap 138 px, measured in Figma
        "valueRange": "unipolar",
    }),
    (1390, 330, "rotary-encoder", "Tempo", {"size": 91, "graphic": asset("demo1-knob-91w=default.svg"), "sensitivity": 0.005}),
    (1390, 520, "led", "Clock Indicator", {
        "width": 52,
        "height": 52,
        "graphics": [asset("demo1-led-52w=inactive.svg"), asset("demo1-led-52w=active.svg")],
        "ledMode": "continuous",
        "numStates": 2,
        "positionNames": ["Off", "On"],
    }),
    (1390, 720, "button", "Hold", {
        "size": 76,
        "graphics": [asset("demo1-button-76w=inactive, color=grey.svg"), asset("demo1-button-76w=active, color=grey.svg")],
        "buttonType": "latching",
    }),
    (1760, 330, "input-jack", "Pitch CV Input", INPUT),
    (1760, 520, "input-jack", "Cutoff CV Input", INPUT),
    (1760, 710, "input-jack", "Gate Input", INPUT),
    (2040, 330, "output-jack", "Oscillator Output", OUTPUT),
    (2040, 520, "output-jack", "Envelope Output", OUTPUT),
    (2040, 710, "output-jack", "Main Output", OUTPUT),
]


def wizard_order(p, q):
    """The upload wizard's numbering: top to bottom, left to right when dots are within 10 px vertically."""
    if abs(p[1] - q[1]) < 10:
        return -1 if p[0] < q[0] else (1 if p[0] > q[0] else 0)
    return -1 if p[1] < q[1] else 1


def main():
    names = [(c[2], c[3]) for c in CONTROLS]
    assert len(set(names)) == len(names), "control names must be unique within a type"
    control_config = {}
    for i, (x, y, kind, name, config) in enumerate(sorted(CONTROLS, key=functools.cmp_to_key(wizard_order)), 1):
        control_config[f"circle_{i}"] = {"x": x, "y": y, "name": name, "type": kind, "config": json.loads(json.dumps(config))}
    control_config["cableStyle"] = {"color": "#000000", "width": 22, "curvature": 6}
    manifest = {
        "format": "synthjson/1",
        "slug": "example-instruments-demo-one",
        "name": "Example Instruments Demo One",
        "manufacturer": "Example Instruments",
        "model": "Demo One",
        "description": "Fictional Semi-Modular Synthesizer with One Oscillator, Low-Pass Filter, Decay Envelope and 6-Point Patch Bay",
        "category": "Semi-Modular",
        "tags": ["analog", "semi-modular"],
        "manufacturer_url": "https://example.com/demo-one",
        "manual_url": None,
        "is_listed": False,
        "verified": False,
        "featured": False,
        "frame": "assets/demo1-frame-2268w.svg",
        "thumbnail": "assets/demo1-thumbnail-2268w.png",
        "placement": "assets/demo1-placement-2268w.svg",
        "source": {"figma_section": "Demo One", "notes": "A made-up synth for the format docs. Not a real instrument.", "no_manual": "Fictional synth; there is no manual."},
        "control_config": control_config,
    }
    (PACKAGE / "synth.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote synth.json with {len(CONTROLS)} controls")


if __name__ == "__main__":
    main()
