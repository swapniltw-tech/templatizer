# Commands for this template repository. Run `make help` for the list.
# (The generated service has its own Makefile: templates/ai-python-template/template/Makefile.jinja.)

PYTHON   ?= python3 -I
COPIER   ?= uvx --from copier copier
TEMPLATE := templates/ai-python-template

.DEFAULT_GOAL := help
.PHONY: help new docs-check rules-export rules rules-check citations check

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

new: ## Generate a service: make new DEST=../my-service
	@test -n "$(DEST)" || { echo "usage: make new DEST=<destination>"; exit 2; }
	$(COPIER) copy --trust $(TEMPLATE) $(DEST)

docs-check: ## Check the standards docs against their conventions
	$(PYTHON) scripts/check_docs.py

rules-export: ## Docs -> rules.yml
	$(PYTHON) scripts/check_docs.py --export

rules: ## Write the agent rule files from rules.yml
	$(PYTHON) tools/gen_agent_rules.py

rules-check: ## Fail if the agent rule files are stale
	$(PYTHON) tools/gen_agent_rules.py --check

citations: ## Fail if the template cites an unknown or retired rule ID
	$(PYTHON) tools/check_rule_citations.py

check: docs-check rules-check citations ## Everything CI runs, plus the docs check
