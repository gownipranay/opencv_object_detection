import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import datetime_skill, smalltalk
from jarvis.storage import Storage


def make_ctx(tmp_path):
    return Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)


def make_engine():
    engine = Engine()
    smalltalk.register(engine)
    datetime_skill.register(engine)
    return engine


def test_time_query(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("what time is it", ctx)
    assert "It's" in response


def test_date_query(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("what's the date", ctx)
    assert "Today is" in response


def test_help_lists_registered_rules(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("help", ctx)
    assert "time" in response.lower()


def test_exit_sets_stop_event(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    assert ctx.stop_event.requested is False
    engine.handle("exit", ctx)
    assert ctx.stop_event.requested is True


def test_identity(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("who are you", ctx)
    assert "jarvis" in response.lower()
