"""Shared state handed to every skill handler."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .storage import Storage


class StopEvent:
    """Mutable flag a handler can set to end the conversation loop."""

    def __init__(self) -> None:
        self.requested = False


@dataclass
class Context:
    storage: Storage
    speak: Callable[[str], None]
    stop_event: StopEvent = field(default_factory=StopEvent)
