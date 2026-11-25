# RAG and Retrieval

> **Owner:** AI Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** OWASP LLM08:2025 Vector and Embedding Weaknesses (genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses); Azure AI Search docs on document-level access and security filters (learn.microsoft.com/azure/search). Items not confirmed there are marked `VERIFY:`.

## Purpose
Defines how we retrieve context for LLMs: pick the simplest retrieval that works (structured or vectorless first), then vector or hybrid when needed; enforce document-level access at retrieval; require citations; defend the index against poisoning; keep PII out of indexes and propagate deletions. Decision rationale for "RAG vs prompt vs fine-tune" is owned by [05-decision-playbook.md](./05-decision-playbook.md). Retrieval eval mechanics (datasets, gates, evidence) are owned by [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md); this doc defines the retrieval metrics. Data classes and PIA triggers are owned by [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md).

## Retrieval ladder
| Step | Use when | Examples |
|---|---|---|
| 1. Direct lookup | Entity is known (policy number, claim ID) | SQL or API call by key, no LLM retrieval |
| 2. Structured / vectorless | Documents have structure: headings, tables, metadata, controlled vocabulary | Metadata filters, keyword/BM25 search, section-tree navigation, table queries |
| 3. Vector | Meaning matters more than wording; paraphrase-heavy corpora | Embedding similarity over chunks |
| 4. Hybrid | Both exact terms (product codes, clause numbers) and semantics matter | Keyword plus vector, fused ranking, optional reranker |

Escalate one step only when a retrieval eval (EVL suite per doc 14) shows the lower step fails the threshold. Record the choice in an ADR.

## Rules

### Choosing the pattern
- **RAG-001** [MUST] [review] A design MUST start at the lowest sufficient step of the retrieval ladder and justify any move to vector or hybrid with eval results in the ADR.
- **RAG-002** [SHOULD] [review] Structured sources (databases, forms, policy admin data) SHOULD be queried through typed tools or SQL with schema-scoped access, not embedded into a vector index.
- **RAG-003** [MUST] [test] Retrieval MUST be a separate, testable component (`ai/retrieval/`) with its own eval suite before it is composed into an agent.

### Chunking and embeddings
- **RAG-004** [SHOULD] [review] Chunk along document structure (sections, clauses, table rows) rather than fixed character windows; each chunk SHOULD carry a title path, source ID, version and language as metadata.
- **RAG-005** [MUST] [review] Chunk size, overlap and embedding deployment MUST be recorded in config and changed only via MR; any change MUST trigger a full re-index and a retrieval eval re-run.
- **RAG-006** [MUST] [ci] The embedding model deployment MUST be an approved Foundry deployment referenced by a placeholder-style config name (for example `<embedding-deployment>`), version-pinned per [15-llm-and-model-governance.md](./15-llm-and-model-governance.md); mixing embeddings from different models in one index MUST NOT occur.
- **RAG-007** [MUST] [test] Bilingual corpora MUST store language per chunk and be evaluated with EN queries over FR documents and the reverse; the embedding choice MUST be validated for both languages.

### Freshness
- **RAG-008** [MUST] [runtime] Each index MUST have a documented freshness SLO (maximum age of source change to searchable) and a monitor that alerts on breach.
- **RAG-009** [SHOULD] [runtime] Indexing SHOULD be incremental with change detection; a full rebuild SHOULD use a new index plus alias swap so it can be rolled back.
- **RAG-010** [MUST] [review] Superseded document versions MUST be removed or flagged inactive so retrieval does not return stale policy wording.

### Access control
- **RAG-011** [MUST] [test] Document-level access control MUST be enforced at retrieval time by filtering on the caller's identity, never by asking the model to withhold content; unauthorized chunks MUST NOT enter the prompt.
- **RAG-012** [MUST] [test] The caller identity used in the filter MUST come from the verified end-user token or session, never from model output or request text.
- **RAG-013** [MUST] [ci] A cross-user leakage eval MUST run on every retrieval change: queries as user A MUST return zero chunks only user B may see (threshold 0 leaks).
- **RAG-014** [MUST] [review] Permission metadata in the index MUST be refreshed when source permissions change; the maximum staleness MUST be stated and approved (ASSUMPTION: no more than the freshness SLO).
- **RAG-015** [MUST] [review] Index write roles MUST be separated from query roles, and the query identity MUST NOT hold a role that bypasses document filters.
- **RAG-016** [SHOULD] [review] Indexes SHOULD be partitioned by data classification so restricted content is never co-mingled with lower classes ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).

