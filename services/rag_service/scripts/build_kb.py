import json
from pathlib import Path

from src.preprocessing.chunker import make_trial_chunks




PROJECT_ROOT = Path(__file__).resolve().parents[1]


TRIAL_INPUT = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "cleaned"
    / "trials.jsonl"
)


TRIAL_CHUNKS = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================

def main():

    print("=" * 60)
    print("TrialGuard AI - Building Trial Knowledge Base")
    print("=" * 60)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Input        : {TRIAL_INPUT}")
    print(f"Output       : {TRIAL_CHUNKS}")

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not TRIAL_INPUT.exists():

        raise FileNotFoundError(
            "\nNormalized clinical-trial dataset was not found.\n"
            f"Expected:\n{TRIAL_INPUT}\n\n"
            "Run ingestion first:\n"
            "python -m scripts.ingest_data"
        )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    TRIAL_CHUNKS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_trials = 0
    total_chunks = 0
    trials_without_chunks = 0

    # --------------------------------------------------------
    # Process normalized trials
    # --------------------------------------------------------

    with TRIAL_INPUT.open(
        "r",
        encoding="utf-8"
    ) as source, TRIAL_CHUNKS.open(
        "w",
        encoding="utf-8"
    ) as output:

        for line in source:

            line = line.strip()

            if not line:
                continue

            trial = json.loads(line)

            total_trials += 1

            chunks = make_trial_chunks(
                trial
            )

            if not chunks:
                trials_without_chunks += 1

            for chunk in chunks:

                output.write(
                    json.dumps(
                        chunk,
                        ensure_ascii=False
                    )
                    + "\n"
                )

                total_chunks += 1

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("KNOWLEDGE BASE BUILD COMPLETE")
    print("=" * 60)

    print(
        f"Trials processed       : {total_trials}"
    )

    print(
        f"Trial chunks created   : {total_chunks}"
    )

    print(
        f"Trials without chunks  : {trials_without_chunks}"
    )

    print(
        f"\nSaved to:\n{TRIAL_CHUNKS}"
    )


if __name__ == "__main__":
    main()