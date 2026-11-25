# ai-code-template

Templates that implement the engineering standards in `canada-life/docs/` (draft).

| Path | What |
|---|---|
| `templates/service/` | Copier template for a Python service (src layout, Makefile, CI, import contracts, agent config) |
| `examples/reference-service/` | A service generated from the template, plus one business endpoint |
| `tools/gen_agent_rules.py` | Generates the `.claude/rules/*.md` files (security, clean-code, api-contracts, architecture, domain-code, observability) from `rules.yml`; run it after the docs or the selection change, `--check` fails when outputs are stale |
| `tools/check_rule_citations.py`, `tools/rules.yml` | Fails when a file in the template or example cites an unknown or retired rule ID or none at all; `rules.yml` is a snapshot of the standards export |
| `.gitlab-ci.yml` | This repo's CI: runs the generator `--check` and the citation check |
| `docs/FINDINGS.md` | Contradictions and gaps found in the standards while building (read this first) |

## Use

```bash
uvx --from copier copier copy --trust templates/service <destination>
cd <destination> && git init && make install && make check
```

`--trust` is required because the template runs `uv lock` and generates `docs/api/openapi.yaml` after copying. Placeholders (`example-org/...`, `<approved-registry>`, image digests) must be replaced before real use; `grep -rn "TODO\|ASSUMPTION:\|VERIFY:"` lists what is still open.

## Regenerate agent rule files

```bash
# rules.yml comes from: python3 -I scripts/check_docs.py --export  (in the standards repo); the CI reads the snapshot tools/rules.yml
cp <path>/rules.yml tools/rules.yml                                    # refresh the snapshot
python3 -I tools/gen_agent_rules.py                                    # write
python3 -I tools/gen_agent_rules.py --check                            # exit 1 if stale
python3 -I tools/check_rule_citations.py                               # cited IDs exist
```

`python-style.md` and `testing.md` are copied from doc 08 and are not generated.
