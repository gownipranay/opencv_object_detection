import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis import llm_client

# These tests never hit the real NVIDIA API -- requests.post is monkeypatched
# throughout, and the key-file fallback is redirected into tmp_path so a
# real ~/.jarvis/nvidia_api_key on the machine running the tests can't leak
# in or be touched.


@pytest.fixture(autouse=True)
def isolate_key_sources(monkeypatch, tmp_path):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)
    monkeypatch.setattr(llm_client, "_KEY_FILE", tmp_path / "nvidia_api_key")


def test_not_configured_without_key():
    assert llm_client.is_configured() is False
    with pytest.raises(llm_client.LLMError):
        llm_client.chat([{"role": "user", "content": "hi"}])


def test_configured_via_env_var(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")
    assert llm_client.is_configured() is True


def test_configured_via_key_file(tmp_path):
    key_file = tmp_path / "nvidia_api_key"
    key_file.write_text("nvapi-test-key\n")
    llm_client._KEY_FILE = key_file
    assert llm_client.is_configured() is True


def test_default_model_name():
    assert llm_client.model_name() == llm_client.DEFAULT_MODEL


def test_model_name_override(monkeypatch):
    monkeypatch.setenv("NVIDIA_MODEL", "some/other-model")
    assert llm_client.model_name() == "some/other-model"


def test_chat_sends_expected_payload_and_parses_reply(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")
    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": " Hello there. "}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("requests.post", fake_post)

    reply = llm_client.chat([{"role": "user", "content": "hi"}])

    assert reply == "Hello there."
    assert captured["url"] == llm_client.API_URL
    assert captured["headers"]["Authorization"] == "Bearer nvapi-test-key"
    assert captured["json"]["messages"][0]["role"] == "system"
    assert captured["json"]["messages"][-1] == {"role": "user", "content": "hi"}


def test_chat_raises_on_401(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-bad-key")

    class FakeResponse:
        status_code = 401
        text = "unauthorized"

    monkeypatch.setattr("requests.post", lambda *a, **k: FakeResponse())

    with pytest.raises(llm_client.LLMError, match="401"):
        llm_client.chat([{"role": "user", "content": "hi"}])


def test_chat_raises_on_network_error(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")
    import requests

    def raise_network_error(*a, **k):
        raise requests.RequestException("boom")

    monkeypatch.setattr("requests.post", raise_network_error)

    with pytest.raises(llm_client.LLMError, match="Couldn't reach"):
        llm_client.chat([{"role": "user", "content": "hi"}])
