from collections import Counter
from pathlib import Path

import chromadb


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "vector_db"
    / "chroma"
)


def main():

    print("=" * 60)
    print("TRIALS ACTUALLY PRESENT IN CHROMA")
    print("=" * 60)

    if not CHROMA_PATH.exists():
        print(
            "\nChroma database does not exist."
        )
        return

    client = (
        chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )
    )

    try:
        collection = (
            client.get_collection(
                "trialguard_trials"
            )
        )

    except Exception as error:
        print(
            "\nCould not open "
            "trialguard_trials:"
        )
        print(error)
        return

    print(
        "\nTotal embedded chunks:",
        collection.count()
    )

    # We only need metadata.
    result = collection.get(
        include=[
            "metadatas"
        ]
    )

    counts = Counter()

    for metadata in (
        result.get(
            "metadatas",
            []
        )
    ):

        if not metadata:
            continue

        trial_id = (
            metadata.get(
                "trial_id"
            )
        )

        if trial_id:
            counts[
                trial_id
            ] += 1

    print(
        "\nUnique embedded trials:",
        len(counts)
    )

    print(
        "\nAvailable trial IDs:\n"
    )

    for trial_id, count in (
        counts.most_common(50)
    ):

        print(
            f"{trial_id:15} "
            f"{count} embedded chunks"
        )


if __name__ == "__main__":
    main()