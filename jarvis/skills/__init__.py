"""All Jarvis skills. Each module exposes register(engine).

Order matters: the engine tries rules in registration order and the first
match wins, so specific/deterministic skills must come before the catch-all
AI chat skill. ai_chat MUST stay last -- its final rule matches any
non-empty input.
"""
from . import smalltalk
from . import datetime_skill
from . import calculator
from . import notes
from . import reminders
from . import device
from . import apps
from . import vision
from . import ai_chat

SKILLS = [
    smalltalk,
    datetime_skill,
    calculator,
    notes,
    reminders,
    device,
    apps,
    vision,
    ai_chat,  # must stay last: its rule matches ANY remaining input
]


def register_all(engine) -> None:
    for skill in SKILLS:
        skill.register(engine)
