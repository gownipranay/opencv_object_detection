# Jarvis - a rule-based, offline phone assistant

A "Jarvis"-style assistant that runs entirely on your phone with **no cloud
APIs, no API keys, and no machine learning models** for its language
understanding. Every command is matched against a hand-written regular
expression and handled by a small Python function — you can read every
"decision" it will ever make by opening the files in `jarvis/skills/`.

> **A note on API keys:** if you shared an API key with the assistant that
> built this, it was deliberately **not** used or committed anywhere in this
> project — this whole point of Jarvis is to work with zero external
> services. Because that key was pasted in plain text, treat it as
> compromised and rotate/revoke it with its provider.

## What it can do

- Tell the time, day, and date
- Do arithmetic ("what is 9 plus 10", "calculate 12 * (3 + 4)")
- Convert units (km/miles, kg/lbs, celsius/fahrenheit, meters/feet)
- Take, list, and delete notes
- Set reminders ("remind me to call mom at 6pm" / "...in 20 minutes")
- Set countdown timers
- Check battery status, toggle the flashlight/volume/wifi
- Save contacts and place calls / send texts by name
- Open apps and websites, or run a Google search in your browser
- Look through the camera and say what it recognizes, reusing this repo's
  own MobileNetSSD object detector (see the root `README.md` for the model
  files)
- `help` to list every command it understands, `exit`/`quit`/`bye` to stop

All of this is stored locally in `~/.jarvis/memory.json` (notes, reminders,
saved contacts, taught app names) — nothing leaves your device.

## Running it on your phone (Termux)

1. Install [Termux](https://f-droid.org/packages/com.termux/) and
   [Termux:API](https://f-droid.org/packages/com.termux.api/) from F-Droid
   (the Play Store builds of Termux are outdated and often broken — use
   F-Droid). Termux:API is what lets Jarvis touch the phone's battery,
   flashlight, microphone/speaker, camera, calls, and SMS.
2. In Termux:
   ```sh
   pkg update && pkg upgrade
   pkg install python opencv termux-api git
   git clone <this-repo-url>
   cd opencv_object_detection
   pip install -r reuirements.txt
   ```
3. Run it:
   ```sh
   python -m jarvis
   ```
   Type commands and press enter. Add `--voice` to speak to it and have it
   talk back using Termux:API's speech-to-text/text-to-speech:
   ```sh
   python -m jarvis --voice
   ```
4. (Optional, for the camera skill) Download `MobileNetSSD_deploy.prototxt`
   and `MobileNetSSD_deploy.caffemodel` into the repo root as described in
   the main `README.md`, then say "what do you see".

Grant Termux and Termux:API the Camera, Microphone, and SMS/Phone
permissions Android asks for the first time each feature is used
(Android Settings -> Apps -> Termux / Termux:API -> Permissions).

## Running it anywhere else (for development/testing)

Jarvis works on a regular PC too — it just falls back to typed input,
console output, and (if installed) `pyttsx3` for offline text-to-speech
instead of Termux:API. Phone-only features (battery, flashlight, calls,
SMS, camera capture) print a clear "needs Termux:API" message instead of
crashing.

```sh
pip install -r reuirements.txt
python -m jarvis
```

## Teaching it new things

Two commands are extensible without touching code:

- `remember app <name> as <package.name>` — teach Jarvis a package name so
  `open <name>` can launch it (find a package name by searching
  "`<app name>` android package name").
- `save contact <name> as <number>` — so `call <name>` / `text <name>
  saying ...` know who you mean.

To add an entirely new command, add a new `engine.register(...)` call in
the relevant file under `jarvis/skills/` (or a new skill module, then list
it in `jarvis/skills/__init__.py`). Each rule is just a regex plus a
function — no framework, no training data.

## Running the tests

```sh
pip install pytest
python -m pytest jarvis/tests -q
```

## Architecture

```
jarvis/
  engine.py       regex rule matcher (the whole "brain")
  storage.py      JSON file persistence (~/.jarvis/memory.json)
  context.py      per-session state passed to every skill handler
  io_backend.py   speak()/listen() -> Termux:API, else pyttsx3, else console
  main.py         REPL loop / `python -m jarvis` entry point
  skills/
    smalltalk.py       greetings, identity, help, exit
    datetime_skill.py  time, date, day
    calculator.py      safe arithmetic (ast-based, no eval()) + unit conversion
    notes.py            notes CRUD
    reminders.py        reminders + timers + background firing thread
    device.py            battery/flashlight/volume/wifi/calls/SMS via Termux:API
    apps.py               open apps, open websites, web search (URL construction only)
    vision.py             camera + this repo's MobileNetSSD detector
```
