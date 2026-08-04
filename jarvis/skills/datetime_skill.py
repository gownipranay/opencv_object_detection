"""Time and date."""
from __future__ import annotations

from datetime import datetime


def _time(match, ctx) -> str:
    now = datetime.now()
    return f"It's {now.strftime('%I:%M %p').lstrip('0')}."


def _date(match, ctx) -> str:
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."


def _day(match, ctx) -> str:
    now = datetime.now()
    return f"It's {now.strftime('%A')}."


def register(engine) -> None:
    engine.register(
        "time",
        r"\bwhat('?s| is) the time\b|\bwhat time is it\b|\btell me the time\b",
        _time,
        "'what time is it' - current time.",
    )
    engine.register(
        "day",
        r"\bwhat day is it\b|\bwhat('?s| is) today('?s)? day\b",
        _day,
        "'what day is it' - current weekday.",
    )
    engine.register(
        "date",
        r"\bwhat('?s| is) (the )?date\b|\btoday('?s)? date\b|\bwhat('?s| is) today\b",
        _date,
        "'what's the date' - today's date.",
    )
