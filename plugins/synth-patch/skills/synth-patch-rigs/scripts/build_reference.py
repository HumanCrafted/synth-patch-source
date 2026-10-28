#!/usr/bin/env python3
"""Regenerate this skill's references from the synth-patch-source repo.

    python3 scripts/build_reference.py           # write references/
    python3 scripts/build_reference.py --check   # exit 1 if references/ is out of date

Everything under references/ comes from here, so names never drift from the
modules: the docs and the example rigs are copied as they are (links that leave
docs/ point into the copies or at GitHub), the module packages, Demo One and
parts.json are copied byte for byte, and module-names.md and panels.json are
built from them. Run it after any change to docs/, modules/, parts/ or
examples/rigs/, and commit the result.
"""

import argparse
import filecmp
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
REPO = SKILL.parents[3]
GITHUB = "https://github.com/HumanCrafted/synth-patch-source/blob/main/"

DOCS = ["rigs.md", "modules.md", "patches.md", "controls.md", "engine.md", "synth-package.md", "parts.md"]
DEMO_ONE = "examples/synths/example-instruments/demo-one"

sys.path.insert(0, str(SCRIPTS))
import rig  # noqa: E402


def rewrite_links(text):
    def link(m):
        target = m.group(1)
        mod = re.fullmatch(r"\.\./modules/([a-z0-9-]+)/synth\.json(#.*)?", target)
        if mod:
            return f"](../library/modules/{mod.group(1)}.json)"
        if target == "../modules":
            return "](../library/modules)"
        if target == f"../{DEMO_ONE}/synth.json":
            return "](../library/synths/example-instruments-demo-one.json)"
        if target == "../parts":
            return "](../library/parts.json)"
        if target.startswith("../examples/rigs"):
            return "](../examples" + target[len("../examples/rigs") :] + ")"
        return f"]({GITHUB}{target[3:]})"

    return re.sub(r"\]\((\.\./[^)\s]+)\)", link, text)


def panel_sizes(modules_md, demo_frame):
    sizes = {}
    for slug, w, h in re.findall(r"\| \[`(synth-patch-[a-z0-9-]+)`\]\([^)]*\) \| (\d+) × (\d+) \|", modules_md):
        sizes[slug] = [int(w), int(h)]
    svg = demo_frame.read_text()[:500]
    w, h = re.search(r'width="(\d+)" height="(\d+)"', svg).groups()
    sizes["example-instruments-demo-one"] = [int(w), int(h)]
    return sizes


def module_reference(modules_md):
    """Each module's bullets from docs/modules.md's Module reference, by slug."""
    ref = modules_md.split("## Module reference", 1)[1]
    out = {}
    for block in re.split(r"\n(?=\*\*[^*]+\*\* \(`)", ref):
        m = re.match(r"\*\*([^*]+)\*\* \(`([a-z0-9-]+)`[^)]*\)\n((?:- .*\n?|  .*\n?)+)", block)
        if m:
            out[m.group(2)] = m.group(3).rstrip()
    return out


def module_order(modules_md):
    """(heading, [slugs]) in the order docs/modules.md lists them."""
    table = modules_md.split("## The modules", 1)[1].split("## Module reference", 1)[0]
    order = []
    for part in re.split(r"\n#### ", table)[1:]:
        heading = part.split("\n", 1)[0].strip()
        order.append((heading, re.findall(r"\| \[`(synth-patch-[a-z0-9-]+)`\]", part)))
    return order


def build(out):
    lib = out / "library"
    (lib / "modules").mkdir(parents=True)
    (lib / "synths").mkdir(parents=True)
    (out / "docs").mkdir()
    (out / "examples").mkdir()

    for path in sorted((REPO / "modules").glob("*/synth.json")):
        shutil.copyfile(path, lib / "modules" / f"{path.parent.name}.json")
    shutil.copyfile(REPO / DEMO_ONE / "synth.json", lib / "synths" / "example-instruments-demo-one.json")
    shutil.copyfile(REPO / "parts" / "parts.json", lib / "parts.json")

    modules_md = (REPO / "docs" / "modules.md").read_text()
    sizes = panel_sizes(modules_md, next((REPO / DEMO_ONE / "assets").glob("*-frame-*.svg")))
    (lib / "panels.json").write_text(json.dumps(sizes, indent=2, ensure_ascii=False) + "\n")

    for name in DOCS:
        text = (REPO / "docs" / name).read_text()
        header = f"<!-- Copied from docs/{name} in synth-patch-source by scripts/build_reference.py. Edit the original. -->\n\n"
        (out / "docs" / name).write_text(header + rewrite_links(text))
    for path in sorted((REPO / "examples" / "rigs").glob("*.json")):
        shutil.copyfile(path, out / "examples" / path.name)

    # module-names.md: every module's exact names, values and behavior, in one place
    rig.LIBRARY = lib
    behavior = module_reference(modules_md)
    lines = [
        "<!-- Built from modules/*/synth.json and docs/modules.md by scripts/build_reference.py. Don't edit. -->",
        "",
        "# Standard modules: exact names",
        "",
        "Every control and jack as rigs must spell them, the group each control's value goes in, its patch value and",
        "default, and what the engine makes of it. Engine ranges are end to end of the knob's travel: a knob at `n`",
        "(0 to 1) gives `lo + n × (hi − lo)`, or `lo × (hi / lo)^n` when it says exp. A bipolar knob at `v` (−1 to 1)",
        "is at `n = (v + 1) / 2`. `scripts/rig.py value <slug> \"<Control>\" <target>` does the sums.",
        "",
        "Panel sizes are in 288 dpi px, for placing instances. Below each table, the module's behavior from the",
        "module reference.",
        "",
    ]
    for heading, slugs in module_order(modules_md):
        lines += [f"## {heading}", ""]
        for slug in slugs:
            pkg = json.loads((lib / "modules" / f"{slug}.json").read_text())
            lines += [rig.module_card(pkg), ""]
            if slug in behavior:
                lines += [behavior[slug], ""]
    demo = json.loads((lib / "synths" / "example-instruments-demo-one.json").read_text())
    lines += [
        "## Drawn synths",
        "",
        "Demo One is the docs' example drawn synth (it isn't a real instrument). It has its own keys block and its",
        "own output, so in a rig it's heard directly until its Main Output is cabled.",
        "",
        rig.module_card(demo),
        "",
    ]
    (out / "module-names.md").write_text("\n".join(lines))


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        for name in cmp.left_only + cmp.right_only + cmp.diff_files:
            print(f"  differs: {Path(b, name).relative_to(SKILL)}")
        return False
    return all(same_tree(Path(a, d), Path(b, d)) for d in cmp.common_dirs)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="compare instead of writing")
    args = p.parse_args()
    target = SKILL / "references"
    with tempfile.TemporaryDirectory() as tmp:
        built = Path(tmp) / "references"
        build(built)
        if args.check:
            if target.exists() and same_tree(built, target):
                print("references/ is up to date.")
                return 0
            print("references/ is out of date: run scripts/build_reference.py")
            return 1
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(built, target)
    print(f"Wrote {target.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
