# ai-code-template

Templates that implement the engineering standards in `canada-life/docs/` (draft).

| Path | What |
|---|---|
| `templates/service/` | Copier template for a Python service (src layout, Makefile, CI, import contracts, agent config) |
| `examples/reference-service/` | A service generated from the template, plus one business endpoint |
| `docs/FINDINGS.md` | Contradictions and gaps found in the standards while building (read this first) |

## Use

```bash
uvx --from copier copier copy --trust templates/service <destination>
cd <destination> && git init && make install && make check
```

`--trust` is required because the template runs `uv lock` and generates `docs/api/openapi.yaml` after copying. Placeholders (`example-org/...`, `<approved-registry>`, image digests) must be replaced before real use; `grep -rn "TODO\|ASSUMPTION:\|VERIFY:"` lists what is still open.
