import json


def load_trials(path: str) -> list[dict]:

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # Format 1:
    # [
    #   {...},
    #   {...}
    # ]

    if isinstance(data, list):
        return data

    # Format 2:
    # {
    #   "studies": [...]
    # }

    if isinstance(data, dict):

        if "studies" in data:
            return data["studies"]

        # Some datasets use "results"
        if "results" in data:
            return data["results"]

        # Single trial JSON
        return [data]

    raise ValueError(
        "Unsupported ClinicalTrials JSON format"
    )