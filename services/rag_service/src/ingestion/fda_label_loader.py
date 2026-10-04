from src.ingestion.file_reader import (
    load_json_file
)


IMPORTANT_SECTIONS = [
    "boxed_warning",
    "contraindications",
    "warnings",
    "drug_interactions",
    "adverse_reactions",
    "dosage_and_administration",
    "pediatric_use",
    "geriatric_use",
    "pregnancy",
    "nursing_mothers"
]


def load_fda_labels(path):

    data = load_json_file(path)

    results = data.get(
        "results",
        []
    )

    for record in results:

        openfda = record.get(
            "openfda",
            {}
        )

        sections = {}

        for name in IMPORTANT_SECTIONS:

            value = record.get(name)

            if value:
                sections[name] = value

        yield {
            "document_id":
                record.get("id"),

            "set_id":
                record.get("set_id"),

            "effective_time":
                record.get(
                    "effective_time"
                ),

            "brand_names":
                openfda.get(
                    "brand_name",
                    []
                ),

            "generic_names":
                openfda.get(
                    "generic_name",
                    []
                ),

            "substance_names":
                openfda.get(
                    "substance_name",
                    []
                ),

            "sections":
                sections,

            "source":
                "openFDA Drug Label"
        }