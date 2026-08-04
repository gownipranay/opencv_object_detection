"""All Jarvis skills. Each module exposes register(engine)."""
from . import smalltalk
from . import datetime_skill
from . import calculator
from . import notes
from . import reminders
from . import device
from . import apps
from . import vision

SKILLS = [
    smalltalk,
    datetime_skill,
    calculator,
    notes,
    reminders,
    device,
    apps,
    vision,
]


def register_all(engine) -> None:
    for skill in SKILLS:
        skill.register(engine)
