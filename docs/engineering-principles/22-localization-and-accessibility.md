# Localization and Accessibility

> **Owner:** Product Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** WCAG 2.2, W3C Recommendation (w3.org/TR/WCAG22); Office quebecois de la langue francaise (oqlf.gouv.qc.ca) guidance on the Charter of the French language. Legal and standards claims beyond these are marked `VERIFY:`. **Not legal advice; confirm with Legal.**

## Purpose
Defines English and French (EN/FR) output, locale handling, translation evals and accessibility for user-facing UIs. EN/FR is in scope (recorded decision 4). Quebec language requirements and the WCAG target level are unresolved (F6), so they are written as assumptions below. Eval mechanics are owned by [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md); API-level locale handling is owned by [17-api-and-contracts.md](./17-api-and-contracts.md); this doc owns what is required of the content and UI.

## Legal context (summary; not legal advice, confirm with Legal)
- ASSUMPTION: Customer-facing services offered to people in Quebec must offer French with at least equivalent quality and terms to any English version. OQLF guidance states, as a summary of the Charter of the French language, that software must be available in French unless no French version exists, and that product inscriptions and user directions must be in French. `VERIFY:` the exact sections (the OQLF summary cites s. 51 and s. 52.1) and whether they apply to our products, on legisquebec.gouv.qc.ca, and which Bill 96 amendments apply.
- ASSUMPTION: Staff-facing tools used by Quebec employees also need French versions (OQLF states employers must provide French versions of software). `VERIFY:` with Legal.
- Insurance-specific rules for policy documents and regulator-mandated wording (federal and provincial) are out of scope here. `VERIFY:` with Compliance whether specific documents have prescribed French text.
- Confirm with Legal: whether AI-generated French needs human review before sending, and any requirement to disclose AI use (F6).

## Rules

### Language and output
- **LOC-001** [MUST] [review] Every user-facing string and AI-generated output for Quebec-facing or bilingual products MUST be available in French and English with equivalent content, quality and availability; confirm with Legal (F6).
- **LOC-002** [MUST] [test] The response language MUST be decided by an explicit, testable rule (user preference, then `Accept-Language`, then default); the model MUST NOT guess language from a single word.
- **LOC-003** [MUST] [test] AI output MUST be in the requested language only, with no unrequested mixing, except for proper nouns, product names and legally defined terms.
- **LOC-004** [SHOULD] [review] Regulated or legally significant text (policy wording, denials, disclosures) SHOULD come from approved bilingual templates, not free-form generation; AI MAY draft, a qualified human MUST approve before it is sent (ASSUMPTION; confirm with Legal).
- **LOC-005** [MUST] [review] A glossary of approved EN/FR insurance terms MUST be kept under version control and used in prompts and checks; ASSUMPTION: Canadian French (OQLF terminology, Grand dictionnaire terminologique) is the target variety, not European French. `VERIFY:` the terminology resource with Legal or the language team.
- **LOC-006** [MUST] [test] Language-switching and refusal messages (errors, guardrail blocks, escalations) MUST exist in both languages.

### Locale handling
- **LOC-007** [MUST] [test] Locale MUST be a BCP 47 tag (`en-CA`, `fr-CA`) carried as an explicit request or user attribute; code MUST NOT infer locale from server settings.
- **LOC-008** [MUST] [lint: ruff] Dates, times, numbers and currency MUST be formatted through a locale library (ASSUMPTION: Babel; `VERIFY:` approval in [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md)), never by string concatenation. Examples: `fr-CA` uses a space for thousands and a comma for decimals; format stored data as ISO 8601 and currency as ISO 4217 amounts.
- **LOC-009** [MUST] [test] Stored data and API payloads MUST stay locale-neutral (ISO dates, numeric amounts, codes); localization MUST happen at the presentation boundary.
- **LOC-010** [MUST] [test] Text handling MUST be Unicode-safe: UTF-8 end to end, NFC normalization for comparison, accented characters preserved in search, sorting (locale collation) and PII matching.
- **LOC-011** [SHOULD] [test] Strings SHOULD live in message catalogs (for example gettext `.po` files), with plural and gender handled by the catalog; code MUST NOT embed user-facing text in logic. UI layouts SHOULD tolerate FR text, which is commonly longer than EN.
- **LOC-012** [MUST] [review] Names, addresses and postal codes MUST NOT be restricted to ASCII; forms MUST accept accented and hyphenated characters.

