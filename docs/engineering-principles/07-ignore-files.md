# Ignore Files (.gitignore and .dockerignore)

> **Owner:** Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** git documentation (gitignore, `git check-ignore`); Docker documentation (`.dockerignore`); Claude Code documentation (settings and memory pages, code.claude.com); Terraform documentation (state and `.terraform.lock.hcl`)

## Purpose
Define the canonical `.gitignore` and `.dockerignore` for Python services. Ignore files are the first control that keeps secrets, state, caches and personal files out of Git history and container images. AI coding agents routinely run `git add -A`, so a missing ignore entry becomes a committed secret. Every repo starts from these blocks (the Copier template ships them) and adds repo-specific entries only below the marker line.

Secret handling itself (storage, rotation, what to do after a leak) is owned by [06-secrets-and-env.md](./06-secrets-and-env.md). The Dockerfile and image build are owned by [00-tech-stack.md](./00-tech-stack.md). Repo layout is owned by [09-structure-and-format.md](./09-structure-and-format.md).

## Rules

- **IGN-001** [MUST] [review] Every repo MUST contain a `.gitignore` that starts from the canonical block in this doc. Repo-specific additions MUST go below the `# --- repo-specific ---` marker, and removals from the canonical block require a waiver.
- **IGN-002** [MUST] [ci: scripts/check_ignore.sh] `.env` and `.env.*` MUST be ignored, and `.env.example` MUST NOT be ignored (negation entry `!.env.example`).
- **IGN-003** [MUST] [ci: scripts/check_ignore.sh] Terraform state (`*.tfstate`, `*.tfstate.*`), the `.terraform/` directory, saved plans (`*.tfplan`) and `*.auto.tfvars` / `terraform.tfvars` MUST be ignored. State lives in the remote backend, never in Git.
- **IGN-004** [MUST] [ci: scripts/check_ignore.sh] `.terraform.lock.hcl` MUST NOT be ignored. It pins provider versions and hashes and is committed.
- **IGN-005** [MUST] [ci: scripts/check_ignore.sh] `.claude/settings.local.json` and `CLAUDE.local.md` MUST be ignored. Claude Code only adds `settings.local.json` to the developer's global git excludes, not to the repo, so the repo entry is still required.
- **IGN-006** [MUST] [ci: scripts/check_ignore.sh] Shared agent files MUST NOT be ignored: `CLAUDE.md`, `AGENTS.md`, `.mcp.json`, `.claude/settings.json`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`. Content rules for these files are in [08-claude-md.md](./08-claude-md.md).
- **IGN-007** [MUST] [ci: scripts/check_ignore.sh] Lockfiles (`uv.lock`) and `.python-version` MUST NOT be ignored.
- **IGN-008** [MUST] [ci: scripts/check_ignore.sh] Private keys and certificate bundles (`*.pem`, `*.key`, `*.pfx`, `*.p12`, `*.jks`), `secrets/`, `credentials.json` and `.azure/` MUST be ignored.
- **IGN-009** [MUST] [ci: scripts/check_ignore.sh] Eval run outputs (`evals/results/`, `evals/outputs/`, `evals/.cache/`) MUST be ignored. Datasets, evaluators and `thresholds.yaml` MUST be committed. Retained eval evidence is stored as CI artifacts per [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).
- **IGN-010** [MUST] [ci: scripts/check_ignore.sh] Tool caches and coverage output (`.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `.hypothesis/`, `.coverage*`, `htmlcov/`, `coverage.xml`, `mutants/`) and virtual environments (`.venv/`) MUST be ignored.
- **IGN-011** [MUST] [review] `.gitignore` MUST NOT be relied on to protect a secret that is already committed. A committed secret is a leaked secret: follow the leak response in [06-secrets-and-env.md](./06-secrets-and-env.md).
- **IGN-012** [MUST] [review] Agents and humans MUST NOT use `git add -f` or `git add --force` to bypass an ignore entry. If a file must be tracked, change the ignore file in the MR and explain why.
- **IGN-013** [MUST] [review] Every repo that builds an image MUST contain a `.dockerignore` that denies everything by default and allow-lists only what the Dockerfile copies (the canonical block below).
- **IGN-014** [MUST] [review] Dockerfile `COPY` instructions MUST name explicit paths (`COPY src ./src`). `COPY . .` MUST NOT be used, because it depends on the ignore file being perfect.
- **IGN-015** [MUST] [ci: image-content check] The built image MUST NOT contain `.env*`, `.git/`, `.claude/`, `CLAUDE.md`, `tests/`, `infra/`, `evals/`, `docs/` or key material. CI verifies the build context with the check in "Verify the `.dockerignore`" below.
- **IGN-016** [SHOULD] [ci: scripts/check_ignore.sh] `scripts/check_ignore.sh` SHOULD run in `make check` or as a dedicated CI job so that an accidental edit of `.gitignore` fails the MR.
- **IGN-017** [SHOULD] [review] Personal editor and OS files SHOULD also be ignored in the developer's global gitignore. The repo keeps a small editor/OS block anyway because contributors and agents run on mixed machines.
- **IGN-018** [SHOULD] [review] Each repo-specific entry SHOULD carry a one-line comment explaining why it exists.
- **IGN-019** [MAY] [review] Repos MAY add language-specific entries (for example `node_modules/` for a docs site) below the marker line.

