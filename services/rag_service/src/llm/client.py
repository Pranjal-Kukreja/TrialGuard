import os
from pathlib import Path

from dotenv import (
    load_dotenv
)

from openai import (
    OpenAI
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

load_dotenv(
    PROJECT_ROOT
    / ".env"
)


def is_llm_configured() -> bool:
    use_llm = (
        os.getenv(
            "USE_LLM",
            "false"
        )
        .strip()
        .lower()
        == "true"
    )

    return (
        use_llm
        and bool(os.getenv("LLM_API_KEY"))
        and bool(os.getenv("LLM_BASE_URL"))
        and bool(os.getenv("LLM_MODEL"))
    )


class LLMClient:

    def __init__(self):

        base_url = os.getenv(
            "LLM_BASE_URL"
        )

        api_key = os.getenv(
            "LLM_API_KEY"
        )

        model = os.getenv(
            "LLM_MODEL"
        )

        timeout_seconds = os.getenv(
            "LLM_TIMEOUT_SECONDS",
            "60"
        )

        try:
            timeout = float(
                timeout_seconds
            )

        except ValueError as error:
            raise RuntimeError(
                "LLM_TIMEOUT_SECONDS must be numeric."
            ) from error

        if not base_url:
            raise RuntimeError(
                "LLM_BASE_URL missing. Create a local .env "
                "from .env.example."
            )

        if (
            not api_key
            or api_key == "replace-with-a-new-kado-key"
        ):
            raise RuntimeError(
                "LLM_API_KEY missing or still a placeholder. "
                "Add a replacement key to local .env."
            )

        if (
            not model
            or model == "your-model-name"
        ):
            raise RuntimeError(
                "LLM_MODEL missing or still a placeholder. "
                "Set the Kado model name in local .env."
            )

        self.model = model

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )

    def generate(
        self,
        messages
    ):

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,

                messages=messages,

                temperature=0
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:

            raise RuntimeError(
                "Empty LLM response."
            )

        return content