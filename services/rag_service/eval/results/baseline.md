# Retrieval baseline (dense-only)

- Embedding model: `BAAI/bge-small-en-v1.5` (cosine, Chroma `1.5.9`, sentence-transformers `6.0.1`)
- Collection: `trialguard_trials` (40 chunks, 4 trials)
- Queries: 36 from `eval/queries.jsonl`; top 10 retrieved per query
- Labels reviewed: 0 of 36
- Git commit: `7b7a5c75e14e7423f5bc073a7d2f0cebeb516e8b` (tracked files modified: no)
- Retrieval under test: current dense-only search. No BM25, no reranking, no score threshold, no tuning.

recall@k is the share of a query's gold chunks found in the top k; MRR is the mean reciprocal rank of the first gold chunk in the top 10 (0 if absent).

† Filtered mode only: the trial has k or fewer chunks, so the filtered search returns every chunk of that trial and the value is 1.000 for any labelled query regardless of embedding quality. For example recall@5 is trivially 1.000 for any trial with 5 or fewer chunks. The overall filtered row mixes trivial and non-trivial entries.

## Filtered by trial_id (as the pipeline does)

| Scope | Queries | Chunks in trial | recall@1 | recall@3 | recall@5 | MRR |
|:---|---:|---:|---:|---:|---:|---:|
| **Overall** | 36 | 40 (all) | 0.778 | 0.889 | 0.972 | 0.853 |
| NCT00699998 | 13 | 14 | 0.692 | 0.846 | 1.000 | 0.804 |
| NCT00781573 | 9 | 10 | 0.556 | 0.778 | 0.889 | 0.694 |
| NCT00809965 | 4 | 5 | 1.000 | 1.000 | 1.000 † | 1.000 |
| NCT02415400 | 10 | 11 | 1.000 | 1.000 | 1.000 | 1.000 |

## Unfiltered (all chunks of all trials compete)

| Scope | Queries | Chunks in trial | recall@1 | recall@3 | recall@5 | MRR |
|:---|---:|---:|---:|---:|---:|---:|
| **Overall** | 36 | 40 (all) | 0.694 | 0.833 | 0.861 | 0.770 |
| NCT00699998 | 13 | 14 | 0.615 | 0.769 | 0.769 | 0.692 |
| NCT00781573 | 9 | 10 | 0.556 | 0.778 | 0.778 | 0.664 |
| NCT00809965 | 4 | 5 | 0.750 | 0.750 | 1.000 | 0.812 |
| NCT02415400 | 10 | 11 | 0.900 | 1.000 | 1.000 | 0.950 |
