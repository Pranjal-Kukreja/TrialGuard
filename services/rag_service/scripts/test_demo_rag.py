from src.rag.retriever import (
    Retriever
)


TESTS = [
    (
        "NCT02415400",
        (
            "eligibility atrial "
            "fibrillation renal bleeding "
            "anticoagulation"
        )
    ),

    (
        "NCT00699998",
        (
            "eligibility NSTEMI "
            "medical management PCI CABG"
        )
    ),

    (
        "NCT00781573",
        (
            "eligibility DES aspirin "
            "clopidogrel platelets warfarin"
        )
    ),

    (
        "NCT00809965",
        (
            "eligibility ACS antiplatelet "
            "anticoagulation bleeding"
        )
    )
]


def main():

    retriever = Retriever()

    for (
        trial_id,
        query
    ) in TESTS:

        print(
            "\n" + "=" * 70
        )

        print(
            "TRIAL:",
            trial_id
        )

        print(
            "QUERY:",
            query
        )

        results = (
            retriever.retrieve_trial(
                query=query,
                trial_id=trial_id,
                k=4
            )
        )

        print(
            "RESULTS:",
            len(results)
        )

        for result in results:

            metadata = (
                result[
                    "metadata"
                ]
            )

            returned_trial = (
                metadata.get(
                    "trial_id"
                )
            )

            print(
                "\nChunk:",
                result[
                    "chunk_id"
                ]
            )

            print(
                "Trial:",
                returned_trial
            )

            print(
                "Distance:",
                result.get(
                    "distance"
                )
            )

            print(
                result["text"][:500]
            )

            assert (
                returned_trial
                == trial_id
            ), (
                "RAG LEAK: "
                f"requested {trial_id}, "
                f"received "
                f"{returned_trial}"
            )


if __name__ == "__main__":
    main()