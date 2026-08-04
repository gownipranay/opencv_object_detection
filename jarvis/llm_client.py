"""Client for NVIDIA's OpenAI-compatible NIM chat API.

Used only by the open-ended "ask Jarvis anything" fallback in
skills/ai_chat.py. Every direct phone action (calls, texts, flashlight,
notes, timers, ...) stays on the deterministic rule engine in engine.py so
a model's mistake can never trigger a real-world action -- the API is only
ever used to generate a spoken/typed reply.

The API key is read from the NVIDIA_API_KEY environment variable, or from
~/.jarvis/nvidia_api_key as a fallback -- both live outside this git repo
and are never hardcoded or committed here. See jarvis/README.md for setup.
"""
from __future__ import annotations

import os
from pathlib import Path

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"
_KEY_FILE = Path.home() / ".jarvis" / "nvidia_api_key"

SYSTEM_PROMPT = (
    "You are Jarvis, a helpful voice assistant running locally on the user's "
    "phone. Reply in short, plain, conversational text with no markdown, "
    "headers, or code fences unless the user explicitly asks for code -- your "
    "replies may be read aloud by text-to-speech. Keep answers to a few "
    "sentences unless the user asks for more detail."
)


class LLMError(RuntimeError):
    pass


def _api_key() -> str | None:
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if key:
        return key
    if _KEY_FILE.exists():
        key = _KEY_FILE.read_text().strip()
        if key:
            return key
    return None


def is_configured() -> bool:
    return _api_key() is not None


def model_name() -> str:
    return os.environ.get("NVIDIA_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def chat(history: list[dict], timeout: float = 30.0) -> str:
    """Send `history` ([{"role": ..., "content": ...}, ...]) and return the reply text."""
    api_key = _api_key()
    if not api_key:
        raise LLMError(
            "No NVIDIA API key is set. See jarvis/README.md for how to set "
            "NVIDIA_API_KEY (or ~/.jarvis/nvidia_api_key)."
        )

    try:
        import requests
    except ImportError as exc:
        raise LLMError(
            "The 'requests' package isn't installed. Run: pip install requests"
        ) from exc

    payload = {
        "model": model_name(),
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history,
        "temperature": 0.5,
        "top_p": 0.9,
        "max_tokens": 400,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise LLMError(f"Couldn't reach the NVIDIA API: {exc}") from exc

    if response.status_code == 401:
        raise LLMError("The NVIDIA API rejected the key (401 Unauthorized). Check NVIDIA_API_KEY.")
    if response.status_code == 429:
        raise LLMError("The NVIDIA API rate-limited this request (429). Try again in a moment.")
    if response.status_code != 200:
        raise LLMError(f"The NVIDIA API returned an error ({response.status_code}): {response.text[:200]}")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError) as exc:
        raise LLMError("The NVIDIA API returned an unexpected response.") from exc