### Citations and grounding
- **RAG-017** [MUST] [test] Every generated answer that uses retrieved content MUST include citations that resolve to chunk IDs and source documents the caller is authorized to see.
- **RAG-018** [MUST] [test] A citation checker MUST verify that each cited chunk was actually retrieved in that request and supports the claim; uncitable claims MUST be omitted or marked as not grounded.
- **RAG-019** [SHOULD] [test] When retrieval returns nothing above the relevance threshold, the system SHOULD answer "not found" and escalate, rather than answer from model memory.

### Poisoning and untrusted content
- **RAG-020** [MUST] [review] Retrieved text MUST be treated as untrusted input (indirect prompt injection); it MUST be delimited from instructions and MUST NOT be able to trigger tool calls without the normal approval gates ([02-security.md](./02-security.md)).
- **RAG-021** [MUST] [ci] Ingestion MUST accept documents only from allow-listed sources, record provenance (source, uploader, hash, time) per chunk, and quarantine documents failing content checks.
- **RAG-022** [MUST] [test] An injection-in-document suite (planted instructions in indexed text) MUST run per doc 14 and pass before release.
- **RAG-023** [SHOULD] [manual] Embedding inversion and cross-tenant leakage risks (OWASP LLM08:2025, Vector and Embedding Weaknesses) SHOULD be reviewed in threat modeling for each index; `VERIFY:` whether a 2026 OWASP LLM list edition has renumbered this entry before citing "LLM08" externally.

### PII, retention and deletion
- **RAG-024** [MUST] [ci] Content MUST be classified before indexing; restricted data MUST NOT be indexed without an approved PIA per doc 13, and PII SHOULD be removed or tokenized before embedding.
- **RAG-025** [MUST] [test] A deletion request or retention expiry for a source document MUST propagate to chunks, embeddings, caches, eval datasets and backups per the schedule in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); a test MUST confirm the deleted ID is no longer retrievable.
- **RAG-026** [MUST] [runtime] Query text and retrieved chunks written to logs or traces MUST follow the redaction rules in [10-logging-observability.md](./10-logging-observability.md); retrieved content MUST NOT be logged by default.

### Retrieval evals
- **RAG-027** [MUST] [ci] Each retriever MUST have a golden query set with labeled relevant chunks, measuring recall at k, MRR or nDCG, citation correctness and leakage rate, gated through `evals/thresholds.yaml` per doc 14.
- **RAG-028** [SHOULD] [ci] Retrieval and generation SHOULD be evaluated separately so a failure can be attributed to one stage.

## Azure AI Search specifics
Confirmed from Microsoft Learn (search results summarizing the pages; re-read the pages before implementing):
- **Security filters** (store allowed user/group IDs in a filterable string field; pass the caller's identities as a filter at query time) are documented as the pattern for custom identity systems and push-model indexes. The principal is only a string match, not authentication; keep the field non-retrievable but do not treat that as a security boundary.
- **Native ACL/RBAC document-level permissions** (permission metadata ingested from sources such as ADLS Gen2, with the user's Microsoft Entra token passed on the query in the `x-ms-query-source-authorization` header) are described as **preview**. Preview use needs a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)); default to security filters. `VERIFY:` current status and supported sources.
- Permissions captured at indexing are only as fresh as the last sync; reindex when source permissions change.
- A caller with a data-contributor role on the index can bypass permission filters; restrict that role (RAG-015).
- `VERIFY:` hybrid search, semantic ranker, integrated vectorization, private endpoint, and Canada region availability and feature parity before committing to them; the service and product naming (Foundry IQ) have changed recently.

## Checklist
- [ ] ADR records the retrieval ladder step and eval evidence.
- [ ] Chunking, embedding deployment and index config in versioned config.
- [ ] Freshness SLO and monitor defined.
- [ ] Access filter uses verified caller identity; leakage eval at zero.
- [ ] Citations resolve to authorized, actually retrieved chunks.
- [ ] Injection-in-document suite passes.
- [ ] Classification and PIA done before indexing; deletion propagation tested.
- [ ] Retrieval evals gate in CI.

## Common AI failure modes
- Reaching for a vector store for data that a SQL query or metadata filter answers exactly.
- Telling the model in the prompt to "only show documents the user may see".
- Filtering on a user ID the model supplied.
- Fixed-size chunks that split clauses and tables.
- Citations the model invented or that were never retrieved.
- Indexing PII or restricted documents "temporarily" and never purging embeddings.
- Forgetting to re-index after changing the embedding model.
- Trusting retrieved text as instructions.
- Citing OWASP numbering from memory.

## Related docs
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md), [05-decision-playbook.md](./05-decision-playbook.md)
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md), [02-security.md](./02-security.md)
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md), [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)
- [10-logging-observability.md](./10-logging-observability.md), [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md), [22-localization-and-accessibility.md](./22-localization-and-accessibility.md)
