# README claim audit

Audit of the README against the code, done by reading the repository, the three PDFs, and probing the deployed site. Statuses are from reading code, not from running the services. Written before the cleanup on this branch, so it describes the state of `main` at that point.

## Which code path the app runs

`start_all.py` and the web app run the gateway path: `apps/gateway/routers/orchestrator.py` calls `services/client_agent.run`. The LangGraph graph (`apps/orchestrator/graph.py`) is reached only through `batch_audit.py` and `apps/orchestrator/server.py`, neither of which `start_all.py` starts.

The gateway path also contains simulated parts: RAG evidence is hard-coded text (`orchestrator.py:41-171`), several verdicts are keyed by patient ID (`client_agent.py:802-896`, `1039-1058`, `938`), and arbitration confidence is fixed at 0.95/0.90 (`client_agent.py:1075`).

## Claims

| README claim | Where in code | Status |
|:---|:---|:---|
| SHA-256 hash-chained audit trail | No `hashlib` anywhere. `nodes/audit.py` entry has no hash. `packages/mcp-audit` was only a `pyproject.toml`. | Not implemented |
| Hash shown in the graph UI | `orchestration-graph.tsx:1307` literal, SHA-256 of `"Hello World!"` | Placeholder |
| "Tamper-evident" / "immutable" wording | `report_generator.py:3,313`, `audit.py:8`, `orchestration-graph.tsx:1296-1301` | Overclaim |
| Override accountability: every Accept/Reject/Modify stored with the recommendation | `orchestrator.py:516-551` -> `supabase_reports.py:86-140` | Implemented (plain list append, no integrity check) |
| Barred subjects in a permanent lockout registry | Lockout is UI/run state only (`decision-gateway.tsx:2401`) | Not implemented |
| Trial leadership can see who accepted/overrode and how often | No aggregation code; `reviewer_id` hard-coded to `PRINCIPAL_INVESTIGATOR` | Not implemented |
| 3 context-isolated agents over A2A JSON-RPC 2.0, parallel | `client_agent.py:623-646`, isolation at `gateway/a2a_server.py:116,123`, servers `apps/agent-*/server.py` | Implemented. Method is `SendMessage`; routes are `/` and `/rpc` |
| `A2A_*_URL=...:800x/a2a` in the `.env` example | `client_agent.py:98-100` appends `/rpc`, so the example 404s and falls back to in-process (`:157-163`) | Wrong |
| LangGraph state machine, HITL interrupt, Modify loop | `graph.py`, `hitl.py` | Implemented, not wired to the live app |
| Guardrails run before any LLM call and bypass specialists | Correct in `graph.py` order. Gateway dispatches specialists (`client_agent.py:623`) before guardrails (`:679-681`) and overwrites results | Partly |
| Guardrail-1 retry budget 3, `EXCLUDED_MAX_ITERS` | `client_agent.py:224-280`; `MAX_REFINEMENT_ITERATIONS` env var not read | Implemented |
| Guardrail-2: eGFR < 15, ANC < 500, bilirubin > 5xULN, hemorrhage | `client_agent.py:282-378`: bilirubin is `> 4.0 mg/dL`; no hemorrhage check | Partly |
| Reducer with weighted confidence, `REQUIRES_HITL` | `gateway/a2a_server.py:143-165` plain rule, enum is `NEEDS_REVIEW` | Partly |
| Financial agent reads a structured cost sheet | `agent-financial/server.py:77-82` hard-coded dict; LLM only writes status/explanation | Partly |
| Compliance agent retrieves protocol clauses from Chroma by Trial ID | Chroma code in `services/rag_service/src/rag/`, used only by `rag_node.py`; gateway uses hard-coded evidence; `vector_db/` gitignored | Partly |
| FastMCP tool servers for EHR and RAG | EHR: `mcp_ehr/server.py` (bypassed by direct imports). RAG: `packages/mcp-rag` empty; RAG is a FastAPI app | EHR implemented but bypassed; RAG-as-MCP not implemented |
| Free-text note extraction, typo correction, conversational filter, 1-click fix | `gateway/routers/extraction.py:207`, `web/app/actions.ts:627,731-940` | Implemented ("fuzzy" is a synonym list; LLM call has a 1.2s timeout and rule fallback) |
| Bidirectional FHIR sync | `actions.ts:974-1140` writes local JSON and `patients.prescribed_action`, errors swallowed | Partly (no FHIR server) |
| Supabase `patients` table and `adjudication_reports` jsonb | `actions.ts:8-26`, `supabase_reports.py`; migration only `ALTER`s; no `CREATE TABLE patients`; gateway reads patients from local JSON | Partly |
| LangGraph Postgres checkpointer with local fallback | `apps/orchestrator/checkpointer.py` | Implemented; used only by the LangGraph path; untested against a real DB |
| LLMs: Gemini / OpenAI / Groq with fallback | No Gemini code. Specialists use an OpenAI-compatible endpoint defaulting to the hackathon proxy (`llm_client.py:19-26`). Groq only in `orchestrator/gateway.py`. No fallback chain | Not implemented as stated |
| Next.js 16, React 19, ReactFlow v12, SSE | `apps/web/package.json`, `orchestrator.py:380-405` | Implemented |
| 17 synthetic patients | Seed script adds 17 (P038-P054); `patients_expanded.json` holds 53, plus P033 injected in `patient_service.py`; `batch_audit.py` iterates 49 | Wrong counts |
| Batch audit sample output | `batch_audit.py` | Unverified at audit time |
| Clone URL, `.env.example` | Placeholder URL; `.env.example` not in repo | Broken |
| Repo tree notes | `mcp-audit` "(hash chain)" was empty; `shared-schemas` has no TypeScript | Wrong |
| `graph.mmd` | Stale topology | Stale |
| Deployed app | Site 200, forwards to a Render backend (`/health` and `/api/patients` 200) | Up; not tested end to end |
| Seven practitioners interviewed | `User_Research.pdf` names seven, but its text says "four"; the project report lists five; screenshots show three conversations; exchanges were written, not live | Number supported, wording not |
| References [1], [3] | README credits [1] to van der Sijs; market PDF cites Poly et al. 2020. [3] differs from the market PDF (Getz et al. 2022) | Fix |
| References [4], [6] | Not in any repo document | Unverified |

## Other notes

- `TrialGuard_Project_Report.pdf` contains unmeasured figures (>=95% catch rate, >80% workload reduction, "Cryptographic / Immutable trail").
- `patient_service.py` contained an absolute path from a teammate's machine.
- 14 `sys.path` insertions across the repo.
- No secrets are committed.
