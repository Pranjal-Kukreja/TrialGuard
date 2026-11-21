# What changed in the post-hackathon cleanup

Summary of the work done on this repository after KADO TechQuest. The README describes the current state of the project; this note records what was changed and how to check it.

## Added

- **Audit hash chain.** `packages/mcp-audit` seals each saved adjudication report with `sha256(prev_hash + canonical_json(report))`, chained per patient, starting from a fixed genesis value. `verify_chain()` recomputes the chain and reports the first broken link.
  - Sealing happens in the gateway's report store, so the local JSON and Supabase paths both carry `hash` and `prev_hash`.
  - `GET /api/reports/{patient_id}/verify` exposes verification.
  - The PDF certificate prints the report hash, the previous hash and the chain status.
  - The graph UI's audit node shows the real chain head and status instead of a fixed value.
  - The LangGraph audit node seals its final entry the same way.
- **Tests.** 19 pytest tests for the chain, the report store and the audit node. Run with `uv run pytest`.
- **`.env.example`**, listing the variables the code reads.

## Changed

- **README** rewritten to match the code: the two execution paths, what is simulated, corrected setup and run instructions, a real patient table, and the audit trail's guarantees and limits.
- **Repo layout.** Utility scripts moved to `scripts/` (run with `python -m scripts.<name>`); generated graph files moved to `docs/`; a stale graph file removed.
- **Imports.** `mcp_ehr` is now a declared dependency and imported normally instead of through `sys.path` edits in most modules.
- **EHR MCP server** start-up fixed for the locked `fastmcp` version.

## How to verify

```bash
uv sync
uv run pytest                                  # 19 tests
uv run python start_all.py                     # then: curl localhost:8000/api/reports/<patient>/verify
```

Known limits of the chain and of the app are listed in the README under "Audit Trail & Regulatory Alignment" and "Limitations & Future Work".
