"""Baseline retrieval evaluation for the CURRENT dense-only retrieval.

Run from services/rag_service:

    python -m eval.eval_retrieval

Needs the local Chroma index (gitignored). Build it first with:

    python -m scripts.build_embeddings

What it does
------------
For every labelled query in eval/queries.jsonl it retrieves the top 10 chunks
from the ``trialguard_trials`` collection in two modes and scores them against
the gold chunk ids:

* filtered:   a Chroma query with ``where={"trial_id": ...}``, the same query
              ``Retriever.retrieve_trial`` makes (src/rag/retriever.py), issued
              directly on the collection so no app code is touched.
* unfiltered: the same embedder and collection, but no trial filter, so all
              40 chunks of all 4 trials compete.

Metrics: recall@1, recall@3, recall@5 and MRR (reciprocal rank of the first
gold chunk within the top 10), overall and per trial. No LLM, no network
(after the embedding model is cached), no randomness.
"""

from __future__ import annotations

import argparse
import inspect
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent

KS = (1, 3, 5)
MAX_K = 10
MODES = ("filtered", "unfiltered")


def _fail(message: str) -> None:
    print(f"\nERROR: {message}\n", file=sys.stderr)
    sys.exit(2)


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def load_queries(path: Path) -> list[dict]:
    if not path.exists():
        _fail(f"Query file not found: {path}")
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        _fail(f"No queries in {path}")
    return rows


def score_query(ranked_ids: list[str], gold: list[str]) -> dict:
    gold_set = set(gold)
    result = {}
    for k in KS:
        hits = len(gold_set.intersection(ranked_ids[:k]))
        result[f"recall@{k}"] = hits / len(gold_set)
    first_rank = None
    for rank, chunk_id in enumerate(ranked_ids[:MAX_K], start=1):
        if chunk_id in gold_set:
            first_rank = rank
            break
    result["mrr"] = 1.0 / first_rank if first_rank else 0.0
    result["first_gold_rank"] = first_rank
    return result


