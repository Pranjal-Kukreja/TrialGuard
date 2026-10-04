from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_prompt(
	name: str
) -> str:
	"""Load a named prompt from the repository prompt directory."""

	prompt_path = (
		Path(__file__)
		.resolve()
		.parents[2]
		/ "prompts"
		/ name
	)

	if not prompt_path.is_file():
		raise FileNotFoundError(
			f"Prompt file not found: {prompt_path}"
		)

	return prompt_path.read_text(
		encoding="utf-8"
	)


def build_eligibility_messages(
	*,
	trial_id: str,
	patient: dict[str, Any],
	deterministic_result: dict[str, Any],
	evidence: list[dict[str, Any]],
	safety_evidence: list[dict[str, Any]],
) -> list[dict[str, str]]:
	"""Build an explanation prompt grounded in deterministic results."""

	context = {
		"trial_id": trial_id,
		"patient": patient,
		"deterministic_result": deterministic_result,
		"clinical_trial_evidence": evidence,
		"fda_safety_evidence": safety_evidence,
	}

	return [
		{
			"role": "system",
			"content": (
				"You are a clinical trial screening assistant. "
				"Summarize the supplied evidence clearly and cautiously. "
				"The deterministic eligibility status is authoritative. "
				"Do not change, infer, or override the decision, "
				"eligibility, confidence, or rule results. "
				"FDA safety evidence is informational only and must not "
				"change trial eligibility. Mention missing evidence."
			),
		},
		{
			"role": "user",
			"content": (
				"Explain this screening result in concise clinical language. "
				"Do not invent patient facts or clinical conclusions.\n\n"
				+ json.dumps(context, ensure_ascii=True, default=str)
			),
		},
	]
