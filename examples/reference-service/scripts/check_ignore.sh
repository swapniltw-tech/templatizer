#!/usr/bin/env bash
# Usage: scripts/check_ignore.sh [repo-dir]   (run from inside a git work tree)
set -eu
cd "${1:-.}"
must_ignore=(
  .env .env.local .env.production
  .claude/settings.local.json CLAUDE.local.md
  .terraform/providers/x infra/.terraform/x infra/terraform.tfstate infra/terraform.tfstate.backup
  infra/plan.tfplan infra/prod.auto.tfvars infra/terraform.tfvars
  src/pkg/__pycache__/a.pyc .venv/bin/python
  .mypy_cache/x .ruff_cache/x .pytest_cache/x .hypothesis/x .coverage htmlcov/index.html
  evals/results/run1.json evals/outputs/a.jsonl
  server.pem id.key .azure/config secrets/a.txt app.log dist/x.whl
)
must_track=(
  .env.example .claude/settings.json .claude/rules/testing.md .claude/skills/x/SKILL.md
  .claude/agents/a.md .claude/hooks/h.sh .mcp.json CLAUDE.md AGENTS.md
  uv.lock .python-version pyproject.toml infra/.terraform.lock.hcl infra/main.tf
  evals/datasets/a.jsonl evals/s/thresholds.yaml registry/tools/t.json prompts/p.md
  src/pkg/main.py docs/adr/0001-x.md Dockerfile .dockerignore
)
rc=0
for p in "${must_ignore[@]}"; do
  git check-ignore -q -- "$p" || { echo "NOT ignored (must be): $p"; rc=1; }
done
for p in "${must_track[@]}"; do
  if git check-ignore -q -- "$p"; then echo "IGNORED (must be tracked): $p"; rc=1; fi
done
exit $rc
