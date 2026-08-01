import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _call_openai(prompt: str, *, model: str = OPENAI_MODEL, max_tokens: int = 300) -> Optional[Dict[str, Any]]:
    api_key = OPENAI_API_KEY
    if not api_key:
        return None

    endpoint = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful educational assistant. Return concise, polished, and faithful text only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    choices = body.get("choices") or []
    if not choices:
        return None

    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if isinstance(content, list):
        content = " ".join(part.get("text", "") for part in content if isinstance(part, dict))

    cleaned = re.sub(r"\s+", " ", str(content)).strip()
    if not cleaned:
        return None

    return {"content": cleaned}


def _fallback_summary(text: str, max_sentences: int = 8) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return "No content available for summary."

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    summary_sentences = sentences[:max_sentences]
    return " ".join(summary_sentences)


def summarize_text(text: str, max_sentences: int = 8) -> Dict:
    """Create a readable summary from extracted PDF content without hard truncation."""
    if OPENAI_API_KEY:
        prompt = (
            "Summarize the following educational content in a concise and readable way. "
            "Keep the key facts and avoid introducing new information.\n\n"
            f"Content:\n{text}"
        )
        llm_response = _call_openai(prompt, max_tokens=250)
        if llm_response and llm_response.get("content"):
            return {"summary": llm_response["content"]}

    return {"summary": _fallback_summary(text, max_sentences=max_sentences)}


def simplify_text(text: str, level: str = "beginner") -> Dict:
    """Simplify text using the optional LLM path when an API key is available."""
    if OPENAI_API_KEY:
        prompt = (
            f"Rewrite the following text for a {level} audience. "
            "Keep the meaning, improve readability, and make it concise.\n\n"
            f"Content:\n{text}"
        )
        llm_response = _call_openai(prompt, max_tokens=400)
        if llm_response and llm_response.get("content"):
            return {"level": level, "simplified": llm_response["content"]}

    simple = text.replace("utilize", "use").replace("demonstrate", "show")
    if level == "beginner":
        simple = ". ".join([s.strip()[:400] for s in simple.split('.')])
    return {"level": level, "simplified": simple}
