# Tech Stack

> **Owner:** Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** python.org downloads and devguide.python.org/versions (primary for Python releases); docs.astral.sh (uv, Ruff); mypy documentation; pytest and coverage.py documentation; Docker documentation; gitleaks README; version numbers observed by resolving the example project on 2026-11-25

## Purpose
Single source for tool choices. Every other doc links here instead of restating a tool or version. This doc fixes the reference stack, the Python version policy, and the three files every service starts from: the `Makefile`, the `pyproject.toml` skeleton and the multi-stage `Dockerfile`. Tools marked **proposed** are open for challenge through an ADR; tools marked **required** are decided.

Related decisions: the Copier template that generates these files is future work; until it exists, copy from this doc.

## Rules

- **TEC-001** [MUST] [ci: python-matrix] ASSUMPTION: (F9) The default Python minor for new services is **3.14**. `requires-python` MUST be `">=3.14"` for new services. 3.15 MAY be used for a service once every pinned dependency publishes support (wheels for native packages) and CI is green on it.
- **TEC-002** [MUST] [ci: python-matrix] CI MUST run the full `make check` on the two newest minors that all dependencies support (today 3.14 and 3.15), so that the next default is already proven.
- **TEC-003** [MUST] [review] New services MUST NOT target a Python minor in security-only phase or end of life (3.13 and older as of 2026-11-25). Existing services on 3.13 or older MUST have a migration ADR before the minor's end-of-life date.
- **TEC-004** [MUST] [ci: image-build] The `.python-version` file, the Dockerfile base image minor and CI MUST name the same Python minor.
- **TEC-005** [MUST] [ci: uv sync --locked] ASSUMPTION: (F10) **uv** is the package, lock and virtual-environment manager. `uv.lock` MUST be committed, CI and the Dockerfile MUST use `uv sync --locked`, and a stale lock MUST fail the build.
- **TEC-006** [MUST] [review] Services MUST NOT keep dependency declarations anywhere except `pyproject.toml` (plus `uv.lock`). Hand-maintained `requirements.txt`, `setup.py`, `setup.cfg` and Poetry or Pipenv files MUST NOT be added. Generated exports (for scanners) are allowed and are not committed.
- **TEC-007** [MUST] [lint: ruff] **Ruff** MUST be the only linter and formatter (`ruff check` and `ruff format`). black, isort, flake8 and pylint MUST NOT be added.
- **TEC-008** [MUST] [lint: mypy] **mypy** MUST run with `strict = true` on `src/`, `tests/` and `evals/`. Each `# type: ignore` MUST carry an error code and a reason comment. Format and typing detail is owned by [09-structure-and-format.md](./09-structure-and-format.md).
- **TEC-009** [MUST] [ci: make] Every repo MUST provide the standard Makefile targets: `install`, `fmt`, `fmt-check`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `eval`, `registry-check`, `security`, `build`, `run`, `check`.
- **TEC-010** [MUST] [ci: make check] `make check` (`fmt-check`, `lint`, `typecheck`, `test`, `registry-check`) MUST be the command CI runs for the quality gate. CI MUST NOT run a different or weaker set of commands under the same name.
- **TEC-011** [MUST] [review] Agents and developers MUST run `make check` and see it pass before declaring work done or opening an MR.
- **TEC-012** [MUST] [review] Makefile recipes MUST NOT hide failures (`-` prefixes, `|| true`, `; true`). A target that has nothing to run MUST be fixed, not silenced; empty test directories exit with pytest status 5 and the template ships one tagged smoke test in each of `tests/integration/`, `tests/contract/` and `evals/`.
- **TEC-013** [MUST] [ci: pytest] Tests MUST use **pytest** with strict markers and `filterwarnings = ["error"]`; coverage MUST run with branch coverage. The coverage floor per service tier is owned by [24-testing-standards.md](./24-testing-standards.md); the `fail_under` below is the template default.
- **TEC-014** [MUST] [ci: image-build] Dockerfiles MUST be multi-stage, run as a non-root numeric user, use `uv sync --locked --no-editable --no-dev`, and copy only the virtual environment into the runtime stage.
- **TEC-015** [MUST] [ci: image-scan] Base images and the `uv` image MUST be pinned by tag and digest. `latest` MUST NOT be used. Digest bumps arrive through the dependency-update bot as reviewed MRs. Ignore-file rules for the build context are in [07-ignore-files.md](./07-ignore-files.md).
- **TEC-016** [MUST] [lint: ruff] Configuration MUST live in `pyproject.toml` (Ruff, mypy, pytest, coverage), not in scattered dotfiles, so one file shows the full gate.
- **TEC-017** [MUST] [ci: uv sync --locked] Direct dependencies MUST have a lower bound and an upper bound at the next major (`>=2.9,<3`). Tool versions (ruff, mypy, pytest) live in the `dev` dependency group and are upgraded by reviewed MR.
- **TEC-018** [MUST] [review] Config and validation MUST use pydantic v2 and pydantic-settings; configuration and secret loading rules are in [06-secrets-and-env.md](./06-secrets-and-env.md).
- **TEC-019** [MUST] [review] ASSUMPTION: (F3) Infrastructure is Terraform under `infra/`; GitLab CI/CD is the pipeline. Details live in [16-cicd-and-deployment.md](./16-cicd-and-deployment.md). There are no GitHub-specific files.
- **TEC-020** [MUST] [review] The LLM platform is Microsoft Foundry through the pinned `azure-ai-projects` v2 SDK; details live in [23-azure-foundry-standards.md](./23-azure-foundry-standards.md). Any other provider needs a waiver per [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md).
- **TEC-021** [MUST] [review] Adding, replacing or dropping a tool in the reference stack table MUST be recorded in an ADR and this doc updated in the same MR.
- **TEC-022** [SHOULD] [ci: pre-commit] Repos SHOULD ship `.pre-commit-config.yaml` (ruff, mypy, gitleaks) for fast local feedback. CI remains the enforcement point; a skipped hook MUST NOT be the only barrier.
- **TEC-023** [SHOULD] [review] Each October the platform team SHOULD re-evaluate the default Python minor after the new minor reaches its second maintenance release, and change the default by ADR when all supported dependencies are ready.
- **TEC-024** [SHOULD] [review] Logging and telemetry SHOULD use structlog and OpenTelemetry as defined in [10-logging-observability.md](./10-logging-observability.md).
- **TEC-025** [SHOULD] [review] This doc's version tables SHOULD be re-verified at least quarterly; the "Last verified" date MUST be updated only when the tables were actually re-checked.
- **TEC-026** [MAY] [review] Editors MAY use pyright as an editor-side checker. It MUST NOT be a CI gate; mypy is the gate.

