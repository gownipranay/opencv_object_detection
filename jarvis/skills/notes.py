"""Notes: take a note, read notes back, delete/clear them. Stored as JSON."""
from __future__ import annotations

from datetime import datetime


def _get_notes(ctx) -> list:
    return ctx.storage.get("notes", [])


def _save_notes(ctx, notes: list) -> None:
    ctx.storage.set("notes", notes)


def _add(match, ctx) -> str:
    text = match.group("text").strip()
    if not text:
        return "What should the note say?"
    notes = _get_notes(ctx)
    note_id = (notes[-1]["id"] + 1) if notes else 1
    notes.append({"id": note_id, "text": text, "created": datetime.now().isoformat(timespec="seconds")})
    _save_notes(ctx, notes)
    return f"Noted (#{note_id})."


def _list(match, ctx) -> str:
    notes = _get_notes(ctx)
    if not notes:
        return "You don't have any notes."
    lines = [f"#{n['id']}: {n['text']}" for n in notes]
    return "Your notes:\n  - " + "\n  - ".join(lines)


def _delete(match, ctx) -> str:
    note_id = int(match.group("id"))
    notes = _get_notes(ctx)
    remaining = [n for n in notes if n["id"] != note_id]
    if len(remaining) == len(notes):
        return f"I don't have a note #{note_id}."
    _save_notes(ctx, remaining)
    return f"Deleted note #{note_id}."


def _clear(match, ctx) -> str:
    _save_notes(ctx, [])
    return "All notes cleared."


def register(engine) -> None:
    engine.register(
        "note_add",
        r"\b(take a note|make a note|add a note|remember)( that)?[:\s]+(?P<text>.+)",
        _add,
        "'take a note buy milk' - save a note.",
    )
    engine.register(
        "note_list",
        r"\b(read|list|show)( me)?( my)? notes\b",
        _list,
        "'read my notes' - list saved notes.",
    )
    engine.register(
        "note_delete",
        r"\bdelete note (?:number |#)?(?P<id>\d+)\b",
        _delete,
        "'delete note 2' - remove a note by number.",
    )
    engine.register(
        "note_clear",
        r"\bclear (all )?notes\b",
        _clear,
        "'clear notes' - delete every note.",
    )
