import json
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)


CANDIDATE_RULES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rules"
    / "candidate_demo_rules.json"
)


class EvidenceStore:

    def __init__(self):
        self.by_id = {}
        self.rule_sources = {}
        self._load_chunks()
        self._load_rule_sources()

    def _load_chunks(self):
        if not CHUNKS_FILE.exists():
            return

        with CHUNKS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            for line in file:
                if not line.strip():
                    continue

                chunk = json.loads(line)
                chunk_id = chunk.get("chunk_id")

                if chunk_id:
                    self.by_id[chunk_id] = chunk

    def _load_rule_sources(self):
        if not CANDIDATE_RULES_FILE.exists():
            return

        with CANDIDATE_RULES_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            document = json.load(file)

        for rules in document.get("trials", {}).values():
            for rule in rules:
                source_chunk_id = rule.get("source_chunk_id")

                if source_chunk_id:
                    self.rule_sources[rule.get("rule_id")] = source_chunk_id

    def get(self, chunk_id):
        return self.by_id.get(chunk_id)

    def source_chunk_id_for_rule(self, rule_id):
        return self.rule_sources.get(rule_id)
