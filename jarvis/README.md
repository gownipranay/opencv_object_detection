# Jarvis - a phone assistant: rule-based actions + free NVIDIA AI chat

A "Jarvis"-style assistant for your phone. It's built in two layers:

- **Phone actions run on a local, deterministic rule engine** — calls,
  texts, notes, reminders/timers, flashlight, volume, opening apps, camera
  object detection. Every one of these is matched against a hand-written
  regular expression and handled by a small Python function you can read
  in `jarvis/skills/`. **No API key needed, fully offline**, and no model
  can ever "decide" to send a text you didn't ask for.
- **Everything else — real questions, conversation, help writing
  something — is answered by a real language model** over NVIDIA's free
  [NIM API](https://build.nvidia.com/), so it actually feels like an AI
  assistant day to day, not just a command list.

## About the API key you shared

It was **not** hardcoded or committed anywhere in this repo — putting a
real key in git permanently exposes it in history the moment this is
pushed to GitHub. Instead, the key is read at runtime from an environment
variable or a file in your home directory (`~/.jarvis/nvidia_api_key`),
both **outside** the repo, so it can never accidentally end up in a commit.
Set it up once on your phone (below) and it stays there.

If that key was ever pasted anywhere public (chat logs, screenshots,
etc.) beyond this one setup step, rotate it at
[build.nvidia.com](https://build.nvidia.com/) — API keys should be treated
like passwords.

## What it can do

**Local, rule-based (no API key):**
- Tell the time, day, and date
- Do arithmetic ("what is 9 plus 10", "calculate 12 * (3 + 4)")
- Convert units (km/miles, kg/lbs, celsius/fahrenheit, meters/feet)
- Take, list, and delete notes
- Set reminders ("remind me to call mom at 6pm" / "...in 20 minutes") and timers
- Check battery status, toggle the flashlight/volume/wifi
- Save contacts and place calls / send texts by name
- Open apps and websites, or run a Google search in your browser
- Look through the camera and say what it recognizes, reusing this repo's
  own MobileNetSSD object detector (see the root `README.md` for the model
  files)

**AI chat (needs `NVIDIA_API_KEY`):**
- Anything that isn't one of the commands above — general knowledge,
  explanations, advice, drafting a message, casual conversation — is sent
  to NVIDIA's API and answered by a real model, with the last few turns of
  conversation kept as context.
- `ai status` tells you whether it's currently on.

`help` lists every built-in command, `exit`/`quit`/`bye` stops Jarvis.
Everything local is stored in `~/.jarvis/memory.json` (notes, reminders,
saved contacts, taught app names) — nothing here leaves your device.

## Setting up on your phone (Termux) — for daily use

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
   pip install -r jarvis/requirements.txt
   ```
3. Set your NVIDIA API key **once** so it's there every time you open
   Termux (this writes it to Termux's own shell startup file, not the
   repo):
   ```sh
   echo 'export NVIDIA_API_KEY="paste-your-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```
   Prefer not to touch your shell config? A single file works too, and
   Jarvis checks it automatically:
   ```sh
   mkdir -p ~/.jarvis
   echo "paste-your-key-here" > ~/.jarvis/nvidia_api_key
   ```
4. Run it:
   ```sh
   python -m jarvis
   ```
   Type commands and press enter. Add `--voice` to speak to it and have it
   talk back using Termux:API's speech-to-text/text-to-speech, for a real
   "hands-free assistant" feel:
   ```sh
   python -m jarvis --voice
   ```
5. (Optional, for the camera skill) Download `MobileNetSSD_deploy.prototxt`
   and `MobileNetSSD_deploy.caffemodel` into the repo root as described in
   the main `README.md`, then say "what do you see".

Grant Termux and Termux:API the Camera, Microphone, and SMS/Phone
permissions Android asks for the first time each feature is used
(Android Settings -> Apps -> Termux / Termux:API -> Permissions).

For quick daily access, add a Termux widget (Termux:Widget app, also on
F-Droid) with a shortcut script that runs `python -m jarvis --voice`, or
just pin the Termux app itself to your home screen.

### Which model / any cost?

Jarvis defaults to `meta/llama-3.1-8b-instruct`, a fast model on NVIDIA's
free NIM catalog. Override it with:
```sh
export NVIDIA_MODEL="meta/llama-3.3-70b-instruct"   # e.g. a larger model
```
Check your usage/limits and browse other available models at
[build.nvidia.com](https://build.nvidia.com/). If a model name stops
working (deprecated/renamed), just point `NVIDIA_MODEL` at a current one
from that catalog.

## Running it anywhere else (for development/testing)

Jarvis works on a regular PC too — it just falls back to typed input,
console output, and (if installed) `pyttsx3` for offline text-to-speech
instead of Termux:API. Phone-only features (battery, flashlight, calls,
SMS, camera capture) print a clear "needs Termux:API" message instead of
crashing, and without `NVIDIA_API_KEY` set, AI chat just tells you how to
turn it on — nothing crashes either way.

```sh
pip install -r reuirements.txt -r jarvis/requirements.txt
python -m jarvis
```

## Teaching it new things

Two commands are extensible without touching code:

- `remember app <name> as <package.name>` — teach Jarvis a package name so
  `open <name>` can launch it (find a package name by searching
  "`<app name>` android package name").
- `save contact <name> as <number>` — so `call <name>` / `text <name>
  saying ...` know who you mean.

To add an entirely new *local* command, add a new `engine.register(...)`
call in the relevant file under `jarvis/skills/` (or a new skill module,
then list it in `jarvis/skills/__init__.py` — just keep `ai_chat` last,
since its rule matches anything). Each rule is just a regex plus a
function — no framework, no training data required for these.

## Running the tests

```sh
pip install pytest requests
python -m pytest jarvis/tests -q
```
No test makes a real network call — the AI chat tests mock
`llm_client.chat`/`requests.post`, so they run the same with or without a
key configured.

## Architecture

```
jarvis/
  engine.py       regex rule matcher (the local "brain")
  llm_client.py   NVIDIA NIM API client (used only by skills/ai_chat.py)
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
    ai_chat.py             catch-all: anything unmatched -> NVIDIA API (must stay last)
```

Rule skills are tried in the order listed above; the first regex match
wins. `ai_chat` is deliberately registered last, so it only ever answers
what nothing else understood.
