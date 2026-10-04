"""Shared OpenAI-compatible LLM client for gateway agents."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load local and root environment variables
load_dotenv(Path(__file__).parents[2] / ".env")
load_dotenv(Path(__file__).parents[1] / ".env")


def _build_llm(max_tokens: int) -> ChatOpenAI:
    api_key = os.getenv("KADO_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY or KADO_API_KEY is not configured")
    base_url = os.getenv("KADO_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://awesome.kado.so/openai/v1")
    model = os.getenv("KADO_MODEL") or os.getenv("OPENAI_MODEL", "kado")
    
    headers = {"x-bf-vk": api_key} if api_key else {}
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        max_tokens=max_tokens,
        timeout=15.0,
        request_timeout=15.0,
        default_headers=headers,
    )


def call_llm(prompt: str, max_tokens: int = 400) -> str:
    chain = ChatPromptTemplate.from_messages([("user", "{prompt}")]) | _build_llm(max_tokens)
    response = chain.invoke({"prompt": prompt})
    content = getattr(response, "content", "")
    if isinstance(content, list):
        content = "".join(str(part) for part in content)
    content = str(content).strip()
    if not content:
        raise RuntimeError("The configured LLM returned no text")
    return content


def parse_json_response(raw: str) -> dict:
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    result = json.loads(cleaned)
    if not isinstance(result, dict):
        raise ValueError("LLM response must be a JSON object")
    return result
