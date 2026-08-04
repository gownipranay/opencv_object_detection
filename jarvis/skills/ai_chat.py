"""Open-ended conversation, backed by the free NVIDIA NIM API.

This is registered *last* (see skills/__init__.py) so every other skill's
regex gets first refusal. Only input that matches nothing more specific --
real questions, "explain X", "help me write Y", small talk the built-in
smalltalk skill doesn't cover, and so on -- falls through to here and gets
sent to the NVIDIA API. Phone actions (calls, texts, flashlight, notes,
timers, ...) are matched and executed earlier by the deterministic rule
skills and never reach this file.
"""
from __future__ import annotations

from .. import llm_client

MAX_HISTORY_MESSAGES = 12


def _not_configured_message() -> str:
    return (
        "I don't have an NVIDIA API key set up yet, so I can only run my "
        "built-in commands. Say 'help' to see them, or set NVIDIA_API_KEY "
        "(see jarvis/README.md) to unlock free-form conversation."
    )


def _ai_status(match, ctx) -> str:
    if llm_client.is_configured():
        return f"AI chat is on, using {llm_client.model_name()} via the NVIDIA API."
    return _not_configured_message()


def _ask(match, ctx) -> str:
    text = match.group(0).strip()
    if not llm_client.is_configured():
        return _not_configured_message()

    history = ctx.chat_history
    history.append({"role": "user", "content": text})
    del history[:-MAX_HISTORY_MESSAGES]

    try:
        reply = llm_client.chat(history)
    except llm_client.LLMError as exc:
        history.pop()
        return str(exc)

    history.append({"role": "assistant", "content": reply})
    del history[:-MAX_HISTORY_MESSAGES]
    return reply


def register(engine) -> None:
    engine.register(
        "ai_status",
        r"\b(are you online|ai status|is the ai (on|working))\b",
        _ai_status,
        "'ai status' - check whether NVIDIA API chat is configured.",
    )
    engine.register(
        "ai_chat",
        r".+",
        _ask,
        "anything else - ask a real question; Jarvis answers using the free NVIDIA AI API.",
    )
