import json
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)

TARGET = "NCT02415400"


def main():

    if not CHUNKS_FILE.exists():

        print(
            "ERROR: trial_chunks.jsonl "
            "does not exist."
        )

        print(
            "Run:"
        )

        print(
            "python -m scripts.build_kb"
        )

        return

    count = 0

    print(
        f"\nChunks for {TARGET}\n"
    )

    print("=" * 70)

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            chunk = json.loads(
                line
            )

            if (
                chunk.get("trial_id")
                != TARGET
            ):
                continue

            count += 1

            print(
                "\nChunk ID:",
                chunk["chunk_id"]
            )

            print(
                "Section:",
                chunk["section"]
            )

            print(
                "\nTEXT:"
            )

            print(
                chunk["text"]
            )

            print(
                "\n" + "-" * 70
            )

    print(
        f"\nTotal chunks "
        f"for {TARGET}: {count}"
    )


if __name__ == "__main__":
    main()