## Reference stack

| Area | Choice | Status | Notes |
|---|---|---|---|
| Language | Python 3.14 default, 3.15 allowed | required (default is `ASSUMPTION:` F9) | See version table below |
| Package manager | uv (lockfile, venv, Python install) | proposed, `ASSUMPTION:` F10 | Alternative if rejected: pip-tools. Observed uv 0.13.9 |
| Lint and format | Ruff | required | Observed 0.17.6 |
| Type checking | mypy, strict | required | Observed 2.4.1 |
| Task runner | Makefile (GNU Make) | required | Tested on GNU Make 3.81; GitLab Linux runners typically ship 4.x. VERIFY: run `make check` once on the real runner image |
| Tests | pytest, pytest-cov, Hypothesis, mutmut, import-linter | required (pytest), rest per [24-testing-standards.md](./24-testing-standards.md) | Observed pytest 9.2.0, pytest-cov 7.1.0, Hypothesis 6.170.17, import-linter 2.17 |
| Config and validation | pydantic v2, pydantic-settings | required | Observed pydantic 2.14.4, pydantic-settings 2.16.3 |
| Containers | Dockerfile (multi-stage, non-root, digest-pinned) and `.dockerignore` | required | Scan with Trivy or GitLab container scanning (decision in [02-security.md](./02-security.md)) |
| CI/CD and hosting | GitLab (`.gitlab-ci.yml`, merge requests, CODEOWNERS) | required (confirmed) | F4 self-managed vs GitLab.com open |
| IaC | Terraform in `infra/` | proposed, `ASSUMPTION:` F3 | Record in ADR |
| Logging | structlog over stdlib logging, JSON | proposed | [10-logging-observability.md](./10-logging-observability.md) |
| Telemetry | OpenTelemetry, OTLP, Azure Monitor export | proposed | [10-logging-observability.md](./10-logging-observability.md) |
| LLM platform | Microsoft Foundry (`azure-ai-projects` v2) | required | [23-azure-foundry-standards.md](./23-azure-foundry-standards.md) |
| Secrets | Azure Key Vault with managed or workload identity | required | [06-secrets-and-env.md](./06-secrets-and-env.md) |
| Dependency audit | pip-audit | proposed | Full scanner set in [02-security.md](./02-security.md) and [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md) |
| Secret scan | gitleaks (also pre-commit) | proposed | `gitleaks dir` and `gitleaks git` confirmed in the project README. The README states the tool is feature complete and receives security patches only: record that in the scanner ADR |
| Hooks | pre-commit | proposed | Convenience only |