### Translation and bilingual evals
- **LOC-013** [MUST] [ci] Any feature producing translated or bilingual output MUST have a bilingual eval slice in its golden dataset, with EN to FR, FR to EN and native-FR prompts, gated through `evals/thresholds.yaml` per doc 14.
- **LOC-014** [MUST] [test] Translation evals MUST check deterministically: glossary term compliance, preserved numbers, dates, amounts, names and placeholders, no untranslated segments, and correct language detection.
- **LOC-015** [SHOULD] [review] Quality judged by an LLM SHOULD use a rubric (adequacy, fluency, terminology, register) calibrated against labels from a qualified bilingual reviewer; the judge MUST NOT be the sole evidence for legally significant text.
- **LOC-016** [MUST] [test] Parity MUST be measured: the FR quality score MUST NOT fall below the EN score by more than a stated margin (ASSUMPTION: 3 percentage points); FR failures block release even if EN passes.
- **LOC-017** [SHOULD] [manual] A bilingual human reviewer SHOULD sample production output per doc 14 online-monitoring rules for both languages.
- **LOC-018** [MUST] [review] Translation and eval data MUST be synthetic or de-identified ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)); text sent to a translation model is subject to the same data-class rules as any prompt.
- **LOC-019** [MUST] [test] Retrieval over bilingual content MUST follow the language rules in [19-rag-and-retrieval.md](./19-rag-and-retrieval.md) and cite sources in the response language where a translation exists.

### Accessibility
- **LOC-020** [MUST] [ci: automated a11y scan] ASSUMPTION: The target is **WCAG 2.2 Level AA** for all user-facing web UIs (F6; confirm with Legal and Product). Automated accessibility scanning (for example axe-core via a browser test; `VERIFY:` tool approval) MUST run in CI and block on violations.
- **LOC-021** [MUST] [review] Automated scans catch only part of the issues; each user-facing release MUST also pass a manual check: keyboard-only operation, visible focus, screen reader pass on the main flows, 200 percent zoom and reflow.
- **LOC-022** [MUST] [review] WCAG 2.2 additions at Level AA MUST be covered: focus not obscured (2.4.11), dragging alternatives (2.5.7), minimum target size (2.5.8), accessible authentication (3.3.8). Verified against w3.org/TR/WCAG22.
- **LOC-023** [MUST] [test] The page language MUST be set (`lang="en-CA"` or `lang="fr-CA"`) and changes of language within content MUST be marked up, so screen readers pronounce correctly.
- **LOC-024** [MUST] [review] AI chat and generative UIs MUST: announce new messages to assistive technology (live regions), keep focus predictable on streamed output, not disappear or time out without warning, offer a text alternative for any generated image or chart, and provide an accessible path to a human.
- **LOC-025** [MUST] [review] Generated content MUST use plain language and structure (headings, lists) and MUST NOT rely on color, position or sound alone to convey meaning.
- **LOC-026** [SHOULD] [review] Accessibility conformance evidence (scan reports, manual test notes, known issues) SHOULD be stored with the release record; known failures MUST have an owner and date.
- **LOC-027** [SHOULD] [review] Voice interfaces and generated documents (PDF, email) SHOULD meet equivalent accessibility requirements (tagged PDF, text alternatives); `VERIFY:` applicable standard with Legal.

### Canadian accessibility context
- **LOC-028** [MUST] [manual] Product and Legal MUST confirm which accessibility laws and standards apply to each product before first release and record the answer in an ADR. `VERIFY:` candidates for Legal to assess: the federal Accessible Canada Act and its regulations, provincial laws (for example Ontario AODA, Quebec requirements), and the Canadian standard CAN/ASC EN 301 549 (Accessibility requirements for ICT products and services). None of these is confirmed applicable here.

## Checklist
- [ ] Legal has confirmed Quebec language scope (F6) and the answer is recorded.
- [ ] All user-facing strings and AI outputs exist in EN and FR with a tested language-selection rule.
- [ ] Glossary under version control; legal text from approved templates.
- [ ] Dates, numbers, currency use a locale library; storage is locale-neutral.
- [ ] Bilingual eval slice with parity margin gates release.
- [ ] WCAG 2.2 AA scan in CI plus manual keyboard and screen reader check.
- [ ] AI chat UI has live-region announcements and a human path.
- [ ] Applicable Canadian accessibility laws recorded in an ADR.

## Common AI failure modes
- Hard-coding English strings and "translating" by prompt at runtime with no glossary.
- Answering in English to a French question, or mixing languages mid-answer.
- European French vocabulary or false friends in Canadian-French output.
- Formatting numbers and dates with f-strings.
- Evaluating only English and shipping FR unchecked.
- Claiming WCAG conformance from an automated scan alone.
- Streaming chat output with no live region, trapping keyboard focus.
- Stating Quebec legal requirements as settled fact without Legal.
- Dropping accents when normalizing text for matching.

## Related docs
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md), [19-rag-and-retrieval.md](./19-rag-and-retrieval.md)
- [17-api-and-contracts.md](./17-api-and-contracts.md), [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)
- [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md), [12-governance-and-compliance.md](./12-governance-and-compliance.md)
