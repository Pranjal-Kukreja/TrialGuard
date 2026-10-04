import re

from src.preprocessing.cleaner import clean_text


def split_criteria(text: str) -> list[str]:

    text = clean_text(text)

    if not text:
        return []

    pieces = re.split(
        r"\n+|(?=\d+\.\s)|(?=[•*-]\s)",
        text
    )

    results = []

    for piece in pieces:

        piece = piece.strip(
            " \n\t-*•"
        )

        if len(piece) >= 20:
            results.append(piece)

    return results


def make_trial_chunks(
    trial: dict
) -> list[dict]:

    chunks = []

    criteria = split_criteria(
        trial.get(
            "eligibility_text",
            ""
        )
    )

    for i, text in enumerate(criteria):

        chunks.append({
            "chunk_id":
                (
                    f'{trial["trial_id"]}'
                    f'-eligibility-{i:03d}'
                ),

            "trial_id":
                trial["trial_id"],

            "section":
                "eligibility",

            "source":
                "ClinicalTrials.gov",

            "text":
                text
        })

    return chunks

def make_fda_label_chunks(
    label: dict
) -> list[dict]:

    chunks = []

    document_id = (
        label.get("document_id")
        or label.get("set_id")
    )

    if not document_id:
        return chunks

    drug_names = (
        label.get("generic_names")
        or label.get("brand_names")
        or label.get("substance_names")
        or []
    )

    sections = label.get(
        "sections",
        {}
    )

    for section, values in sections.items():

        if not isinstance(
            values,
            list
        ):

            values = [values]

        for index, value in enumerate(
            values
        ):

            text = clean_text(
                str(value)
            )

            if len(text) < 30:
                continue

            chunk_id = (
                f"FDA-{document_id}-"
                f"{section}-{index:03d}"
            )

            chunks.append({
                "chunk_id":
                    chunk_id,

                "document_id":
                    document_id,

                "trial_id":
                    "",

                "section":
                    section,

                "drug_names":
                    drug_names,

                "source":
                    "openFDA Drug Label",

                "text":
                    text
            })

    return chunks