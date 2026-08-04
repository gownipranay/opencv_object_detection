"""Entry point: `python -m jarvis` (or `python jarvis/main.py`).

Phone actions (calls, texts, flashlight, notes, timers, ...) are handled by
a local regex rule engine (jarvis/engine.py) with JSON-file memory
(jarvis/storage.py) -- fully offline, no API key needed for any of that.
Anything else falls through to the free NVIDIA API for real conversation
(jarvis/llm_client.py), only if NVIDIA_API_KEY is set; see jarvis/README.md.
"""
from __future__ import annotations

import argparse

from . import llm_client
from .context import Context
from .engine import Engine
from .io_backend import listen, speak
from .skills import register_all
from .storage import Storage
from .skills.reminders import start_scheduler

BANNER = (
    "Jarvis is ready.\n"
    "Try: 'what time is it', 'take a note buy milk', 'set a timer for 5 minutes',\n"
    "'what do you see', 'battery status', 'help' -- or just ask a question.\n"
    "Say 'exit' to quit."
)


def _status_line() -> str:
    if llm_client.is_configured():
        return f"AI chat: ON ({llm_client.model_name()}, via NVIDIA API)."
    return (
        "AI chat: OFF (no NVIDIA_API_KEY set -- built-in commands still work). "
        "See jarvis/README.md to enable free-form conversation."
    )


def build_engine() -> Engine:
    engine = Engine()
    register_all(engine)
    return engine


def run(voice: bool = False) -> None:
    engine = build_engine()
    storage = Storage()

    def _speak(text: str) -> None:
        speak(text, voice=voice)

    ctx = Context(storage=storage, speak=_speak)
    start_scheduler(ctx)

    print(BANNER)
    print(_status_line())
    while not ctx.stop_event.requested:
        text = listen(voice=voice)
        if not text:
            continue
        response = engine.handle(text, ctx)
        ctx.speak(response)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jarvis: rule-based phone control plus free-form AI chat via the NVIDIA API."
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Use Termux:API speech-to-text/text-to-speech instead of typed input (requires Termux:API).",
    )
    args = parser.parse_args()
    run(voice=args.voice)


if __name__ == "__main__":
    main()
