# Clean code and scope (always loaded)

<!-- Implements AGT-010, AGT-011 (no frontmatter: always loaded). -->

- Comments explain why (a constraint, rule source or trade-off), never what the code does (CLN-027).
- No comments that narrate the edit (`# added`, `# fixed`), author or date; git holds that (CLN-028).
- Give public functions and classes a one-line docstring stating purpose and non-obvious behavior (CLN-030).
- Do not loosen lint, type or complexity config, and do not add `noqa` or per-file ignores, to get green (CLN-032, CLN-033, PRC-023).
- Use only imports, functions and library calls that exist in the pinned dependency versions; check instead of guessing (CLN-037).
- Keep the diff to the task: no drive-by reformatting, renames, new files or dependencies (CLN-038).
- Keep modules under about 400 lines with a single responsibility (CLN-007).
