from src.rag.retriever import (
    Retriever
)


TRIAL_ID = "NCT02415400"


def main():

    print(
        "Loading retriever..."
    )

    retriever = Retriever()

    query = (
        "eligibility exclusion criteria "
        "laboratory liver ALT AST renal "
        "function bleeding medications"
    )

    print(
        f"\nTrial: {TRIAL_ID}"
    )

    print(
        f"Query: {query}"
    )

    results = (
        retriever.retrieve_trial(
            query=query,
            trial_id=TRIAL_ID,
            k=5
        )
    )

    print(
        f"\nResults: "
        f"{len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "=" * 70)

        print(
            f"RESULT {index}"
        )

        print(
            "Chunk:",
            result["chunk_id"]
        )

        print(
            "Trial:",
            result[
                "metadata"
            ].get(
                "trial_id"
            )
        )

        print(
            "Distance:",
            result["distance"]
        )

        print(
            "\nText:\n"
        )

        print(
            result["text"]
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()