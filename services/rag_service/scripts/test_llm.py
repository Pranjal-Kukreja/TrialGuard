from src.llm.client import (
    LLMClient
)


def main():

    try:
        client = LLMClient()

    except RuntimeError as error:
        print(
            "LLM is not configured: "
            f"{error}"
        )
        return

    result = client.generate(
        [
            {
                "role":
                    "system",

                "content":
                    (
                        "Return exactly "
                        "CONNECTION_OK."
                    )
            },

            {
                "role":
                    "user",

                "content":
                    "Connection test."
            }
        ]
    )

    print(result)


if __name__ == "__main__":
    main()