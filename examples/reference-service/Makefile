# Standard Makefile (docs/00-tech-stack.md). Implements TEC-009 (all standard targets),
# TEC-010 (check = what CI runs), TEC-012 (no hidden failures), ARC-015 (lint-imports in lint),
# TST-001 (test = unit + integration). Test targets follow doc 24 where it differs from doc 00.
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

PACKAGE ?= reference_service
IMAGE   ?= reference-service
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

lint: ## Ruff, then architecture contracts (ARC-015)
	$(RUN) ruff check .
	$(RUN) lint-imports

typecheck: ## mypy strict
	$(RUN) mypy

test-unit: ## Unit and architecture tests with coverage gate (doc 24)
	$(RUN) pytest tests/unit --cov=$(PACKAGE) --cov-branch --cov-report=term-missing:skip-covered --cov-report=xml --junitxml=reports/unit.xml

test-integration: ## Integration and contract tests (containers, emulators, specs)
	$(RUN) pytest tests/integration tests/contract -m "integration or contract" --junitxml=reports/integration.xml

test: test-unit test-integration ## Unit then integration/contract tests

eval: ## Model-quality evals (standard in docs/14-evals-and-testing-ai.md)
	$(RUN) pytest evals -m eval --no-cov

registry-check: ## Validate AI tool/agent manifests (docs/25); skips if no registry/
	@if [ -d registry ]; then $(RUN) python scripts/registry_check.py; else echo "no registry/ directory: skipped"; fi

security: ## Dependency audit and secret scan (full set: docs/02-security.md)
	$(RUN) pip-audit --skip-editable
	gitleaks dir --redact --no-banner .

build: ## Build the container image
	docker build --tag $(IMAGE):$(TAG) .

run: ## Run the service locally
	$(RUN) python -m $(PACKAGE).main

check: fmt-check lint typecheck test registry-check ## Same command CI runs
