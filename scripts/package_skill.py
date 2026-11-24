#!/usr/bin/env python3
"""Zip the synth-patch-rigs skill for upload to claude.ai.

    python3 scripts/package_skill.py

Writes dist/synth-patch-rigs-<version>.zip, with the skill folder at the zip
root, ready for claude.ai/customize/skills > Upload skill (or Replace for a
skill that's already there). The version is the synth-patch plugin's, from
plugins/synth-patch/.claude-plugin/plugin.json, so the zip name says which
release it is; nothing in the skill is changed. dist/ isn't committed.
"""

import json
import re
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


def main():
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
