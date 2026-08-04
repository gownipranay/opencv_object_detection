"""Reminders and timers.

Both are stored as {id, text, due (ISO timestamp), fired} records in the
JSON storage. A background thread (started once from main.py) wakes up
every few seconds, checks which ones are due, and speaks them -- there is
no external scheduler, cron, or notification service involved.
"""
from __future__ import annotations

import re
import threading
import time as time_module
from datetime import datetime, timedelta

_UNIT_SECONDS = {
    "second": 1, "seconds": 1, "sec": 1, "secs": 1,
    "minute": 60, "minutes": 60, "min": 60, "mins": 60,
    "hour": 3600, "hours": 3600, "hr": 3600, "hrs": 3600,
}


def _get_reminders(ctx) -> list:
    return ctx.storage.get("reminders", [])


def _save_reminders(ctx, reminders: list) -> None:
    ctx.storage.set("reminders", reminders)


def _next_id(reminders: list) -> int:
    return (max((r["id"] for r in reminders), default=0)) + 1


def _parse_clock_time(hour_str: str, minute_str: str, meridiem: str) -> datetime:
    hour = int(hour_str)
    minute = int(minute_str) if minute_str else 0
    if meridiem:
        meridiem = meridiem.lower().replace(".", "")
        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
    now = datetime.now()
    due = now.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
    if due <= now:
        due += timedelta(days=1)
    return due


def _add_reminder(ctx, text: str, due: datetime) -> dict:
    reminders = _get_reminders(ctx)
    entry = {
        "id": _next_id(reminders),
        "text": text.strip() or "Reminder",
        "due": due.isoformat(timespec="seconds"),
        "fired": False,
    }
    reminders.append(entry)
    _save_reminders(ctx, reminders)
    return entry


def _remind_at_clock(match, ctx) -> str:
    text = match.group("text")
    due = _parse_clock_time(match.group("hour"), match.group("minute"), match.group("meridiem"))
    entry = _add_reminder(ctx, text, due)
    return f"Okay, I'll remind you to {entry['text']} at {due.strftime('%I:%M %p').lstrip('0')} (#{entry['id']})."


def _remind_in_relative(match, ctx) -> str:
    text = match.group("text")
    amount = int(match.group("amount"))
    unit = match.group("unit").lower()
    seconds = amount * _UNIT_SECONDS.get(unit, 60)
    due = datetime.now() + timedelta(seconds=seconds)
    entry = _add_reminder(ctx, text, due)
    return f"Okay, I'll remind you to {entry['text']} in {amount} {unit} (#{entry['id']})."


def _timer(match, ctx) -> str:
    amount = int(match.group("amount"))
    unit = match.group("unit").lower()
    seconds = amount * _UNIT_SECONDS.get(unit, 60)
    due = datetime.now() + timedelta(seconds=seconds)
    entry = _add_reminder(ctx, f"Timer for {amount} {unit}", due)
    return f"Timer set for {amount} {unit} (#{entry['id']})."


def _list_reminders(match, ctx) -> str:
    reminders = [r for r in _get_reminders(ctx) if not r["fired"]]
    if not reminders:
        return "You have no pending reminders."
    lines = []
    for r in reminders:
        due = datetime.fromisoformat(r["due"])
        lines.append(f"#{r['id']}: {r['text']} at {due.strftime('%I:%M %p on %b %d').lstrip('0')}")
    return "Pending reminders:\n  - " + "\n  - ".join(lines)


def _cancel_reminder(match, ctx) -> str:
    reminder_id = int(match.group("id"))
    reminders = _get_reminders(ctx)
    remaining = [r for r in reminders if r["id"] != reminder_id]
    if len(remaining) == len(reminders):
        return f"I don't have a reminder #{reminder_id}."
    _save_reminders(ctx, remaining)
    return f"Cancelled reminder #{reminder_id}."


def register(engine) -> None:
    engine.register(
        "reminder_at_clock",
        r"\bremind me to (?P<text>.+?) at (?P<hour>\d{1,2})(:(?P<minute>\d{2}))?\s*(?P<meridiem>am|pm|a\.m\.|p\.m\.)?\s*$",
        _remind_at_clock,
        "'remind me to call mom at 6pm' - reminder at a clock time.",
    )
    engine.register(
        "reminder_relative",
        r"\bremind me to (?P<text>.+?) in (?P<amount>\d+)\s*(?P<unit>seconds?|secs?|minutes?|mins?|hours?|hrs?)\b",
        _remind_in_relative,
        "'remind me to check the oven in 20 minutes' - relative reminder.",
    )
    engine.register(
        "timer",
        r"\bset (a |an )?timer for (?P<amount>\d+)\s*(?P<unit>seconds?|secs?|minutes?|mins?|hours?|hrs?)\b",
        _timer,
        "'set a timer for 10 minutes' - countdown timer.",
    )
    engine.register(
        "reminder_list",
        r"\b(list|show) (my )?(reminders|timers)\b",
        _list_reminders,
        "'list reminders' - see everything pending.",
    )
    engine.register(
        "reminder_cancel",
        r"\bcancel reminder (?:number |#)?(?P<id>\d+)\b",
        _cancel_reminder,
        "'cancel reminder 3' - remove a pending reminder or timer.",
    )


def fire_due(ctx) -> list[dict]:
    """Speak and mark-fired any reminder/timer whose due time has passed.

    Returns the list of entries that were fired, so this can be unit
    tested without waiting on the real clock or a background thread.
    """
    reminders = _get_reminders(ctx)
    now = datetime.now()
    fired = []
    for r in reminders:
        if r["fired"]:
            continue
        if datetime.fromisoformat(r["due"]) <= now:
            ctx.speak(f"Reminder: {r['text']}")
            r["fired"] = True
            fired.append(r)
    if fired:
        _save_reminders(ctx, reminders)
    return fired


def start_scheduler(ctx, poll_seconds: float = 15.0) -> threading.Thread:
    """Start a daemon thread that fires due reminders/timers. Returns the thread."""

    def _loop():
        while not ctx.stop_event.requested:
            fire_due(ctx)
            time_module.sleep(poll_seconds)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread
