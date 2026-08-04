import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.storage import Storage


def make_ctx(tmp_path):
    spoken = []
    ctx = Context(storage=Storage(tmp_path / "memory.json"), speak=spoken.append)
    return ctx, spoken


def test_first_matching_rule_wins():
    engine = Engine()
    engine.register("a", r"\bhello\b", lambda m, c: "A", "help a")
    engine.register("b", r"\bhello\b", lambda m, c: "B", "help b")
    assert engine.handle("hello", ctx=None) == "A"


def test_no_match_returns_fallback():
    engine = Engine()
    engine.register("a", r"\bhello\b", lambda m, c: "A", "help a")
    response = engine.handle("gibberish that matches nothing", ctx=None)
    assert "help" in response.lower()


def test_empty_input_is_handled():
    engine = Engine()
    assert "didn't catch" in engine.handle("", ctx=None).lower()


def test_handler_exception_does_not_crash_engine():
    def boom(match, ctx):
        raise ValueError("kaboom")

    engine = Engine()
    engine.register("boom", r"\bboom\b", boom, "boom help")
    response = engine.handle("boom", ctx=None)
    assert "kaboom" in response


def test_help_lines_deduplicated():
    engine = Engine()
    engine.register("a", r"\ba\b", lambda m, c: "", "same help")
    engine.register("b", r"\bb\b", lambda m, c: "", "same help")
    engine.register("c", r"\bc\b", lambda m, c: "", "different help")
    assert engine.help_lines() == ["same help", "different help"]
