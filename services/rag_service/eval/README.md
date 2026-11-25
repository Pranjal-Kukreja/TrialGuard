# Retrieval evaluation (baseline)

This folder measures how well the **current dense-only retrieval** finds the right protocol chunk. It is a baseline: no BM25, no reranking, no score threshold, no tuning. Retrieval is `BAAI/bge-small-en-v1.5` embeddings with cosine search in the Chroma collection `trialguard_trials`.

## Run it

```bash
cd services/rag_service
python -m scripts.build_embeddings     # builds the local, gitignored index from the committed 40 chunks
python -m eval.eval_retrieval          # writes eval/results/baseline.json and baseline.md
```

The embedding model must be in the Hugging Face cache (it is downloaded on first use). With `HF_HUB_OFFLINE=1` set and the model cached, the run makes no network calls. It uses no LLM and no API keys, and it is deterministic: two consecutive runs produced byte-identical result files. The script stops with an error if the Chroma collection is empty or a gold chunk id is not in the index.

## What is measured

- **Queries:** `queries.jsonl`, 36 queries over the 4 indexed trials (40 chunks). Each has one gold chunk id. 14 queries (`"source": "rule_mapping"`) take their gold chunk from the `source_chunk_id` that `data/processed/rules/candidate_demo_rules.json` records for a rule, and are written in the style `query_builder.py` produces. The other 22 (`"hand_written"`) are short questions or patient facts whose answer is in one named chunk. `NCT02415400` has no rule-to-chunk mapping, so all 10 of its queries are hand written.
- **Metrics:** recall@1, recall@3, recall@5 and MRR, over the top 10 retrieved chunks, overall and per trial. With one gold chunk per query, recall@k is the share of queries whose gold chunk is in the top k.
- **Two modes:**
  - *Filtered:* a Chroma query with `where={"trial_id": ...}`, the same query `Retriever.retrieve_trial` makes. Only that trial's chunks compete.
  - *Unfiltered:* the same query without the trial filter, so all 40 chunks compete.

## Caveats

- **Labels are not reviewed.** Every query has `"reviewed": false`, so the results are "labels reviewed: 0 of 36". Gold labels may be wrong, and a query may have more than one relevant chunk while only one is labelled (for example a query about PCI within 30 days is labelled with one chunk although a neighbouring chunk about previous PCI is also related). Either can lower the numbers.
- **Tiny corpus.** Trials have 5 to 14 chunks. In filtered mode, if a trial has `k` or fewer chunks, the search returns all of them, so recall@k is 1.000 whatever the embeddings are. Such cells are marked † in `results/baseline.md` (here, recall@5 for the 5-chunk trial `NCT00809965`). The overall filtered row mixes trivial and non-trivial cells.
- **Small sample.** 36 queries, 4 of them for `NCT00809965`. Differences of a few queries move the percentages a lot.
- **Only eligibility chunks** are indexed, so this says nothing about dosing text or the FDA label collection (which cannot be built from the repo).
- **The live demo does not use this retrieval.** The deployed gateway shows fixed protocol clauses; see the RAG status section of the root README.
- `results/baseline.md` records the git commit of the code that produced it; the results were committed afterwards.

## Reviewing the labels

Open `queries.jsonl`, check that the gold chunk answers the query, and set `"reviewed": true` only for lines you checked. Then re-run the script; the "labels reviewed" line is computed from that flag.
