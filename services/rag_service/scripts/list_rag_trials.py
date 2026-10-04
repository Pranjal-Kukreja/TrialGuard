import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)


def main():

    if not CHUNKS_FILE.exists():
        print("trial_chunks.jsonl not found.")
        print("Run:")
        print("python -m scripts.build_kb")
        return

    counts = Counter()

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if not line.strip():
                continue

            chunk = json.loads(line)

            trial_id = chunk.get(
                "trial_id"
            )

            if trial_id:
                counts[trial_id] += 1

    print("=" * 60)
    print("TRIALS AVAILABLE FOR RAG")
    print("=" * 60)

    print(
        f"Unique trials: {len(counts)}"
    )

    print("\nTop trials by chunk count:\n")

    for trial_id, count in (
        counts.most_common(30)
    ):
        print(
            f"{trial_id:15} "
            f"{count} chunks"
        )


if __name__ == "__main__":
    main()