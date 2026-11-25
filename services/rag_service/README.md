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
