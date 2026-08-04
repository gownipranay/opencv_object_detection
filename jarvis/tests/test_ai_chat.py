import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis import llm_client
from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import ai_chat
from jarvis.storage import Storage

# ai_chat.chat() is always monkeypatched here -- no test ever makes a real
# network call to the NVIDIA API.


def make_ctx(tmp_path):
    return Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)


def make_engine():
    engine = Engine()
    ai_chat.register(engine)
    return engine


def test_not_configured_gives_setup_instructions(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: False)
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("why is the sky blue", ctx)
    assert "NVIDIA_API_KEY" in response


def test_configured_calls_llm_and_returns_reply(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: True)
    monkeypatch.setattr(llm_client, "chat", lambda history, **k: "Scattering of sunlight.")

    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("why is the sky blue", ctx)

    assert response == "Scattering of sunlight."
    assert ctx.chat_history[-2] == {"role": "user", "content": "why is the sky blue"}
    assert ctx.chat_history[-1] == {"role": "assistant", "content": "Scattering of sunlight."}


def test_llm_error_rolls_back_history_and_shows_message(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: True)

    def boom(history, **k):
        raise llm_client.LLMError("service down")

    monkeypatch.setattr(llm_client, "chat", boom)

    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("why is the sky blue", ctx)

    assert response == "service down"
    assert ctx.chat_history == []


def test_history_is_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: True)
    monkeypatch.setattr(llm_client, "chat", lambda history, **k: "ok")

    engine = make_engine()
    ctx = make_ctx(tmp_path)
    for i in range(20):
        engine.handle(f"question number {i}", ctx)

    assert len(ctx.chat_history) <= ai_chat.MAX_HISTORY_MESSAGES


def test_ai_status_reports_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: True)
    monkeypatch.setattr(llm_client, "model_name", lambda: "meta/llama-3.1-8b-instruct")
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("ai status", ctx)
    assert "on" in response.lower()
    assert "meta/llama-3.1-8b-instruct" in response


def test_ai_status_reports_not_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "is_configured", lambda: False)
    engine = make_engine()
    ctx = make_ctx(tmp_path)
    response = engine.handle("ai status", ctx)
    assert "NVIDIA_API_KEY" in response
