import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import reminders
from jarvis.storage import Storage


def make_ctx(tmp_path):
    spoken = []
    ctx = Context(storage=Storage(tmp_path / "memory.json"), speak=spoken.append)
    return ctx, spoken


def make_engine():
    engine = Engine()
    reminders.register(engine)
    return engine


def test_relative_reminder_is_scheduled(tmp_path):
    engine = make_engine()
    ctx, _ = make_ctx(tmp_path)
    response = engine.handle("remind me to check the oven in 20 minutes", ctx)
    assert "check the oven" in response
    assert "#1" in response

    pending = ctx.storage.get("reminders")
    assert len(pending) == 1
    due = datetime.fromisoformat(pending[0]["due"])
    assert timedelta(minutes=19) < due - datetime.now() < timedelta(minutes=21)


def test_timer_is_scheduled(tmp_path):
    engine = make_engine()
    ctx, _ = make_ctx(tmp_path)
    response = engine.handle("set a timer for 10 minutes", ctx)
    assert "Timer set" in response
    assert len(ctx.storage.get("reminders")) == 1


def test_list_reminders(tmp_path):
    engine = make_engine()
    ctx, _ = make_ctx(tmp_path)
    engine.handle("remind me to stretch in 5 minutes", ctx)
    response = engine.handle("list reminders", ctx)
    assert "stretch" in response


def test_cancel_reminder(tmp_path):
    engine = make_engine()
    ctx, _ = make_ctx(tmp_path)
    engine.handle("remind me to stretch in 5 minutes", ctx)
    response = engine.handle("cancel reminder 1", ctx)
    assert "Cancelled reminder #1" in response
    assert "no pending reminders" in engine.handle("list reminders", ctx)


def test_fire_due_speaks_and_marks_fired(tmp_path):
    ctx, spoken = make_ctx(tmp_path)
    past = (datetime.now() - timedelta(minutes=1)).isoformat(timespec="seconds")
    ctx.storage.set("reminders", [{"id": 1, "text": "wake up", "due": past, "fired": False}])

    fired = reminders.fire_due(ctx)

    assert len(fired) == 1
    assert any("wake up" in s for s in spoken)
    assert ctx.storage.get("reminders")[0]["fired"] is True


def test_fire_due_ignores_future_reminders(tmp_path):
    ctx, spoken = make_ctx(tmp_path)
    future = (datetime.now() + timedelta(hours=1)).isoformat(timespec="seconds")
    ctx.storage.set("reminders", [{"id": 1, "text": "later", "due": future, "fired": False}])

    fired = reminders.fire_due(ctx)

    assert fired == []
    assert spoken == []
