import re
from typing import Any


LAB_NAMES = {
    "ALT": ["ALT", "alanine aminotransferase"],
    "AST": ["AST", "aspartate aminotransferase"],
    "eGFR": [
        "eGFR",
        "estimated glomerular filtration rate"
    ],
}


def make_rule(
    trial_id: str,
    chunk_id: str,
    rule_type: str,
    parameter: str,
    operator: str,
    threshold: Any,
    unit: str | None,
    action: str,
    evidence_text: str,
    index: int
) -> dict:

    parameter_id = (
        parameter.upper()
        .replace(" ", "_")
        .replace("/", "_")
    )

    return {
        "rule_id":
            f"{trial_id}-{parameter_id}-{index:03d}",

        "trial_id":
            trial_id,

        "rule_type":
            rule_type,

        "parameter":
            parameter,

        "operator":
            operator,

        "threshold":
            threshold,

        "unit":
            unit,

        "action":
            action,

        "source_chunk_id":
            chunk_id,

        "evidence_text":
            evidence_text
    }


def determine_action(text: str) -> str:

    value = text.lower()

    exclusion_words = [
        "exclude",
        "excluded",
        "exclusion",
        "not eligible",
        "ineligible",
        "must not",
        "cannot participate"
    ]

    if any(
        word in value
        for word in exclusion_words
    ):
        return "EXCLUDE"

    return "EXCLUDE"


def extract_age_rules(
    trial_id: str,
    chunk_id: str,
    text: str,
    start_index: int
):

    rules = []

    lower = text.lower()

    # --------------------------------------------------
    # "18 years or older"
    # "at least 18 years"
    # "minimum age of 18 years"
    #
    # Failure condition:
    # age < 18 -> EXCLUDE
    # --------------------------------------------------

    min_patterns = [
        r"(\d+)\s*years?\s*(?:of age\s*)?or older",
        r"at least\s+(\d+)\s*years?",
        r"minimum age(?: of)?\s+(\d+)\s*years?"
    ]

    for pattern in min_patterns:

        match = re.search(
            pattern,
            lower
        )

        if match:

            threshold = int(
                match.group(1)
            )

            rules.append(
                make_rule(
                    trial_id=trial_id,
                    chunk_id=chunk_id,
                    rule_type="age",
                    parameter="age",
                    operator="<",
                    threshold=threshold,
                    unit="years",
                    action="EXCLUDE",
                    evidence_text=text,
                    index=start_index
                )
            )

            return rules

    # --------------------------------------------------
    # "younger than 18 years"
    # --------------------------------------------------

    match = re.search(
        r"younger than\s+(\d+)\s*years?",
        lower
    )

    if match:

        threshold = int(
            match.group(1)
        )

        rules.append(
            make_rule(
                trial_id,
                chunk_id,
                "age",
                "age",
                "<",
                threshold,
                "years",
                "EXCLUDE",
                text,
                start_index
            )
        )

    return rules


def extract_uln_lab_rules(
    trial_id: str,
    chunk_id: str,
    text: str,
    start_index: int
):

    rules = []

    for parameter, aliases in LAB_NAMES.items():

        for alias in aliases:

            escaped = re.escape(
                alias
            )

            # Examples:
            #
            # ALT > 3 x ULN
            # ALT > 3 times ULN
            # ALT greater than 3 times the upper limit of normal

            patterns = [
                (
                    rf"\b{escaped}\b"
                    rf".{{0,80}}?"
                    rf"(?:>|greater than|above|exceeds)"
                    rf"\s*(\d+(?:\.\d+)?)"
                    rf"\s*(?:x|times)?\s*"
                    rf"(?:the\s+)?"
                    rf"(?:upper limit of normal|ULN)"
                )
            ]

            matched = False

            for pattern in patterns:

                match = re.search(
                    pattern,
                    text,
                    flags=re.IGNORECASE
                )

                if not match:
                    continue

                threshold = float(
                    match.group(1)
                )

                rules.append(
                    make_rule(
                        trial_id=trial_id,
                        chunk_id=chunk_id,
                        rule_type="lab",
                        parameter=parameter,
                        operator=">",
                        threshold=threshold,
                        unit="ULN",
                        action=determine_action(text),
                        evidence_text=text,
                        index=start_index + len(rules)
                    )
                )

                matched = True
                break

            if matched:
                break

    return rules


def extract_egfr_rules(
    trial_id: str,
    chunk_id: str,
    text: str,
    start_index: int
):

    patterns = [
        (
            r"\beGFR\b"
            r".{0,80}?"
            r"(?:<|less than|below)"
            r"\s*(\d+(?:\.\d+)?)"
        ),
        (
            r"\beGFR\b"
            r".{0,80}?"
            r"(?:must be|at least|>=|greater than or equal to)"
            r"\s*(\d+(?:\.\d+)?)"
        )
    ]

    lower = text.lower()

    # Explicit exclusion such as:
    # eGFR < 30
    match = re.search(
        patterns[0],
        text,
        re.IGNORECASE
    )

    if match:

        return [
            make_rule(
                trial_id,
                chunk_id,
                "lab",
                "eGFR",
                "<",
                float(match.group(1)),
                "mL/min/1.73m2",
                "EXCLUDE",
                text,
                start_index
            )
        ]

    # Inclusion requirement:
    # eGFR >= 30
    #
    # Convert to failure condition:
    # eGFR < 30 -> EXCLUDE

    match = re.search(
        patterns[1],
        text,
        re.IGNORECASE
    )

    if match:

        return [
            make_rule(
                trial_id,
                chunk_id,
                "lab",
                "eGFR",
                "<",
                float(match.group(1)),
                "mL/min/1.73m2",
                "EXCLUDE",
                text,
                start_index
            )
        ]

    return []


def extract_rules_from_chunk(
    chunk: dict,
    start_index: int = 1
):

    trial_id = chunk[
        "trial_id"
    ]

    chunk_id = chunk[
        "chunk_id"
    ]

    text = chunk.get(
        "text",
        ""
    )

    rules = []

    extractors = [
        extract_age_rules,
        extract_uln_lab_rules,
        extract_egfr_rules
    ]

    for extractor in extractors:

        extracted = extractor(
            trial_id,
            chunk_id,
            text,
            start_index + len(rules)
        )

        rules.extend(
            extracted
        )

    return rules