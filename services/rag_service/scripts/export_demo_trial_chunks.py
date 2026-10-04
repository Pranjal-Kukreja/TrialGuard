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


OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "documents"
    / "demo_trials"
)


TRIAL_IDS = [
    "NCT00699998",
    "NCT02415400",
    "NCT00781573",
    "NCT00809965"
]


def main():

    if not CHUNKS_FILE.exists():

        raise FileNotFoundError(
            f"Chunks not found:\n"
            f"{CHUNKS_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    grouped = {
        trial_id: []
        for trial_id
        in TRIAL_IDS
    }

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if not line.strip():
                continue

            chunk = json.loads(
                line
            )

            trial_id = (
                chunk.get(
                    "trial_id"
                )
            )

            if trial_id in grouped:

                grouped[
                    trial_id
                ].append(
                    chunk
                )

    print("=" * 70)
    print("EXPORTING DEMO TRIAL RAG CHUNKS")
    print("=" * 70)

    for trial_id, chunks in (
        grouped.items()
    ):

        output_file = (
            OUTPUT_DIR
            / f"{trial_id}_chunks.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chunks,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(
            f"{trial_id}: "
            f"{len(chunks)} chunks"
        )

        print(
            f"    -> {output_file}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()