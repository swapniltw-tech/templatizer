# templatizer

Templates that implement the engineering standards in `docs/engineering-principles/` (draft). The main template generates a Python AI service that already follows those standards: src layout, Makefile, CI, import contracts, and agent configuration for Claude Code and GitLab Duo.

## Prerequisites

| Tool | Why |
|---|---|
| [`uv`](https://docs.astral.sh/uv/) | Runs copier (`uvx`), and is the package manager of generated services |
| `make` | Entry point for every command in this repo |
| `python3` | Runs the repo's checks and generators (standard library only) |
| `git` | A generated service must be a git work tree before `make check` |

## Quick start

```bash
make new DEST=../my-service          # prompts for service name, package name, description, ...
cd ../my-service
git init && make install && make check
```

`make new` runs `copier copy --trust`. `--trust` is required because the template runs `uv lock` and generates `docs/api/openapi.yaml` after copying.

Placeholders (`example-org/...`, `<approved-registry>`, image digests) must be replaced before real use. `grep -rn "TODO\|ASSUMPTION:\|VERIFY:" .` lists what is still open.

## Make targets

Run `make help` for the list. All commands in this repo go through `make`.

| Target | What |
|---|---|
| `make new DEST=<dir>` | Generate a service from `templates/ai-python-template` into `<dir>` |
| `make docs-check` | Check the standards docs against their conventions |
| `make rules-export` | Docs → `rules.yml` (repo root) |
| `make rules` | Write the agent rule files from `rules.yml` |
| `make rules-check` | Fail if the agent rule files are stale |
| `make citations` | Fail if the template cites an unknown or retired rule ID |
| `make check` | `docs-check` + `rules-check` + `citations` |

The Makefile variables `PYTHON` and `COPIER` can be overridden, for example `make new COPIER="copier" DEST=../x` if copier is installed globally.

The generated service has its own Makefile (`install`, `fmt`, `lint`, `typecheck`, `test`, `check`, `build`, ...); see `templates/ai-python-template/template/Makefile.jinja`.

## Repository layout

| Path | What |
|---|---|
| `templates/ai-python-template/` | Copier template for a Python service |
| `docs/engineering-principles/` | The engineering standards the template is built on; start at its `README.md`. `docs/engineering-principles-summary.md` is the two-page version |
| `rules.yml` | Every rule from the standards, generated from the docs; input to the tools below |
| `scripts/check_docs.py` | Checks the standards docs against their conventions; `--export` writes `rules.yml` |
| `tools/gen_agent_rules.py` | Generates the `.claude/rules/*.md` files (security, clean-code, api-contracts, architecture, domain-code, observability) and the GitLab Duo files `.gitlab/duo/chat-rules.md` and `mr-review-instructions.yaml` from `rules.yml` |
| `tools/check_rule_citations.py` | Fails when a file in the template cites an unknown or retired rule ID, or none at all |
| `Makefile` | Entry point for every command in this repo |
| `.gitlab-ci.yml` | This repo's CI: runs the generator `--check` and the citation check |

## Changing the standards or the template

1. Edit the docs in `docs/engineering-principles/`.
2. `make rules-export` to refresh `rules.yml`.
3. `make rules` to regenerate the agent rule files in the template.
4. `make check` before pushing. CI fails on stale rule files or bad rule citations.

`python-style.md` and `testing.md` are copied from doc 08 and are not generated.