## Canonical `.gitignore`

Checked on 2026-11-25 with `git init` plus `git check-ignore` using the script below (all paths behaved as expected).

```gitignore
# ===== Canonical .gitignore for Python services (docs/07-ignore-files.md) =====

# --- Secrets and local environment ---
.env
.env.*
!.env.example
*.pem
*.key
*.pfx
*.p12
*.jks
secrets/
credentials.json
.azure/

# --- Claude Code personal files (shared .claude/ files and .mcp.json ARE committed) ---
.claude/settings.local.json
CLAUDE.local.md

# --- Python ---
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/
.venv/
venv/

# --- Tool caches and test output ---
.ruff_cache/
.mypy_cache/
.pytest_cache/
.hypothesis/
.import_linter_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml
junit.xml
mutants/
.ipynb_checkpoints/

# --- Terraform (commit .terraform.lock.hcl; never commit state or plans) ---
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
tfplan
crash.log
crash.*.log
*.auto.tfvars
terraform.tfvars
*.tfvars.json
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# --- Eval and run outputs (datasets, evaluators, thresholds.yaml ARE committed) ---
evals/results/
evals/outputs/
evals/.cache/
reports/
sbom*.json
sbom*.xml

# --- Local data and logs ---
*.log
.local/
tmp/
*.sqlite3
*.db

# --- Editors and OS ---
.idea/
.vscode/
*.swp
.DS_Store
Thumbs.db

# --- repo-specific --- (additions only; one-line reason per entry)
```

### Per-entry rationale

