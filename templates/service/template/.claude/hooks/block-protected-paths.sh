#!/usr/bin/env bash
# PreToolUse hook (Edit|Write): block edits to files that agents must never change by hand.
# Fails closed: if jq is missing or the input is unreadable, the edit is blocked.
set -u
FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || FILE=""
if [ -z "$FILE" ]; then
  echo "block-protected-paths: could not read tool_input.file_path; blocking edit" >&2
  exit 2
fi
case "$FILE" in
  */.env.example) exit 0 ;;
  */.env|*/.env.*|*/uv.lock|*.tfstate|*.tfstate.*|*/.git/*)
    jq -n --arg f "$FILE" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("Protected file, edit it through the proper tool or ask a human: " + $f)
      }
    }'
    exit 0
    ;;
esac
exit 0
