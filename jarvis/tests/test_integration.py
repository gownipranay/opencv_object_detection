import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import register_all
from jarvis.storage import Storage

# Sanity check that every skill can be registered together without patterns
# stealing each other's commands.

SAMPLE_EXCHANGES = [
    ("who are you", "rule-based"),
    ("what time is it", "It's"),
    ("what's the date", "Today is"),
    ("what day is it", "It's"),
    ("calculate 12 * (3 + 4)", "84"),
    ("what is 9 plus 10", "19"),
    ("convert 10 km to miles", "miles"),
    ("take a note buy milk", "Noted"),
    ("read my notes", "buy milk"),
    ("remind me to stretch in 5 minutes", "stretch"),
    ("set a timer for 2 minutes", "Timer set"),
    ("list reminders", "stretch"),
    ("battery status", "battery"),
    ("save contact mom as 5551234567", "Saved contact mom"),
    ("what do you see", "download"),
    ("search for pizza", "google.com/search?q=pizza"),
    ("help", "Here's what I can do"),
]


def build_ctx(tmp_path):
    engine = Engine()
    register_all(engine)
    ctx = Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)
    return engine, ctx


def test_all_sample_commands_hit_the_right_skill(tmp_path):
    engine, ctx = build_ctx(tmp_path)
    for utterance, expected_fragment in SAMPLE_EXCHANGES:
        response = engine.handle(utterance, ctx)
        assert expected_fragment.lower() in response.lower(), (
            f"'{utterance}' -> '{response}' (expected to contain '{expected_fragment}')"
        )


def test_greeting_gets_a_greeting_back(tmp_path):
    from jarvis.skills.smalltalk import GREETINGS

    engine, ctx = build_ctx(tmp_path)
    assert engine.handle("hello", ctx) in GREETINGS


def test_unknown_command_gives_fallback(tmp_path):
    engine, ctx = build_ctx(tmp_path)
    response = engine.handle("please compose a symphony for me", ctx)
    assert "help" in response.lower()


def test_exit_ends_session(tmp_path):
    engine, ctx = build_ctx(tmp_path)
    engine.handle("goodbye", ctx)
    assert ctx.stop_event.requested is True
