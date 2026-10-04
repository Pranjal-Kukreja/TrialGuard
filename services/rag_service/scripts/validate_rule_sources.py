import json
import sys
from pathlib import Path

def validate_sources():
    candidate_path = Path("trialgaurd-ai-ml/data/processed/rules/candidate_demo_rules.json")
    chunks_path = Path("trialgaurd-ai-ml/data/processed/chunks/trial_chunks.jsonl")

    if not candidate_path.exists():
        print(f"Candidate file not found: {candidate_path}")
        return False
    
    if not chunks_path.exists():
        print(f"Chunks file not found: {chunks_path}")
        return False

    with open(candidate_path, 'r') as f:
        candidates = json.load(f)

    # Load chunks into a map
    chunk_map = {}
    with open(chunks_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            chunk_map[chunk['chunk_id']] = chunk

    errors = []
    found_count = 0

    for trial_id, rules in candidates.get("trials", {}).items():
        for rule in rules:
            chunk_id = rule.get("source_chunk_id")
            if not chunk_id:
                errors.append(f"Rule {rule.get('rule_id')} has no source_chunk_id")
                continue

            if chunk_id not in chunk_map:
                errors.append(f"MISSING: Rule {rule.get('rule_id')} references non-existent chunk {chunk_id}")
                continue

            chunk = chunk_map[chunk_id]
            
            # Verify trial_id match
            if chunk['trial_id'] != rule['trial_id']:
                errors.append(f"WRONG_TRIAL: Rule {rule.get('rule_id')} (trial {rule['trial_id']}) references chunk from trial {chunk['trial_id']}")

            # Verify evidence text existence (ignoring case/whitespace for basic check)
            evidence = rule.get("evidence_text", "")
            if evidence.lower().strip() not in chunk['text'].lower().strip():
                # Allow partial match if chunk is larger
                if evidence.lower().strip() not in chunk['text'].lower().strip():
                    errors.append(f"TEXT_MISMATCH: Rule {rule.get('rule_id')} evidence text not found in chunk {chunk_id}")
            
            found_count += 1

    if errors:
        print("\n".join(errors))
        print(f"\nValidation failed with {len(errors)} errors.")
        return False
    
    print(f"Provenance validation successful! Checked {found_count} rules.")
    return True

if __name__ == "__main__":
    if not validate_sources():
        sys.exit(1)
