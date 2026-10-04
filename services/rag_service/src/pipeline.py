from src.rag.retriever import (
    Retriever
)

from src.rag.metadata_filter import (
    build_trial_query
)

from src.safety.rule_engine import (
    RuleEngine,
    derive_decision
)


class TrialGuardPipeline:

    def __init__(self):

        self.rule_engine = (
            RuleEngine()
        )

        self.retriever = (
            Retriever()
        )

    def evaluate(
        self,
        request
    ):

        trial_id = (
            request.trial_id
        )

        patient = (
            request.patient
            .model_dump()
        )

        # ======================================
        # 1. RULES
        # ======================================

        self.rule_engine.reload()

        rules = (
            self.rule_engine
            .get_rules(
                trial_id
            )
        )

        if not rules:

            rule_results = []

            decision = "REVIEW"
            eligibility = "UNCERTAIN"
            needs_review = True

        else:

            rule_results = (
                self.rule_engine
                .evaluate(
                    patient,
                    trial_id
                )
            )

            (
                decision,
                eligibility,
                needs_review
            ) = derive_decision(
                rule_results
            )

        # ======================================
        # 2. RAG QUERY
        # ======================================

        query = (
            build_trial_query(
                request,
                rule_results
            )
        )

        # ======================================
        # 3. RETRIEVAL
        # ======================================

        retrieved = (
            self.retriever
            .retrieve_trial(
                query=query,
                trial_id=trial_id,
                k=6
            )
        )

        # ======================================
        # 4. EVIDENCE
        # ======================================

        evidence = []

        seen = set()

        for item in retrieved:

            chunk_id = (
                item["chunk_id"]
            )

            if chunk_id in seen:
                continue

            seen.add(
                chunk_id
            )

            metadata = (
                item["metadata"]
            )

            evidence.append({
                "source":
                    metadata.get(
                        "source",
                        "ClinicalTrials.gov"
                    ),

                "trial_id":
                    trial_id,

                "section":
                    metadata.get(
                        "section",
                        "eligibility"
                    ),

                "chunk_id":
                    chunk_id,

                "text":
                    item["text"]
            })

        # ======================================
        # 5. VIOLATIONS
        # ======================================

        violations = []

        for result in rule_results:

            if (
                result["status"]
                != "VIOLATION"
            ):
                continue

            violations.append({
                "rule_id":
                    result["rule_id"],

                "parameter":
                    result["parameter"],

                "value":
                    result.get(
                        "value"
                    ),

                "threshold":
                    result.get(
                        "threshold"
                    ),

                "unit":
                    result.get(
                        "unit"
                    ),

                "action":
                    result.get(
                        "action",
                        "REVIEW"
                    ),

                "reason":
                    result.get(
                        "reason",
                        "Protocol rule violation."
                    )
            })

        # ======================================
        # 6. MATCHED CRITERIA
        # ======================================

        matched = []

        for result in rule_results:

            if (
                result["status"]
                != "PASS"
            ):
                continue

            # DOSE_CHECK is not an eligibility
            # criterion, so don't report it as
            # an inclusion PASS here.

            if (
                result.get("action")
                == "DOSE_CHECK"
            ):
                continue

            matched.append({
                "criterion":
                    result["parameter"],

                "result":
                    "PASS",

                "value":
                    result.get(
                        "value"
                    )
            })

        # ======================================
        # 7. UNKNOWN
        # ======================================

        unknown = [
            result["parameter"]

            for result
            in rule_results

            if result["status"]
            == "UNKNOWN"
        ]

        if not rules:

            unknown.append(
                "No structured rules available."
            )

        # ======================================
        # 8. EXPLANATION
        # ======================================

        explanation = (
            self._explanation(
                decision,
                violations,
                unknown
            )
        )

        # ======================================
        # 9. CONFIDENCE
        # ======================================

        confidence = (
            self._confidence(
                rule_results,
                evidence
            )
        )

        return {
            "trial_id":
                trial_id,

            "decision":
                decision,

            "eligibility":
                eligibility,

            "violations":
                violations,

            "matched_criteria":
                matched,

            "unknown_criteria":
                unknown,

            "evidence":
                evidence,

            "explanation":
                explanation,

            "confidence":
                confidence,

            "needs_human_review":
                needs_review
        }

    @staticmethod
    def _explanation(
        decision,
        violations,
        unknown
    ):

        if decision == "FAIL":

            names = ", ".join(
                violation[
                    "parameter"
                ]

                for violation
                in violations
            )

            return (
                "The patient fails one or "
                "more evaluated trial "
                f"criteria: {names}."
            )

        if decision == "REVIEW":

            return (
                "Eligibility cannot be "
                "determined conclusively "
                "because required protocol "
                "information is missing or "
                "unresolved."
            )

        return (
            "The patient satisfies all "
            "currently evaluated eligibility "
            "rules."
        )

    @staticmethod
    def _confidence(
        results,
        evidence
    ):

        eligibility_results = [
            result
            for result
            in results
            if result.get(
                "action"
            ) != "DOSE_CHECK"
        ]

        if not eligibility_results:
            return 0.25

        known = sum(
            result["status"]
            in {
                "PASS",
                "VIOLATION",
                "NOT_APPLICABLE"
            }

            for result
            in eligibility_results
        )

        coverage = (
            known
            / len(
                eligibility_results
            )
        )

        evidence_factor = (
            1.0
            if evidence
            else 0.5
        )

        confidence = (
            0.45
            + (
                0.45
                * coverage
                * evidence_factor
            )
        )

        return round(
            min(
                confidence,
                0.95
            ),
            2
        )


pipeline = TrialGuardPipeline()


def run_pipeline(
    request
):

    return pipeline.evaluate(
        request
    )