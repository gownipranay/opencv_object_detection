import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import notes
from jarvis.storage import Storage


def make_ctx(tmp_path):
    return Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)


def make_engine():
    engine = Engine()
    notes.register(engine)
    return engine


def test_add_and_list_note(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)

    response = engine.handle("take a note buy milk", ctx)
    assert "#1" in response

    listing = engine.handle("read my notes", ctx)
    assert "buy milk" in listing


def test_no_notes_message(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    assert "don't have any notes" in engine.handle("list notes", ctx)


def test_delete_note(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    engine.handle("take a note walk the dog", ctx)
    response = engine.handle("delete note 1", ctx)
    assert "Deleted note #1" in response
    assert "don't have any notes" in engine.handle("list notes", ctx)


def test_delete_missing_note(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("delete note 99", ctx)
    assert "don't have a note #99" in response


def test_clear_notes(tmp_path):
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    engine.handle("take a note one", ctx)
    engine.handle("take a note two", ctx)
    engine.handle("clear notes", ctx)
    assert "don't have any notes" in engine.handle("list notes", ctx)


def test_notes_persist_across_storage_instances(tmp_path):
    path = tmp_path / "memory.json"
    ctx1 = Context(storage=Storage(path), speak=lambda t: None)
    make_engine().handle("take a note persisted", ctx1)

    ctx2 = Context(storage=Storage(path), speak=lambda t: None)
    response = make_engine().handle("read my notes", ctx2)
    assert "persisted" in response
