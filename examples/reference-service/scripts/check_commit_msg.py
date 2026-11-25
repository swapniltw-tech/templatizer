#!/usr/bin/env python3
"""Check that commit subjects follow Conventional Commits 1.0.0.

Usage: scripts/check_commit_msg.py <git-rev-range>   e.g. origin/main..HEAD
Reads subjects with `git log --format=%s`. Merge commits and fixup commits are rejected.
"""

import re
import subprocess
import sys

TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "build", "ci", "perf", "revert")
SUBJECT = re.compile(rf"^({'|'.join(TYPES)})(\([a-z0-9][a-z0-9._/-]*\))?!?: \S.{{0,70}}$")


def main(rev_range: str) -> int:
    out = subprocess.run(  # noqa: S603
        ["git", "log", "--format=%s", rev_range],  # noqa: S607
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    bad = [s for s in out.splitlines() if not SUBJECT.match(s)]
    for subject in bad:
        print(f"Not a Conventional Commit subject: {subject!r}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
