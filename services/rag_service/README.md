# rag_service

Protocol retrieval and rule-engine code for TrialGuard: chunking, embeddings, a Chroma vector store, dense retrieval filtered by trial, a deterministic rule engine, and a FastAPI app (`src/api/main.py`, endpoints `/health`, `/evaluate`, `/mock-fhir/patients/{id}`).

**Status:** this is a built component. It is called in-process from the LangGraph node (`apps/orchestrator/nodes/rag_node.py`) and by its own FastAPI app. The deployed gateway and web demo (`start_all.py`) do not use it; they show fixed protocol clauses. See the "RAG status" section of the root README.

## Corpus

4 trials (`NCT02415400`, `NCT00781573`, `NCT00699998`, `NCT00809965`), 40 eligibility chunks, committed at `data/processed/chunks/trial_chunks.jsonl`. Only the eligibility section is chunked. The raw input files (`data/raw/`) are not in the repo, so the ingestion step (`scripts/ingest_data.py`) cannot be re-run. The FDA label collection (`trialguard_fda_labels`) is created empty: its raw data and chunk file are not in the repo, so FDA retrieval cannot be built from what is committed.

## Build the trial index

From `services/rag_service`, using the environment created by `uv sync` at the repo root:

```bash
cd services/rag_service
python -m scripts.build_embeddings    # or: uv run python -m scripts.build_embeddings
```

This embeds the 40 chunks and writes them to the `trialguard_trials` Chroma collection. Check what is in the index with `python -m scripts.list_chroma_trials`.

## Model

Embeddings use `BAAI/bge-small-en-v1.5` via `sentence-transformers` (set in `src/rag/embeddings.py`). The weights are downloaded from Hugging Face the first time the model is loaded and are cached outside the repo. No model files are stored here. The `config.yaml` file lists the same model name, but no code reads it.

## Where the index lives

`services/rag_service/vector_db/chroma/` (a Chroma `PersistentClient`, collections `trialguard_trials` and `trialguard_fda_labels`, cosine distance). The directory is gitignored and is never committed. If it is missing or empty, retrieval returns no results; rebuild it with the command above.

## Tests

```bash
cd services/rag_service
uv run pytest
```

These tests cover the rule engine and API contracts (decisions and response keys). They do not measure retrieval quality.

## Design choices

What the code does, and the tradeoffs that come with it. These are descriptions of the code, not measured claims.

| Choice | Where | Tradeoff |
|:---|:---|:---|
| `BAAI/bge-small-en-v1.5` embeddings (384 dimensions), normalized | `src/rag/embeddings.py` | Small, free and runs locally with no API. It is a general-domain model, not a biomedical one. The BGE-recommended query instruction prefix is not used, and its effect has not been measured here. |
| Chroma `PersistentClient`, cosine distance, two collections (trials, FDA labels) | `src/rag/vector_store.py` | Simple and local. The index is not hosted, so only a machine that has built it can retrieve. |
| Hard metadata filter on `trial_id` | `Retriever.retrieve_trial` | Keeps one trial's criteria out of another trial's results. A wrong `trial_id` returns the wrong trial's text without an error. See the filtered and unfiltered rows in the baseline. |
| Dense retrieval only; k=6 for trials and k=4 for FDA (k=4 and k=3 in the LangGraph node) | `src/rag/retriever.py`, `apps/orchestrator/nodes/rag_node.py` | No BM25, reranking or score threshold. `config.yaml` also lists k values, but no code reads it. |
| Query built from the patient's diagnoses, medications and failing rule parameters | `src/rag/query_builder.py` | Long patient-specific queries may drift from the criterion text. |
| Regex chunking of the eligibility section only | `src/preprocessing/chunker.py` | Short chunks of one criterion each. Some chunks are not criteria (for example a website footer in `NCT02415400-eligibility-000`), and dosing text is not indexed. |

With 4 trials and 40 chunks, k is larger than the chunk count of several trials, so recall there is partly trivial. See [`eval/README.md`](eval/README.md) for how the baseline marks those cells.

