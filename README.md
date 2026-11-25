# ai-code-template

Templates that implement the engineering standards in `canada-life/docs/` (draft).

| Path | What |
|---|---|
| `templates/service/` | Copier template for a Python service (src layout, Makefile, CI, import contracts, agent config) |
| `examples/reference-service/` | A service generated from the template, plus one business endpoint |
| `tools/gen_agent_rules.py` | Generates the `.claude/rules/*.md` files (security, clean-code, api-contracts, architecture, domain-code, observability) from `rules.yml`; run it after the docs or the selection change, `--check` fails when outputs are stale |
| `docs/FINDINGS.md` | Contradictions and gaps found in the standards while building (read this first) |

## Use

```bash
uvx --from copier copier copy --trust templates/service <destination>
cd <destination> && git init && make install && make check
```

`--trust` is required because the template runs `uv lock` and generates `docs/api/openapi.yaml` after copying. Placeholders (`example-org/...`, `<approved-registry>`, image digests) must be replaced before real use; `grep -rn "TODO\|ASSUMPTION:\|VERIFY:"` lists what is still open.

## Regenerate agent rule files

```bash
# rules.yml comes from: python3 -I scripts/check_docs.py --export  (in the standards repo)
python3 -I tools/gen_agent_rules.py --rules <path>/rules.yml          # write
python3 -I tools/gen_agent_rules.py --rules <path>/rules.yml --check  # exit 1 if stale
```

`python-style.md` and `testing.md` are copied from doc 08 and are not generated.
