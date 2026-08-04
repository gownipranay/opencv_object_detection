import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import apps, device
from jarvis.storage import Storage

# This dev environment has no Termux:API binaries, so these tests double as
# proof that every device/app skill fails gracefully (never crashes) when
# the phone-only tools are missing.


def make_ctx(tmp_path):
    return Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)


def test_battery_without_termux_api(tmp_path):
    engine = Engine()
    device.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("what's my battery", ctx)
    assert "battery" in response.lower()


def test_save_and_use_contact(tmp_path):
    engine = Engine()
    device.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("save contact mom as 5551234567", ctx)
    assert "Saved contact mom" in response
    assert ctx.storage.get("contacts")["mom"] == "5551234567"


def test_call_without_termux_api_is_graceful(tmp_path):
    engine = Engine()
    device.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("call mom", ctx)
    assert "couldn't place the call" in response


def test_web_search_constructs_google_url(tmp_path, monkeypatch):
    opened = {}

    def fake_run(cmd, **kwargs):
        opened["cmd"] = cmd

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(apps.shutil, "which", lambda name: "/usr/bin/termux-open-url" if name == "termux-open-url" else None)
    monkeypatch.setattr(apps.subprocess, "run", fake_run)

    engine = Engine()
    apps.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("search for best pizza", ctx)

    assert "google.com/search?q=best" in opened["cmd"][1]
    assert "Opening" in response


def test_open_unknown_app_asks_to_be_taught(tmp_path):
    engine = Engine()
    apps.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("open some totally made up app", ctx)
    assert "don't know the app" in response


def test_remember_app_then_open(tmp_path, monkeypatch):
    monkeypatch.setattr(apps.shutil, "which", lambda name: "/usr/bin/am" if name == "am" else None)
    monkeypatch.setattr(apps.subprocess, "run", lambda *a, **k: None)

    engine = Engine()
    apps.register(engine)
    ctx = make_ctx(tmp_path)
    engine.handle("remember app myapp as com.example.myapp", ctx)
    response = engine.handle("open myapp", ctx)
    assert "Opening myapp" in response
