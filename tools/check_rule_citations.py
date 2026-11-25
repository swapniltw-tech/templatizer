#!/usr/bin/env python3
"""Check the rule IDs cited in template and example files against rules.yml.

Usage: python3 -I tools/check_rule_citations.py [--rules PATH] [DIR ...]
  default DIRs: templates/ai-python-template/template examples/reference-service (tracked files only)

Fails (exit 1) when a file cites an ID that is not in rules.yml or is retired, or when a file cites
no rule ID at all (the brief: every generated file cites the rules it implements). Files that cannot
carry a comment are exempt (findings log F-18). IDs are matched only for known doc prefixes, so
words like "UTF-123" are ignored. Stdlib only, so it runs with `python3 -I`.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"\b([A-Z]{3})-(\d{3})\b")
# Cannot carry a comment: strict JSON (AGT-016), a bare version (TEC-004), generated lock/spec files.
EXEMPT_NAMES = {"settings.json", ".python-version", "uv.lock", "openapi.yaml"}
DEFAULT_DIRS = ["templates/ai-python-template/template", "examples/reference-service"]


def read_rules(path: Path) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    retired: set[str] = set()
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^  - id: "([A-Z]{3}-\d{3})"$', line)
        if m:
            current = m.group(1)
            ids.add(current)
        elif line == "    retired: true":
            retired.add(current)
    return ids, retired


def tracked_files(directory: str) -> list[Path]:
    out = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--", directory],  # noqa: S607
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return [ROOT / name for name in out]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, default=ROOT / "rules.yml")
    parser.add_argument("dirs", nargs="*", default=DEFAULT_DIRS)
    args = parser.parse_args()
    ids, retired = read_rules(args.rules)
    prefixes = {i.split("-")[0] for i in ids}
    problems: list[str] = []
    checked = 0
    for directory in args.dirs:
        for path in tracked_files(directory):
            if path.name in EXEMPT_NAMES or not path.is_file():
                continue
            checked += 1
            cited = [m.group(0) for m in ID.finditer(path.read_text(encoding="utf-8", errors="ignore"))
                     if m.group(1) in prefixes]
            rel = path.relative_to(ROOT)
            if not cited:
                problems.append(f"{rel}: cites no rule ID")
            problems += [f"{rel}: {i} is not in rules.yml" for i in sorted(set(cited) - ids)]
            problems += [f"{rel}: {i} is retired" for i in sorted(set(cited) & retired)]
    for problem in problems:
        print(f"ERROR {problem}")
    print(f"{checked} files checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
