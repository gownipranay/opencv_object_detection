"""Rule-based intent engine.

A "rule" is just a compiled regex plus a handler function. There is no
machine learning, no intent classifier, no external service involved:
user input is matched top-to-bottom against every registered rule and the
first one that matches wins. This is the entire "brain" of Jarvis.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Match

HandlerFn = Callable[[Match, "object"], str]


@dataclass
class Rule:
    name: str
    pattern: re.Pattern
    handler: HandlerFn
    help: str


class Engine:
    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def register(self, name: str, pattern: str, handler: HandlerFn, help_text: str = "") -> None:
        """Add a rule. Rules are tried in registration order, first match wins."""
        self._rules.append(Rule(name, re.compile(pattern, re.IGNORECASE), handler, help_text))

    def handle(self, text: str, ctx) -> str:
        text = (text or "").strip()
        if not text:
            return "I didn't catch that. Could you say it again?"

        for rule in self._rules:
            match = rule.pattern.search(text)
            if match:
                try:
                    return rule.handler(match, ctx)
                except Exception as exc:  # a broken skill shouldn't crash the assistant
                    return f"I ran into a problem with '{rule.name}': {exc}"

        return (
            "I don't have a rule for that yet. Say 'help' to see everything I "
            "understand."
        )

    def help_lines(self) -> List[str]:
        lines: List[str] = []
        seen = set()
        for rule in self._rules:
            if rule.help and rule.help not in seen:
                lines.append(rule.help)
                seen.add(rule.help)
        return lines
