#!/usr/bin/env python3
"""Validate committed Claude Code configuration. Exit 1 on any problem.

Implements AGT-001, AGT-010, AGT-011, AGT-014, AGT-016 (optional --schema), AGT-017/AGT-021 (broad
allow rules and bypass default), AGT-018 (.env denies), AGT-028 (.mcp.json entries have a type).

Usage: scripts/check_agent_config.py [repo-dir] [--schema settings.schema.json]
Needs PyYAML; jsonschema is only needed with --schema.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

MAX_CLAUDE_MD_LINES = 200
MAX_RULE_LINES = 100
REQUIRED_DENY = ("Read(.env)", "Read(.env.*)")
FORBIDDEN_ALLOW = ("Bash", "Bash(*)", "Bash(bash *)", "Bash(sh *)", "Bash(python *)")


def frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    _, block, _ = text.split("---\n", 2)
    data = yaml.safe_load(block)
    if not isinstance(data, dict):
        msg = "frontmatter is not a mapping"
        raise ValueError(msg)
    return data


def check(root: Path, schema: Path | None) -> list[str]:
    errors: list[str] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        errors.append("CLAUDE.md is missing")
    elif len(claude_md.read_text(encoding="utf-8").splitlines()) > MAX_CLAUDE_MD_LINES:
        errors.append(f"CLAUDE.md is longer than {MAX_CLAUDE_MD_LINES} lines")
    settings_path = root / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"{settings_path}: {exc}"]
    perms = settings.get("permissions", {})
    if perms.get("defaultMode") in {"bypassPermissions", "auto"}:
        errors.append("permissions.defaultMode must not be bypassPermissions or auto")
    errors += [f"allow rule too broad: {r}" for r in perms.get("allow", []) if r in FORBIDDEN_ALLOW]
    errors += [f"missing deny rule: {r}" for r in REQUIRED_DENY if r not in perms.get("deny", [])]
    if schema is not None:
        import jsonschema  # noqa: PLC0415

        validator = jsonschema.Draft7Validator(json.loads(schema.read_text(encoding="utf-8")))
        for err in validator.iter_errors(settings):
            errors.append(f"schema: {err.message} at {list(err.path)}")
    mcp = root / ".mcp.json"
    if mcp.exists():
        servers = json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {})
        errors += [f".mcp.json: {n} has no type" for n, srv in servers.items() if "type" not in srv]
    for path in sorted((root / ".claude").glob("rules/*.md")):
        if len(path.read_text(encoding="utf-8").splitlines()) > MAX_RULE_LINES:
            errors.append(f"{path}: longer than {MAX_RULE_LINES} lines")
        try:
            fm = frontmatter(path)
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(f"{path}: frontmatter does not parse ({exc}); quote every glob")
            continue
        if fm is not None:
            paths = fm.get("paths")
            valid = isinstance(paths, list) and all(isinstance(p, str) for p in paths)
            if set(fm) - {"paths"} or not valid:
                errors.append(f"{path}: frontmatter must be only a 'paths' list of strings")
    skills = sorted((root / ".claude").glob("skills/*/SKILL.md"))
    agents = sorted((root / ".claude").glob("agents/*.md"))
    for path in [*skills, *agents]:
        try:
            fm = frontmatter(path)
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(f"{path}: frontmatter does not parse ({exc})")
            continue
        if not fm or "description" not in fm:
            errors.append(f"{path}: needs frontmatter with a description")
        elif path in agents and "tools" not in fm:
            errors.append(f"{path}: subagent must set an explicit tools allowlist")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args()
    problems = check(Path(args.root), args.schema)
    for problem in problems:
        print(f"ERROR {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
