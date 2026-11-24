#!/usr/bin/env python3
"""Zip the synth-patch-rigs skill for upload to claude.ai.

    python3 scripts/package_skill.py             # refresh references/, then zip
    python3 scripts/package_skill.py --offline   # zip with the snapshot already here

First it runs the skill's scripts/build_reference.py, which rebuilds
references/ and refreshes the snapshot of the app's library synths from the
app's public API, so the zip always carries the current names. If the app
can't be reached it stops, unless --offline. If the refresh changed anything,
it says so: commit those changes so the repo matches the zip.

Then it writes dist/synth-patch-rigs-<version>.zip, with the skill folder at
the zip root, ready for claude.ai/customize/skills > Upload skill (or Replace
for a skill that's already there). The version is the synth-patch plugin's,
from plugins/synth-patch/.claude-plugin/plugin.json. dist/ isn't committed.
"""

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "synth-patch"
SKILL = PLUGIN / "skills" / "synth-patch-rigs"
DIST = REPO / "dist"
SKIP_NAMES = {".DS_Store", "__pycache__"}
SKIP_SUFFIXES = {".pyc"}
# claude.ai's limits on a skill's frontmatter
MAX_NAME, MAX_DESCRIPTION = 64, 1024


def frontmatter(skill_md):
    text = skill_md.read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit(f"{skill_md}: no --- frontmatter block")
    fields = dict(re.findall(r"^(\w+): (.*)$", match.group(1), re.M))
    for field, limit in (("name", MAX_NAME), ("description", MAX_DESCRIPTION)):
        if not fields.get(field):
            raise SystemExit(f"{skill_md}: no {field}")
        if len(fields[field]) > limit:
            raise SystemExit(f"{skill_md}: {field} is {len(fields[field])} characters; claude.ai allows {limit}")
    return fields


def refresh(offline):
    """Rebuild references/ (and the library snapshot). Returns the skill's
    changed paths, as git sees them."""
    if not offline:
        code = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_reference.py")]).returncode
        if code == 2:
            raise SystemExit("The app couldn't be reached, so the library snapshot wasn't refreshed. "
                             "Try again, or pass --offline to zip the snapshot already here.")
        if code:
            raise SystemExit(f"build_reference.py failed ({code}).")
    status = subprocess.run(["git", "status", "--porcelain", "--", str(SKILL)], cwd=REPO, capture_output=True, text=True)
    return [line[3:] for line in status.stdout.splitlines()]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--offline", action="store_true", help="skip the refresh and zip the references already here")
    args = p.parse_args()
    changed = refresh(args.offline)
    fields = frontmatter(SKILL / "SKILL.md")
    if fields["name"] != SKILL.name:
        raise SystemExit(f'SKILL.md name "{fields["name"]}" doesn\'t match its folder "{SKILL.name}"')
    version = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())["version"]
    DIST.mkdir(exist_ok=True)
    target = DIST / f"{SKILL.name}-{version}.zip"
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SKILL.rglob("*")):
            relative = path.relative_to(SKILL)
            if any(part in SKIP_NAMES for part in relative.parts) or path.suffix in SKIP_SUFFIXES or not path.is_file():
                continue
            archive.write(path, Path(SKILL.name) / relative)
            count += 1
    print(f"{SKILL.name} {version}: {count} files -> {target.relative_to(REPO)}")
    if changed:
        print("Not committed yet, so the zip differs from the repo:")
        for path in changed:
            print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
