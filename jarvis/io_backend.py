"""Speech/text input and output.

Three tiers, tried in order, no API keys involved anywhere:
  1. Termux:API (`termux-tts-speak` / `termux-speech-to-text`) when running
     on an Android phone inside Termux.
  2. `pyttsx3` for offline desktop text-to-speech, if it happens to be
     installed (optional, never required).
  3. Plain console print()/input() as the universal fallback.
"""
from __future__ import annotations

import shutil
import subprocess

_termux_tts_checked = False
_termux_tts = False
_termux_stt_checked = False
_termux_stt = False
_pyttsx3_engine = None
_pyttsx3_tried = False


def has_termux_tts() -> bool:
    global _termux_tts_checked, _termux_tts
    if not _termux_tts_checked:
        _termux_tts = shutil.which("termux-tts-speak") is not None
        _termux_tts_checked = True
    return _termux_tts


def has_termux_stt() -> bool:
    global _termux_stt_checked, _termux_stt
    if not _termux_stt_checked:
        _termux_stt = shutil.which("termux-speech-to-text") is not None
        _termux_stt_checked = True
    return _termux_stt


def _pyttsx3_speak(text: str) -> bool:
    global _pyttsx3_engine, _pyttsx3_tried
    if not _pyttsx3_tried:
        _pyttsx3_tried = True
        try:
            import pyttsx3

            _pyttsx3_engine = pyttsx3.init()
        except Exception:
            _pyttsx3_engine = None
    if _pyttsx3_engine is None:
        return False
    try:
        _pyttsx3_engine.say(text)
        _pyttsx3_engine.runAndWait()
        return True
    except Exception:
        return False


def speak(text: str, voice: bool = True) -> None:
    print(f"Jarvis: {text}")
    if not voice:
        return
    if has_termux_tts():
        try:
            subprocess.run(["termux-tts-speak", text], timeout=15, check=False)
            return
        except Exception:
            pass
    _pyttsx3_speak(text)


def listen(voice: bool = True, prompt: str = "You: ") -> str:
    if voice and has_termux_stt():
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            heard = result.stdout.strip()
            if heard:
                print(f"{prompt}{heard}")
                return heard
        except Exception:
            pass
    try:
        return input(prompt).strip()
    except EOFError:
        return "exit"