def summarize(per_query: list[dict]) -> dict:
    n = len(per_query)
    summary = {"queries": n}
    for key in [f"recall@{k}" for k in KS] + ["mrr"]:
        summary[key] = sum(q[key] for q in per_query) / n if n else None
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--queries", type=Path, default=EVAL_DIR / "queries.jsonl")
    parser.add_argument("--out-dir", type=Path, default=EVAL_DIR / "results")
    args = parser.parse_args()

    # Imports are here so --help works without the heavy dependencies.
    import chromadb
    import sentence_transformers

    from src.rag.embeddings import EmbeddingService
    from src.rag.vector_store import DEFAULT_DB_PATH, VectorStore

    if not Path(DEFAULT_DB_PATH).exists():
        _fail(
            f"No Chroma index at {DEFAULT_DB_PATH}.\n"
            "Build it first:  python -m scripts.build_embeddings"
        )

    queries = load_queries(args.queries)

    model_name = inspect.signature(EmbeddingService.__init__).parameters["model_name"].default
    embedder = EmbeddingService(model_name)
    store = VectorStore(embedder)
    collection = store.trials

    total_chunks = collection.count()
    if total_chunks == 0:
        _fail(
            "The Chroma collection 'trialguard_trials' is empty (count = 0).\n"
            "Build it first:  python -m scripts.build_embeddings"
        )

    indexed = collection.get(include=["metadatas"])
    chunks_per_trial = Counter(m["trial_id"] for m in indexed["metadatas"])
    indexed_ids = set(indexed["ids"])
    trial_of_chunk = {i: m["trial_id"] for i, m in zip(indexed["ids"], indexed["metadatas"])}

    missing = sorted({g for q in queries for g in q["gold_chunk_ids"]} - indexed_ids)
    if missing:
        _fail(
            "Gold chunk ids not found in the index (index out of sync with "
            f"queries?): {missing}\nRebuild with: python -m scripts.build_embeddings"
        )

    for q in queries:
        if q["trial_id"] not in chunks_per_trial:
            _fail(f"Query {q['id']} uses trial {q['trial_id']} which is not in the index.")
        for g in q["gold_chunk_ids"]:
            if trial_of_chunk[g] != q["trial_id"]:
                _fail(f"Query {q['id']}: gold chunk {g} belongs to {trial_of_chunk[g]}, not {q['trial_id']}.")

    commit = _git("rev-parse", "HEAD")
    dirty = "yes" if _git("status", "--porcelain", "--untracked-files=no") not in ("", "unknown") else "no"
    reviewed = sum(1 for q in queries if q.get("reviewed") is True)

    print("=" * 70)
    print("TrialGuard retrieval eval (dense-only baseline)")
    print("=" * 70)
    print(f"Embedding model : {model_name}")
    print(f"Retrieved k     : {MAX_K} (metrics at k = {', '.join(map(str, KS))}, MRR over top {MAX_K})")
    print(f"Queries         : {len(queries)} (labels reviewed: {reviewed} of {len(queries)})")
    print(f"Indexed chunks  : {total_chunks} across {len(chunks_per_trial)} trials")
    print(f"Git commit      : {commit} (tracked files modified: {dirty})")

    per_query_results = []
    for q in queries:
        query_text = q["query"]
        trial_id = q["trial_id"]
        gold = q["gold_chunk_ids"]

        query_embedding = embedder.embed_query(query_text)

        filtered_raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=MAX_K,
            where={"trial_id": trial_id},
        )
        filtered_ids = list(filtered_raw["ids"][0])

        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=MAX_K,
        )
        unfiltered_ids = list(raw["ids"][0])

        per_query_results.append(
            {
                "id": q["id"],
                "trial_id": trial_id,
                "source": q.get("source"),
                "reviewed": q.get("reviewed"),
                "gold_chunk_ids": gold,
                "filtered": {"ranked_ids": filtered_ids, **score_query(filtered_ids, gold)},
                "unfiltered": {"ranked_ids": unfiltered_ids, **score_query(unfiltered_ids, gold)},
            }
        )

    results = {}
    for mode in MODES:
        mode_rows = [dict(r[mode], trial_id=r["trial_id"]) for r in per_query_results]
        by_trial = defaultdict(list)
        for row in mode_rows:
            by_trial[row["trial_id"]].append(row)
        results[mode] = {
            "overall": summarize(mode_rows),
            "per_trial": {
                trial: dict(summarize(rows), chunks_in_trial=chunks_per_trial[trial])
                for trial, rows in sorted(by_trial.items())
            },
        }

    report = {
        "description": (
            "Baseline of the current dense-only retrieval (no BM25, no rerank, "
            "no tuning). Gold labels in queries.jsonl may be unreviewed."
        ),
        "model": model_name,
        "chromadb_version": chromadb.__version__,
        "sentence_transformers_version": sentence_transformers.__version__,
        "collection": "trialguard_trials",
        "distance": "cosine",
        "retrieved_k": MAX_K,
        "ks": list(KS),
        "queries_file": args.queries.name,
        "num_queries": len(queries),
        "labels_reviewed": reviewed,
        "indexed_chunks": total_chunks,
        "chunks_per_trial": dict(sorted(chunks_per_trial.items())),
        "git_commit": commit,
        "git_tracked_files_modified": dirty,
        "results": results,
        "per_query": per_query_results,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "baseline.json"
    md_path = args.out_dir / "baseline.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print()
    print(md_path.read_text(encoding="utf-8"))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def _fmt(value, trivial: bool = False) -> str:
    if value is None:
        return "n/a"
    text = f"{value:.3f}"
    return text + " †" if trivial else text


def render_markdown(report: dict) -> str:
    n = report["num_queries"]
    lines = [
        "# Retrieval baseline (dense-only)",
        "",
        f"- Embedding model: `{report['model']}` (cosine, Chroma `{report['chromadb_version']}`, sentence-transformers `{report['sentence_transformers_version']}`)",
        f"- Collection: `{report['collection']}` ({report['indexed_chunks']} chunks, {len(report['chunks_per_trial'])} trials)",
        f"- Queries: {n} from `eval/queries.jsonl`; top {report['retrieved_k']} retrieved per query",
        f"- Labels reviewed: {report['labels_reviewed']} of {n}",
        f"- Git commit: `{report['git_commit']}` (tracked files modified: {report['git_tracked_files_modified']})",
        "- Retrieval under test: current dense-only search. No BM25, no reranking, no score threshold, no tuning.",
        "",
        "recall@k is the share of a query's gold chunks found in the top k; MRR is the mean reciprocal rank of the first gold chunk in the top 10 (0 if absent).",
        "",
        "† Filtered mode only: the trial has k or fewer chunks, so the filtered search returns every chunk of that trial and the value is 1.000 for any labelled query regardless of embedding quality. For example recall@5 is trivially 1.000 for any trial with 5 or fewer chunks. The overall filtered row mixes trivial and non-trivial entries.",
        "",
    ]
    for mode in MODES:
        title = "Filtered by trial_id (as the pipeline does)" if mode == "filtered" else "Unfiltered (all chunks of all trials compete)"
        lines += [f"## {title}", "", "| Scope | Queries | Chunks in trial | recall@1 | recall@3 | recall@5 | MRR |", "|:---|---:|---:|---:|---:|---:|---:|"]
        overall = report["results"][mode]["overall"]
        lines.append(
            f"| **Overall** | {overall['queries']} | {report['indexed_chunks']} (all) | "
            f"{_fmt(overall['recall@1'])} | {_fmt(overall['recall@3'])} | {_fmt(overall['recall@5'])} | {_fmt(overall['mrr'])} |"
        )
        for trial, s in report["results"][mode]["per_trial"].items():
            cells = []
            for k in (1, 3, 5):
                trivial = mode == "filtered" and s["chunks_in_trial"] <= k
                cells.append(_fmt(s[f"recall@{k}"], trivial))
            lines.append(
                f"| {trial} | {s['queries']} | {s['chunks_in_trial']} | {cells[0]} | {cells[1]} | {cells[2]} | {_fmt(s['mrr'])} |"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