"Observed" means the version `uv lock` resolved on 2026-11-25 for the example project in this doc. Services pin through `uv.lock`; this column is a reference point, not a pin.

## Python versions

Confirmed against python.org on 2026-11-25 (downloads page lists 3.15.2 as the latest stable release, dated 2026-10-25; the developer guide's version table gives the dates below). Third-party release trackers disagreed on these dates; python.org is the source of record here.

| Minor | Phase (2026-11-25) | First release | End of support | Use for new services |
|---|---|---|---|---|
| 3.16 | pre-release (planned 2027-10-06) | n/a | 2032-10 | no |
| 3.15 | bugfix | 2026-10-09 | 2031-10 | yes, when all deps support it |
| 3.14 | bugfix | 2025-10-07 | 2030-10 | **yes (default)** |
| 3.13 | security | 2024-10-07 | 2029-10 | no |
| 3.12 | security | 2023-10-02 | 2028-10 | no |
| 3.11 | security | 2022-10-24 | 2027-10 | no |
| 3.10 | end of life | 2021-10-04 | 2026-10-01 | no (unsupported) |

Dates in italics on python.org are scheduled and can move; re-check before relying on a future date. The example project was run through `ruff`, `mypy` and `pytest` on both 3.14.10 and 3.15.2 with the dependency set below and passed on both. That only proves the toy stack, not your service's dependencies; ML and native packages may lag a new minor by months, which is why 3.14 is the default.

## `Makefile`

Checked on 2026-11-25 on GNU Make 3.81 (macOS) against a toy project: `make -n` for every target, and real runs of `install`, `fmt-check`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `eval`, `run` and `check`. Not executed: `security` (gitleaks binary not installed in the authoring environment) and `build` (no container daemon). `.SHELLFLAGS` needs GNU Make 3.82 or later; older versions ignore it harmlessly.

```make
# Standard Makefile. Every repo MUST provide these targets (docs/00-tech-stack.md).
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

PACKAGE ?= my_service
IMAGE   ?= my-service
TAG     ?= dev
RUN     := uv run --locked

.PHONY: help install fmt fmt-check lint typecheck test test-unit test-integration \
        eval registry-check security build run check

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "%-18s %s\n", $$1, $$2}'

install: ## Create .venv from uv.lock (fails if the lock is stale)
	uv sync --locked

fmt: ## Format and apply safe lint fixes
	$(RUN) ruff format .
	$(RUN) ruff check --fix .

fmt-check: ## Verify formatting (no changes)
	$(RUN) ruff format --check .

lint: ## Lint
	$(RUN) ruff check .

typecheck: ## mypy strict
	$(RUN) mypy

test: ## Tests except integration, contract and eval, with coverage gate
	$(RUN) pytest -m "not integration and not contract and not eval"

test-unit: ## Unit tests only
	$(RUN) pytest tests/unit -m "not integration and not contract and not eval"

test-integration: ## Integration and contract tests (containers, emulators, specs)
	$(RUN) pytest tests/integration tests/contract -m "integration or contract" --no-cov

eval: ## Model-quality evals (standard in docs/14-evals-and-testing-ai.md)
	$(RUN) pytest evals -m eval --no-cov

registry-check: ## Validate AI tool/agent manifests (docs/25-ai-tool-and-agent-registry.md); skips if no registry/
	@if [ -d registry ]; then $(RUN) python scripts/registry_check.py; else echo "no registry/ directory: skipped"; fi

security: ## Dependency audit and secret scan (full set: docs/02-security.md)
	$(RUN) pip-audit --skip-editable
	gitleaks dir --redact --no-banner .

build: ## Build the container image
	docker build --tag $(IMAGE):$(TAG) .

run: ## Run the service locally
	$(RUN) python -m $(PACKAGE).main

check: fmt-check lint typecheck test registry-check ## Same command CI runs
```

Notes:
- `uv run --locked` fails when `uv.lock` does not match `pyproject.toml`, so a stale lock cannot pass `make check`.
- `eval` and `test-integration` run with `--no-cov` because the coverage gate belongs to unit-level `test`.
- The `security` target is the minimal local subset. The SAST, container and IaC scanners are defined in [02-security.md](./02-security.md) and run in CI.

## `pyproject.toml` skeleton

Checked on 2026-11-25: parsed with `tomllib`, then `uv sync`, `ruff format --check`, `ruff check`, `mypy` and `pytest` all passed on a toy package under Python 3.14 and 3.15. Rule selection is a starting point: complexity and size thresholds are owned by [11-clean-code.md](./11-clean-code.md), and style detail by [09-structure-and-format.md](./09-structure-and-format.md).

```toml
[build-system]
requires = ["uv_build>=0.13,<0.14"]
build-backend = "uv_build"

[project]
name = "my-service"
version = "0.1.0"
description = "Example service"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "pydantic>=2.9,<3",
    "pydantic-settings>=2.6,<3",
]

[dependency-groups]
dev = [
    "ruff>=0.17",
    "mypy>=2.4",
    "pytest>=9",
    "pytest-cov>=6",
    "hypothesis>=6.100",
    "import-linter>=2",
    "pip-audit>=2.7",
]

[tool.uv]
required-version = ">=0.13"

[tool.ruff]
line-length = 100
target-version = "py314"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "B", "UP", "N", "S", "C4", "C90", "SIM", "RUF", "PL", "PT",
    "ANN", "ASYNC", "T20", "TID", "DTZ", "PERF", "ERA",
]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "PLR2004"]
"evals/**" = ["S101", "ANN", "PLR2004"]

[tool.ruff.lint.isort]
known-first-party = ["my_service"]

[tool.ruff.format]
docstring-code-format = true

[tool.mypy]
python_version = "3.14"
strict = true
files = ["src", "tests", "evals"]
warn_unreachable = true
explicit_package_bases = true
mypy_path = "src"
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --import-mode=importlib --strict-markers --strict-config --cov --cov-report=term-missing"
markers = [
    "integration: needs real dependencies (containers or emulators)",
    "contract: validates responses or schemas against a published spec",
    "eval: model-quality evals, run by make eval",
]
filterwarnings = ["error"]

[tool.coverage.run]
branch = true
source = ["my_service"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_also = ["if TYPE_CHECKING:", "raise NotImplementedError", "if __name__ == .__main__.:"]
```

Notes:
- `uv_build` is uv's own build backend; its version range must follow the installed uv minor. VERIFY: confirm with the platform team that `uv_build` is acceptable, or switch to another PEP 517 backend.
- The skeleton assumes `evals/`, `tests/integration/` and `tests/contract/` exist and contain at least one marker-tagged test, as the template provides (`tests/contract/` is run by `make test-integration`, following the testing standard). mypy fails on a missing path listed in `files`.
- `--import-mode=importlib` and mypy `explicit_package_bases` avoid the "Duplicate module named" error when `tests/` and `evals/` hold files with the same name (found while testing this skeleton).
- `S101` (assert) is allowed only in tests and evals. Do not widen `per-file-ignores` to `src/`.
- `fail_under = 80` is the template default, not the standard; see [24-testing-standards.md](./24-testing-standards.md).
- import-linter contracts (layering) are configured in the repo-root `.importlinter` file as defined in [03-architecture.md](./03-architecture.md).

## `Dockerfile` (multi-stage, non-root, digest-pinned)

VERIFY: this Dockerfile was **not built** in the authoring environment (no container daemon was available). The instructions follow the uv Docker integration guide (cache mounts, `--no-install-project`, `--no-editable`, copy only `.venv` into the runtime stage). Build it once in CI before adopting it. The `REPLACE_WITH_DIGEST` placeholders make the build fail on purpose until real digests are set. Also VERIFY: that image tag `ghcr.io/astral-sh/uv:0.13.9` exists in your registry mirror.

```dockerfile
# syntax=docker/dockerfile:1
# Pin both images by digest. Resolve a digest with: docker buildx imagetools inspect <image:tag>
ARG PYTHON_IMAGE=python:3.14-slim@sha256:REPLACE_WITH_DIGEST
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.9@sha256:REPLACE_WITH_DIGEST

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS builder
COPY --from=uv /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# Layer 1: third-party dependencies only; cached until uv.lock or pyproject.toml change
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --no-dev
# Layer 2: the project itself, installed non-editable into the venv
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

FROM ${PYTHON_IMAGE} AS runtime
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "my_service.main"]
```

Notes:
- Both stages use the same Python image so the virtual environment's interpreter path resolves in the runtime stage (`UV_PYTHON_DOWNLOADS=0` forces the system Python).
- No secrets are passed as build arguments or `ENV`. Runtime configuration arrives through environment variables injected by the platform; see [06-secrets-and-env.md](./06-secrets-and-env.md).
- Image scanning, SBOM and signing requirements are owned by [02-security.md](./02-security.md) and [16-cicd-and-deployment.md](./16-cicd-and-deployment.md).

## `.pre-commit-config.yaml` (optional convenience)
The YAML passes `pre-commit validate-config`, but the hooks were not run (VERIFY: run `pre-commit run --all-files` once; the gitleaks `rev` is a placeholder). Use the local-hook form so hooks use the locked tool versions. Pin the gitleaks `rev` to the current release tag.

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run --locked ruff format
        language: system
        types: [python]
      - id: ruff-check
        name: ruff check
        entry: uv run --locked ruff check --fix
        language: system
        types: [python]
      - id: mypy
        name: mypy
        entry: uv run --locked mypy
        language: system
        pass_filenames: false
  - repo: https://github.com/gitleaks/gitleaks
    rev: v0.0.0-REPLACE-WITH-CURRENT-TAG
    hooks:
      - id: gitleaks
```

## Checklist
- [ ] `requires-python`, `.python-version`, Dockerfile base image and CI matrix agree (TEC-001, TEC-004).
- [ ] `uv.lock` committed; CI uses `uv sync --locked`.
- [ ] All 14 Makefile targets exist and none hides a failure.
- [ ] CI runs `make check`, not a bespoke command list.
- [ ] Ruff and mypy settings live in `pyproject.toml`; mypy is strict.
- [ ] Dockerfile is multi-stage, non-root, base and uv images pinned by digest.
- [ ] `.dockerignore` and `.gitignore` copied from [07-ignore-files.md](./07-ignore-files.md).
- [ ] No black, isort, flake8, pylint, `requirements.txt` or `setup.py`.
- [ ] Any deviation from the reference stack has an ADR.

## Common AI failure modes
| Failure | What to do instead |
|---|---|
| Picks Python 3.12 or 3.13 because they dominate training data | Use 3.14 default; check the version table |
| Adds `black`, `isort`, `flake8` or `pylint` next to Ruff | Ruff only |
| Generates `requirements.txt` plus `pip install -r` in the Dockerfile | `pyproject.toml`, `uv.lock`, `uv sync --locked` |
| Uses `FROM python:latest` or a tag without a digest | Pin tag and digest |
| Runs the container as root, or `COPY . .` into the runtime image | Non-root numeric user; copy only `.venv` |
| Creates a Makefile with `.PHONY` missing, spaces instead of tabs, or `-` prefixes that hide errors | Copy the standard Makefile |
| Sets mypy to non-strict or sprinkles bare `# type: ignore` | Strict, with codes and reasons |
| Declares done after `pytest` only | Run `make check` |
| Invents tool versions from memory | Take versions from `uv.lock`; mark anything unverified `VERIFY:` |
| Adds GitHub Actions workflows or other GitHub-specific automation files | GitLab CI only |

## Related docs
- [07-ignore-files.md](./07-ignore-files.md): `.gitignore`, `.dockerignore`
- [06-secrets-and-env.md](./06-secrets-and-env.md): config, secrets, identities
- [09-structure-and-format.md](./09-structure-and-format.md): layout, naming, formatting
- [08-claude-md.md](./08-claude-md.md): agent entry files that tell agents to run `make check`
- [24-testing-standards.md](./24-testing-standards.md): coverage floors, test layout
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): pipeline stages
- [02-security.md](./02-security.md): scanners, image signing
- [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md): registries, update cadence
