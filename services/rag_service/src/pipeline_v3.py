from src.rag.retriever import (
    Retriever
)

from src.safety.result_adapter import (
    adapt_engine_result
)

from src.safety.rule_engine_v3 import (
    evaluate_trial
)

from src.rag.query_builder import (
    build_trial_query,
    build_fda_query
)

from src.rag.evidence_guard import (
    filter_trial_evidence
)

from src.rag.evidence_store import (
    EvidenceStore
)

from src.llm.reasoner import (
    ComplianceReasoner
)

from src.llm.client import (
    is_llm_configured
)

import os

class TrialGuardPipelineV3:

    def __init__(self):

        self.retriever = (
            Retriever()
        )

        self.reasoner = None

        self.evidence_store = (
            EvidenceStore()
        )

    def evaluate(
        self,
        request
    ):
        """Evaluate deterministically, retrieve evidence, then explain with the LLM."""

        return self._evaluate(
            request,
            use_reasoner=True
        )

    def _evaluate(
        self,
        request,
        use_reasoner=False
    ):

        trial_id = (
            request.trial_id
        )

        patient = (
            request.patient
            .model_dump()
        )

        # ==================================
        # 1. DETERMINISTIC ENGINE
        # ==================================

        engine_result = (
            evaluate_trial(
                trial_id,
                patient
            )
        )

        adapted = (
            adapt_engine_result(
                engine_result
            )
        )

        # ==================================
        # 2. RAG QUERY
        # ==================================

        query = (
            build_trial_query(
                trial_id=trial_id,
                patient=patient,
                rule_results=(
                    engine_result.get(
                        "rule_results",
                        []
                    )
                ),
                user_query=(
                    request.query
                )
            )
        )

        # ==================================
        # 3. RETRIEVE TRIAL EVIDENCE
        # ==================================

        rag_results = (
            self.retriever
            .retrieve_trial(
                query=query,
                trial_id=trial_id,
                k=6
            )
        )

        evidence = []

        for item in rag_results:

            metadata = (
                item[
                    "metadata"
                ]
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
                    item[
                        "chunk_id"
                    ],

                "text":
                    item[
                        "text"
                    ],

                "score":
                    (
                        1.0
                        - item["distance"]
                        if (
                            item.get(
                                "distance"
                            )
                            is not None
                        )
                        else None
                    )
            })

        evidence = filter_trial_evidence(
            evidence,
            trial_id
        )

        exact_evidence = []
        missing_provenance = False

        for rule_result in engine_result.get(
            "rule_results",
            []
        ):
            if rule_result.get("state") not in {
                "FAIL",
                "UNKNOWN",
            }:
                continue

            source_chunk_id = (
                rule_result.get(
                    "source_chunk_id"
                )
                or self.evidence_store
                .source_chunk_id_for_rule(
                    rule_result.get("rule_id")
                )
            )
            source_chunk = self.evidence_store.get(
                source_chunk_id
            )

            if source_chunk_id and not source_chunk:
                missing_provenance = True

            if not source_chunk:
                continue

            exact_evidence.append({
                "source": source_chunk.get(
                    "source",
                    "ClinicalTrials.gov"
                ),
                "trial_id": trial_id,
                "section": source_chunk.get(
                    "section",
                    "eligibility"
                ),
                "chunk_id": source_chunk["chunk_id"],
                "text": source_chunk.get("text", ""),
                "score": None,
            })

        combined_evidence = []
        seen_chunk_ids = set()

        for item in exact_evidence + evidence:
            chunk_id = item.get("chunk_id")

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)
            combined_evidence.append(item)

        evidence = combined_evidence

        if missing_provenance:
            adapted["needs_human_review"] = True

        # ==================================
        # 4. RETRIEVE FDA SAFETY EVIDENCE
        # ==================================

        fda_query = (
            build_fda_query(
                patient,
                trial_id=trial_id
            )
        )

        fda_results = (
            self.retriever
            .retrieve_fda(
                query=fda_query,
                k=4
            )
        )

        safety_evidence = []

        for item in fda_results:

            metadata = (
                item[
                    "metadata"
                ]
            )

            safety_evidence.append({
                "source":
                    metadata.get(
                        "source",
                        "openFDA Drug Label"
                    ),

                "drug":
                    metadata.get(
                        "drug_names"
                    ),

                "section":
                    metadata.get(
                        "section",
                        "unknown"
                    ),

                "chunk_id":
                    item[
                        "chunk_id"
                    ],

                "text":
                    item[
                        "text"
                    ],

                "score":
                    (
                        1.0
                        - item["distance"]
                        if (
                            item.get(
                                "distance"
                            )
                            is not None
                        )
                        else None
                    )
            })

        # ==================================
        # 5. LLM EXPLANATION WITH FALLBACK
        # ==================================

        llm_used = False
        fallback_used = False

        try:
            if not use_reasoner or not is_llm_configured():
                raise RuntimeError(
                    "LLM explanation disabled."
                )

            if self.reasoner is None:
                self.reasoner = ComplianceReasoner()

            explanation = (
                self.reasoner.explain(
                    trial_id=trial_id,
                    patient=patient,
                    deterministic_result=adapted,
                    evidence=evidence,
                    safety_evidence=safety_evidence,
                    query=request.query
                )
            )

            llm_used = True

        except Exception:

            fallback_used = True

            if (
                adapted["decision"]
                == "FAIL"
            ):

                explanation = (
                    "One or more deterministic "
                    "trial eligibility criteria "
                    "were violated."
                )

            elif (
                adapted["decision"]
                == "REVIEW"
            ):

                explanation = (
                    "Eligibility requires review "
                    "because required information "
                    "is missing or unresolved."
                )

            else:

                explanation = (
                    "All currently evaluated "
                    "eligibility criteria were "
                    "satisfied."
                )

        return {
            "trial_id":
                trial_id,

            **adapted,

            "evidence":
                evidence,

            "safety_evidence":
                safety_evidence,

            "explanation":
                explanation,

            "confidence":
                self._confidence(
                    adapted,
                    evidence
                ),

            "generation_metadata": {
                "llm_used": llm_used,
                "llm_model": (
                    os.getenv("LLM_MODEL")
                    if llm_used
                    else None
                ),
                "fallback_used": fallback_used,
            }
        }

    def evaluate_without_llm(
        self,
        request
    ):
        """Evaluate rules and retrieval without calling the LLM."""

        return self._evaluate(
            request,
            use_reasoner=False
        )

    @staticmethod
    def _confidence(
        adapted,
        evidence
    ):

        known = (
            len(
                adapted[
                    "matched_criteria"
                ]
            )
            +
            len(
                adapted[
                    "violations"
                ]
            )
        )

        unknown = len(
            adapted[
                "unknown_criteria"
            ]
        )

        total = (
            known
            + unknown
        )

        if total == 0:
            return 0.30

        coverage = (
            known
            / total
        )

        evidence_factor = (
            1.0
            if evidence
            else 0.5
        )

        result = (
            0.35
            + (
                0.55
                * coverage
                * evidence_factor
            )
        )

        return round(
            min(
                result,
                0.95
            ),
            2
        )