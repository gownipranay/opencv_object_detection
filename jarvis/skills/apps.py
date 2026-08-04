"""Launching apps and opening URLs.

Web search/open-website only ever *constructs a URL* from your words and
hands it to `termux-open-url`, which asks Android to open it in your
default browser -- Jarvis itself never makes a network request or calls
any search/API service.

Opening an app by name uses Android's `monkey` launcher trick
(`monkey -p <package> -c android.intent.category.LAUNCHER 1`), a
well-known Termux technique that starts an app's launcher activity from
just its package name, no root required.
"""
from __future__ import annotations

import shutil
import subprocess
import urllib.parse

_KNOWN_APPS = {
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "gmail": "com.google.android.gm",
    "maps": "com.google.android.apps.maps",
    "google maps": "com.google.android.apps.maps",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
    "spotify": "com.spotify.music",
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "gallery": "com.google.android.apps.photos",
    "photos": "com.google.android.apps.photos",
}


def _package_for(ctx, name: str) -> str | None:
    name = name.strip().lower()
    custom = ctx.storage.get("app_packages", {})
    if name in custom:
        return custom[name]
    return _KNOWN_APPS.get(name)


def _open_app(match, ctx) -> str:
    name = match.group("name").strip()
    package = _package_for(ctx, name)
    if not package:
        return (
            f"I don't know the app '{name}' yet. Teach me with "
            f"'remember app {name} as <package.name>'."
        )
    if shutil.which("am") is None:
        return f"I'd open {name}, but the 'am' command isn't available here."
    try:
        subprocess.run(
            ["am", "start", "-n", f"{package}/{package}.MainActivity"],
            capture_output=True, timeout=10, check=False,
        )
        subprocess.run(
            ["monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"],
            capture_output=True, timeout=10, check=False,
        )
    except Exception as exc:
        return f"I couldn't open {name}: {exc}"
    return f"Opening {name}."


def _remember_app(match, ctx) -> str:
    name = match.group("name").strip().lower()
    package = match.group("package").strip()
    custom = ctx.storage.get("app_packages", {})
    custom[name] = package
    ctx.storage.set("app_packages", custom)
    return f"Got it, I'll open {package} for '{name}'."


def _open_url(url: str) -> str:
    if shutil.which("termux-open-url"):
        subprocess.run(["termux-open-url", url], capture_output=True, timeout=10, check=False)
        return f"Opening {url} in your browser."
    if shutil.which("termux-open"):
        subprocess.run(["termux-open", url], capture_output=True, timeout=10, check=False)
        return f"Opening {url} in your browser."
    return f"I'd open this in your browser: {url}"


def _open_website(match, ctx) -> str:
    site = match.group("site").strip()
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    return _open_url(site)


def _web_search(match, ctx) -> str:
    query = match.group("query").strip()
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    return _open_url(url)


def register(engine) -> None:
    engine.register(
        "remember_app",
        r"\bremember app (?P<name>[a-zA-Z0-9 ]+?) as (?P<package>[\w.]+)$",
        _remember_app,
        "'remember app spotify as com.spotify.music' - teach me a new app.",
    )
    engine.register(
        "web_search",
        r"\b(search( the web)?|google) for (?P<query>.+)$",
        _web_search,
        "'search for pizza near me' - google search opened in your browser.",
    )
    engine.register(
        "open_website",
        r"\bopen (website\s+)?(?P<site>[\w.-]+\.[a-z]{2,})\b",
        _open_website,
        "'open wikipedia.org' - open a website in your browser.",
    )
    engine.register(
        "open_app",
        r"\bopen (?P<name>.+?)$",
        _open_app,
        "'open whatsapp' - launch an app (needs Termux, no root).",
    )
