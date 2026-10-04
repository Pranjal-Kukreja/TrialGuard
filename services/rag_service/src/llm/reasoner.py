import json

from src.llm.client import (
    LLMClient
)

from src.llm.prompts import (
    load_prompt
)


class ComplianceReasoner:

    def __init__(self):

        self.client = (
            LLMClient()
        )

        self.system_prompt = (
            load_prompt(
                "compliance.txt"
            )
        )

    def explain(
        self,
        *,
        trial_id,
        patient,
        deterministic_result,
        evidence,
        safety_evidence,
        query
    ):

        payload = {
            "trial_id":
                trial_id,

            "patient":
                patient,

            "deterministic_result":
                deterministic_result,

            "trial_evidence":
                evidence,

            "fda_safety_evidence":
                safety_evidence,

            "query":
                query
        }

        return self.client.generate(
            [
                {
                    "role":
                        "system",

                    "content":
                        self.system_prompt
                },

                {
                    "role":
                        "user",

                    "content":
                        (
                            "Explain the following "
                            "TrialGuard assessment. "
                            "Do not change the "
                            "deterministic decision.\n\n"
                            + json.dumps(
                                payload,
                                indent=2,
                                ensure_ascii=False,
                                default=str
                            )
                        )
                }
            ]
        )