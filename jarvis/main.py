"""Entry point: `python -m jarvis` (or `python jarvis/main.py`).

Everything here is local and offline: a regex rule engine (jarvis/engine.py),
a JSON file for memory (jarvis/storage.py), and a handful of skill modules
under jarvis/skills/. No API keys are read, required, or used anywhere in
this project.
"""
from __future__ import annotations

import argparse

from .context import Context
from .engine import Engine
from .io_backend import listen, speak
from .skills import register_all
from .storage import Storage
from .skills.reminders import start_scheduler

BANNER = (
    "Jarvis (rule-based, offline) is ready.\n"
    "Try: 'what time is it', 'take a note buy milk', 'set a timer for 5 minutes',\n"
    "'what do you see', 'battery status', or 'help'. Say 'exit' to quit."
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
    while not ctx.stop_event.requested:
        text = listen(voice=voice)
        if not text:
            continue
        response = engine.handle(text, ctx)
        ctx.speak(response)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis: a rule-based, offline phone assistant.")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Use Termux:API speech-to-text/text-to-speech instead of typed input (requires Termux:API).",
    )
    args = parser.parse_args()
    run(voice=args.voice)


if __name__ == "__main__":
    main()
