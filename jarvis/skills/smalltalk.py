"""Greetings, identity, help, and exit."""
from __future__ import annotations

import random

GREETINGS = [
    "Hello! How can I help?",
    "Hi there.",
    "Hey. What do you need?",
]

IDENTITY = (
    "I'm Jarvis, a rule-based assistant. I run entirely on your device, "
    "match what you say against a list of patterns, and run a matching "
    "skill. No cloud, no API keys, no machine learning."
)


def _greet(match, ctx) -> str:
    return random.choice(GREETINGS)


def _identity(match, ctx) -> str:
    return IDENTITY


def _thanks(match, ctx) -> str:
    return "You're welcome."


def _make_help(engine):
    def _help(match, ctx) -> str:
        lines = engine.help_lines()
        return "Here's what I can do:\n  - " + "\n  - ".join(lines)

    return _help


def _exit(match, ctx) -> str:
    ctx.stop_event.requested = True
    return "Goodbye."


def register(engine) -> None:
    engine.register(
        "greeting",
        r"\b(hi|hello|hey)\b(?!.*\?)",
        _greet,
        "Say 'hello' to greet me.",
    )
    engine.register(
        "identity",
        r"\b(who are you|what are you|what('?s| is) your name)\b",
        _identity,
        "'Who are you?' - learn what I am.",
    )
    engine.register(
        "thanks",
        r"\b(thanks|thank you)\b",
        _thanks,
        "Say 'thanks' any time.",
    )
    engine.register(
        "help",
        r"\b(help|what can you do|list commands)\b",
        _make_help(engine),
        "'help' - list every command I understand.",
    )
    engine.register(
        "exit",
        r"\b(exit|quit|stop listening|goodbye|bye|shut ?down)\b",
        _exit,
        "'exit' / 'quit' / 'bye' - end the session.",
    )
