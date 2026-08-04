"""Phone hardware control via the Termux:API app.

Every function here shells out to a `termux-*` command (part of the free,
open-source Termux:API add-on) and fails gracefully with a plain-English
message when that command isn't available -- e.g. when Jarvis is run on a
regular desktop for testing. No network access, no API keys.
"""
from __future__ import annotations

import json
import shutil
import subprocess

_TERMUX_HINT = (
    " (this needs the Termux:API app installed alongside Termux, plus "
    "`pkg install termux-api`)"
)


def _run(cmd: list[str], timeout: float = 10.0):
    if shutil.which(cmd[0]) is None:
        return None, f"'{cmd[0]}' isn't available on this device.{_TERMUX_HINT}"
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return result.stdout.strip(), None
    except Exception as exc:
        return None, f"Couldn't run '{cmd[0]}': {exc}"


def _get_contact(ctx, name: str) -> str:
    contacts = ctx.storage.get("contacts", {})
    return contacts.get(name.strip().lower(), name.strip())


def _battery(match, ctx) -> str:
    out, err = _run(["termux-battery-status"])
    if err:
        return f"I can't check the battery right now. {err}"
    try:
        info = json.loads(out)
    except (json.JSONDecodeError, TypeError):
        return "I couldn't read the battery status."
    pct = info.get("percentage", "unknown")
    status = info.get("status", "").lower()
    return f"Battery is at {pct} percent{', and charging' if status == 'charging' else ''}."


def _torch(match, ctx) -> str:
    state = "on" if match.group("state").lower() in ("on", "turn on") else "off"
    out, err = _run(["termux-torch", state])
    if err:
        return f"I couldn't control the flashlight. {err}"
    return f"Flashlight turned {state}."


def _volume(match, ctx) -> str:
    action = match.group("action").lower()
    out, err = _run(["termux-volume", "music"])
    if err:
        return f"I couldn't read the volume. {err}"
    try:
        info = json.loads(out)
        current, maximum = info["volume"], info["max_volume"]
    except Exception:
        return "I couldn't read the current volume."
    if "up" in action or "increase" in action:
        target = min(maximum, current + 2)
    elif "mute" in action:
        target = 0
    else:
        target = max(0, current - 2)
    _run(["termux-volume", "music", str(target)])
    return f"Volume set to {target} out of {maximum}."


def _wifi(match, ctx) -> str:
    state = "true" if "on" in match.group("state").lower() else "false"
    out, err = _run(["termux-wifi-enable", state])
    if err:
        return f"I couldn't change wifi. {err}"
    return f"Wifi turned {'on' if state == 'true' else 'off'} (Android may ask you to confirm)."


def _call(match, ctx) -> str:
    target = _get_contact(ctx, match.group("who"))
    out, err = _run(["termux-telephony-call", target])
    if err:
        return f"I couldn't place the call. {err}"
    return f"Calling {target}."


def _sms(match, ctx) -> str:
    target = _get_contact(ctx, match.group("who"))
    message = match.group("message").strip()
    out, err = _run(["termux-sms-send", "-n", target, message])
    if err:
        return f"I couldn't send the text. {err}"
    return f"Sent to {target}: \"{message}\""


def _save_contact(match, ctx) -> str:
    contacts = ctx.storage.get("contacts", {})
    name = match.group("name").strip().lower()
    number = match.group("number").strip()
    contacts[name] = number
    ctx.storage.set("contacts", contacts)
    return f"Saved contact {name} as {number}."


def register(engine) -> None:
    engine.register(
        "battery",
        r"\b(battery|how('?s| is) (my )?battery)\b",
        _battery,
        "'battery status' - check charge level (needs Termux:API).",
    )
    engine.register(
        "torch",
        r"\bturn (?P<state>on|off) (the )?(flashlight|torch)\b",
        _torch,
        "'turn on the flashlight' - toggle the torch (needs Termux:API).",
    )
    engine.register(
        "volume",
        r"\b(?P<action>turn up|turn down|increase|decrease|lower|raise|mute)( the)? volume\b",
        _volume,
        "'turn up the volume' - adjust media volume (needs Termux:API).",
    )
    engine.register(
        "wifi",
        r"\bturn (?P<state>on|off) (the )?wifi\b",
        _wifi,
        "'turn on wifi' - toggle wifi (needs Termux:API, may need manual confirm).",
    )
    engine.register(
        "save_contact",
        r"\bsave contact (?P<name>[a-zA-Z ]+?) as (?P<number>[\d+\-\s]+)$",
        _save_contact,
        "'save contact mom as +1234567890' - remember a phone number.",
    )
    engine.register(
        "call",
        r"\bcall (?P<who>.+)$",
        _call,
        "'call mom' - place a phone call (needs Termux:API).",
    )
    engine.register(
        "sms",
        r"\b(send|text) (?P<who>[a-zA-Z0-9 ]+?) (?:a text |a message )?saying (?P<message>.+)$",
        _sms,
        "'text mom saying I'll be late' - send an SMS (needs Termux:API).",
    )
