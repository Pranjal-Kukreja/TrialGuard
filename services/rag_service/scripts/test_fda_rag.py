from src.rag.retriever import (
    Retriever
)


def main():

    retriever = Retriever()

    query = (
        "aspirin clopidogrel apixaban "
        "bleeding contraindications "
        "drug interactions warnings"
    )

    results = (
        retriever.retrieve_fda(
            query=query,
            k=5
        )
    )

    print("=" * 70)
    print("FDA RAG TEST")
    print("=" * 70)

    print(
        "Results:",
        len(results)
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"RESULT {index}"
        )

        print(
            "Chunk:",
            result.get(
                "chunk_id"
            )
        )

        print(
            "Metadata:",
            result.get(
                "metadata"
            )
        )

        print(
            "Distance:",
            result.get(
                "distance"
            )
        )

        print("\nText:")

        print(
            result.get(
                "text",
                ""
            )[:1000]
        )


if __name__ == "__main__":
    main()