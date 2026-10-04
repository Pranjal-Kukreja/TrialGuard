import json
from pathlib import Path

from src.rag.embeddings import (
    EmbeddingService
)

from src.rag.vector_store import (
    VectorStore
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


TRIAL_CHUNKS = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)


FDA_CHUNKS = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "fda_label_chunks.jsonl"
)


def index_jsonl(
    path: Path,
    callback,
    batch_size=64
):

    if not path.exists():

        print(
            f"Skipping missing file: "
            f"{path}"
        )

        return 0

    total = 0
    batch = []

    with path.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            batch.append(
                json.loads(line)
            )

            if (
                len(batch)
                >= batch_size
            ):

                callback(batch)

                total += len(batch)

                print(
                    f"Indexed {total} chunks"
                )

                batch.clear()

        if batch:

            callback(batch)

            total += len(batch)

            print(
                f"Indexed {total} chunks"
            )

    return total


def main():

    print("=" * 70)
    print("TrialGuard AI - Building Vector Database")
    print("=" * 70)

    embedder = EmbeddingService()

    store = VectorStore(
        embedder
    )

    print("\nIndexing ClinicalTrials chunks...")

    trial_total = index_jsonl(
        TRIAL_CHUNKS,
        store.add_trial_chunks,
        batch_size=64
    )

    print(
        f"ClinicalTrials indexed: "
        f"{trial_total}"
    )

    print("\nIndexing FDA label chunks...")

    fda_total = index_jsonl(
        FDA_CHUNKS,
        store.add_fda_chunks,
        batch_size=32
    )

    print(
        f"FDA chunks indexed: "
        f"{fda_total}"
    )

    print("\n" + "=" * 70)
    print("VECTOR DATABASE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()