| Entry | Why |
|---|---|
| `.env`, `.env.*`, `!.env.example` | Local-only config and credentials. The example file documents variable names with fake values and is the only `.env*` file committed. |
| `*.pem`, `*.key`, `*.pfx`, `*.p12`, `*.jks`, `secrets/`, `credentials.json` | Common names for private keys, keystores and exported credentials. Public certificates that must be committed go in a named directory with an explicit `!` entry and a review note. |
| `.azure/` | Azure CLI profile and token cache; contains tokens after `az login`. |
| `.claude/settings.local.json`, `CLAUDE.local.md` | Personal Claude Code overrides and approvals (they can contain allow rules and personal URLs). Claude Code adds the settings file to the developer's global excludes after it first writes it, which does not protect other clones. |
| `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `build/`, `dist/` | Generated Python artifacts. |
| `.venv/`, `venv/` | Environments are rebuilt from `uv.lock`; they are platform-specific and large. |
| `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `.hypothesis/`, `.import_linter_cache/` | Tool caches. `.hypothesis/` can contain generated examples derived from test data. |
| `.coverage*`, `htmlcov/`, `coverage.xml`, `junit.xml`, `mutants/` | Test output (including mutmut's `mutants/` working copy); CI stores what it needs as artifacts. |
| `.terraform/` | Downloaded providers and backend config cache. |
| `*.tfstate*` | State holds resource attributes in plain text, including secrets. |
| `*.tfplan`, `tfplan` | Saved plans can contain secret values. |
| `*.auto.tfvars`, `terraform.tfvars`, `*.tfvars.json` | Variable files are frequently used for secrets. Commit environment config under another name and keep secrets out of it entirely. VERIFY: confirm the chosen variable-file naming scheme when the Terraform module standard is final (F3). |
| `override.tf`, `*_override.tf` | Local-only overrides that must not reach shared environments. |
| `crash.log`, `crash.*.log` | Terraform crash logs can dump variable values. |
| `evals/results/`, `evals/outputs/`, `evals/.cache/` | Model outputs may echo prompts and retrieved data; they are run artifacts, not source. Inputs (datasets, thresholds) are source. |
| `reports/`, `sbom*.json`, `sbom*.xml` | Generated scan and SBOM output; CI publishes them as artifacts. |
| `*.log`, `.local/`, `tmp/`, `*.sqlite3`, `*.db` | Local runtime data that can hold real data. |
| `.idea/`, `.vscode/`, `*.swp`, `.DS_Store`, `Thumbs.db` | Editor and OS noise. |

### What is intentionally not ignored
`uv.lock`, `.python-version`, `.terraform.lock.hcl`, `.env.example`, `CLAUDE.md`, `AGENTS.md`, `.mcp.json`, `.claude/settings.json`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`, `prompts/`, `registry/`, `evals/datasets/`, `evals/thresholds.yaml`, `docs/adr/`.

### Verify the ignore file: `scripts/check_ignore.sh`
This script was run against the canonical block on 2026-11-25. It exits non-zero if a path that must be ignored is not, or a path that must be tracked is ignored. Extend the lists for repo-specific paths.

```bash
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
```

## Canonical `.dockerignore`

The Dockerfile in [00-tech-stack.md](./00-tech-stack.md) copies only `pyproject.toml`, `uv.lock`, `README.md` and `src/`, so those are the only allowed paths. The file is deny-by-default: anything new at the repo root stays out of the image until someone allow-lists it on purpose.

```dockerignore
# Deny by default. Only the paths allow-listed below may enter the build context.
*

# Allow-list: exactly what the Dockerfile copies (uv.lock and pyproject.toml are
# also used by --mount=type=bind, which goes through this file too).
!pyproject.toml
!uv.lock
!README.md
!src

# Re-exclude generated or sensitive files inside allowed paths.
# These MUST stay after the allow rules (the last matching rule wins).
**/__pycache__
**/*.py[cod]
**/*.egg-info
**/.env*
**/*.pem
**/*.key
```

| Entry | Why |
|---|---|
| `*` | Deny by default: `.git/`, `.env*`, `.claude/`, `tests/`, `infra/`, `evals/`, `docs/`, `.venv/` and anything added later stay out of the context. Smaller context also means faster builds. |
| `!pyproject.toml`, `!uv.lock`, `!README.md`, `!src` | The only inputs of the Dockerfile; `README.md` is needed because `pyproject.toml` references it as the project readme. |
| `**/__pycache__`, `**/*.py[cod]`, `**/*.egg-info` | Stale bytecode from the host Python must not ship. |
| `**/.env*`, `**/*.pem`, `**/*.key` | Defense in depth if someone drops a secret inside `src/`. |

Notes for multi-stage builds:
- The runtime stage copies only `/app/.venv` from the builder, so the builder's contents (compilers, caches, `uv`) never ship.
- A test stage that needs `tests/` requires `!tests` (and a separate, non-shipping target). Do not add `!tests` to the shared file without a separate test target.
- Excluding `Dockerfile` and `.dockerignore` through `*` is fine: the builder reads both directly.

### Verify the `.dockerignore`
VERIFY: not executed in the authoring environment (no container daemon available). The patterns follow the documented syntax, but run this once per repo and keep it as a CI job. It builds a throwaway image whose only job is to list the build context:

```dockerfile
# Dockerfile.context-check (CI only, never shipped)
FROM busybox:stable
COPY . /context
RUN find /context -type f | sort
```

```bash
docker build --no-cache --progress=plain -f Dockerfile.context-check . 2>&1 | grep '/context/'
```

The output MUST list only `pyproject.toml`, `uv.lock`, `README.md` and files under `src/`.

## Checklist
- [ ] `.gitignore` equals the canonical block plus entries below the marker.
- [ ] `scripts/check_ignore.sh` passes in CI.
- [ ] `.env.example` is tracked and contains fake values only.
- [ ] `uv.lock` and `.terraform.lock.hcl` (if `infra/` exists) are tracked.
- [ ] `.claude/settings.local.json` and `CLAUDE.local.md` are ignored; shared `.claude/` files are tracked.
- [ ] `.dockerignore` starts with `*` and allow-lists only what the Dockerfile copies.
- [ ] The Dockerfile has no `COPY . .`.
- [ ] The image-content check lists no `.env*`, `.git/`, `.claude/`, tests or key material.
- [ ] No `git add -f` in the MR history for ignored paths.

## Common AI failure modes
| Failure | What to do instead |
|---|---|
| Generates a generic GitHub-style Python `.gitignore` that omits Terraform, Claude local files, eval outputs and `.env.*` | Copy the canonical block verbatim |
| Ignores `uv.lock` or `.terraform.lock.hcl` "because it is generated" | Both are committed for reproducibility |
| Adds `.env` to `.gitignore` but forgets `.env.local`, `.env.production` | Use `.env.*` with the `!.env.example` negation |
| Writes a `.dockerignore` that mirrors `.gitignore` (allow by default) | Deny by default with an allow-list |
| Uses `COPY . .` and relies on the ignore file | Copy named paths only |
| Runs `git add -f` when a needed file is "mysteriously" untracked | Check `git check-ignore -v <path>` and fix the rule in the MR |
| Commits `settings.local.json` because the global exclude on its machine hid it from view | Keep the repo-level entry and the check script |
| Ignores `.claude/` entirely, which drops shared rules, skills and subagents | Ignore only the two personal files |

## Related docs
- [06-secrets-and-env.md](./06-secrets-and-env.md): `.env` rules, secret storage, leak response
- [00-tech-stack.md](./00-tech-stack.md): Dockerfile, Makefile, tool choices
- [08-claude-md.md](./08-claude-md.md): which `.claude/` files are shared vs personal
- [09-structure-and-format.md](./09-structure-and-format.md): repo layout
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): CI jobs, Terraform state
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): eval outputs and evidence retention
