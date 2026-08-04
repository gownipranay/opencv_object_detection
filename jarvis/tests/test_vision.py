import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.context import Context
from jarvis.engine import Engine
from jarvis.skills import vision
from jarvis.storage import Storage


def make_ctx(tmp_path):
    return Context(storage=Storage(tmp_path / "memory.json"), speak=lambda t: None)


def test_vision_without_model_files_gives_helpful_message(tmp_path):
    # The model files are ~23MB and intentionally not committed to the repo
    # (per the main README, users download them separately), so this skill
    # must degrade gracefully rather than crash.
    assert not vision._PROTOTXT.exists()
    assert not vision._MODEL.exists()

    engine = Engine()
    vision.register(engine)
    ctx = make_ctx(tmp_path)
    response = engine.handle("what do you see", ctx)
    assert "download" in response.lower()
