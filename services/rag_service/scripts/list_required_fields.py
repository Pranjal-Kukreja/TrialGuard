import json
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


RULE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rules"
    / "rules.json"
)


def collect_paths_from_rule(
    rule
):

    paths = []

    field_path = rule.get(
        "field_path"
    )

    if field_path:

        paths.append(
            field_path
        )

    for condition in rule.get(
        "conditions",
        []
    ):

        path = condition.get(
            "field_path"
        )

        if path:

            paths.append(
                path
            )

    applies_if = rule.get(
        "applies_if",
        {}
    )

    if isinstance(
        applies_if,
        dict
    ):

        paths.extend(
            applies_if.keys()
        )

    return paths


def extract_trial_rules(
    data
):

    trials = data.get(
        "trials",
        {}
    )

    result = {}

    for trial_id, config in (
        trials.items()
    ):

        # Supports:
        #
        # "NCT": [...]
        #
        # and
        #
        # "NCT": {
        #    "rules": [...]
        # }

        if isinstance(
            config,
            list
        ):

            rules = config

        elif isinstance(
            config,
            dict
        ):

            rules = config.get(
                "rules",
                []
            )

        else:

            rules = []

        result[
            trial_id
        ] = rules

    return result


def main():

    if not RULE_FILE.exists():

        raise FileNotFoundError(
            f"Rules file missing:\n"
            f"{RULE_FILE}"
        )

    with RULE_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    trials = extract_trial_rules(
        data
    )

    print("=" * 70)
    print("REQUIRED PATIENT FIELDS BY TRIAL")
    print("=" * 70)

    for trial_id, rules in (
        trials.items()
    ):

        paths = set()

        for rule in rules:

            paths.update(
                collect_paths_from_rule(
                    rule
                )
            )

        print(
            f"\n{trial_id}"
        )

        print("-" * 70)

        for path in sorted(
            paths
        ):

            print(
                f"  {path}"
            )

        print(
            f"\nTotal rules: "
            f"{len(rules)}"
        )

        print(
            f"Unique fields: "
            f"{len(paths)}"
        )


if __name__ == "__main__":
    main()