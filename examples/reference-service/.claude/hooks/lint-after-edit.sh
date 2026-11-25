#!/usr/bin/env bash
# Implements AGT-024 (script under .claude/hooks), AGT-026 (guardrail; CI is the control),
# AGT-027 (quick: formatter and linter on the edited file only).
# PostToolUse hook (Edit|Write): format and lint the edited Python file.
# Exit 2 sends the output back to the agent as feedback; CI remains the real gate.
set -u
FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
case "$FILE" in
  *.py) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
uv run --locked ruff format --quiet "$FILE" >/dev/null 2>&1
if ! OUTPUT=$(uv run --locked ruff check --fix "$FILE" 2>&1); then
  printf 'ruff check failed for %s:\n%s\n' "$FILE" "$OUTPUT" >&2
  exit 2
fi
exit 0
