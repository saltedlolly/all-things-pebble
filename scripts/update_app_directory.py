#!/usr/bin/env python3
"""Regenerate the open source watchface and watchapp directories.

Fetches every watchface and watchapp from the Pebble App Store API that has
a source code link, and writes them into docs/watchfaces.md and
docs/watchapps.md between the GENERATED markers. Everything outside the
markers (intro text, hand-added entries) is left alone.

Usage:
    python3 scripts/update_app_directory.py              # fetch from the API
    python3 scripts/update_app_directory.py --fixture f  # use a saved JSON file
"""

import argparse
import datetime
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://appstore-api.repebble.com/api/v1/apps/collection/all/{kind}"
STORE_URL = "https://apps.repebble.com/{id}"
PREFERRED_PLATFORM = "emery"  # Pebble Time 2

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "watchface": ("watchfaces", ROOT / "docs" / "watchfaces.md"),
    "watchapp": ("watchapps-and-companions", ROOT / "docs" / "watchapps.md"),
}
BEGIN = "<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->"
END = "<!-- END GENERATED -->"

# Hosts that are code hosting services. Any other host is accepted only if its
# name looks like a code forge (git., hg., gitea, forgejo...).
CODE_HOSTS = {
    "github.com", "gist.github.com", "gitlab.com", "codeberg.org",
    "bitbucket.org", "git.sr.ht", "hg.sr.ht", "sourceforge.net",
    "cloudpebble.net", "notabug.org", "framagit.org", "gitgud.io",
}
FORGE_HINTS = ("git", "hg.", "mercurial", "forge", "gitea", "sr.ht", "svn")


def fetch_all(kind):
    apps, offset = [], 0
    while True:
        query = urllib.parse.urlencode({
            "hardware": PREFERRED_PLATFORM, "source": "available",
            "limit": 100, "offset": offset,
        })
        url = API.format(kind=kind) + "?" + query
        for attempt in range(5):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "all-things-pebble"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)["data"]
                break
            except Exception as e:  # network hiccup: retry with backoff
                if attempt == 4:
                    raise
                print(f"retrying {url}: {e}", file=sys.stderr)
                time.sleep(2 ** attempt)
        apps.extend(data)
        if len(data) < 100:
            return apps
        offset += 100


def normalise_source(src):
    """Return a cleaned source URL, or None if it doesn't look like source code."""
    if not src or not isinstance(src, str):
        return None
    src = src.strip()
    if not re.match(r"^https?://", src):
        if re.match(r"^(www\.)?[a-z0-9.-]+\.[a-z]{2,}/", src, re.I):
            src = "https://" + src
        else:
            return None
    try:
        u = urllib.parse.urlparse(src)
    except ValueError:
        return None
    host = (u.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in u.path.split("/") if p]
    if host in ("github.com", "gitlab.com", "codeberg.org", "bitbucket.org"):
        if len(parts) < 2:  # a user profile rather than a repository
            return None
    elif host not in CODE_HOSTS and not any(h in host for h in FORGE_HINTS):
        return None
    return src


def screenshot(app):
    for hp in app.get("hardware_platforms") or []:
        if hp.get("name") == PREFERRED_PLATFORM:
            shot = (hp.get("images") or {}).get("screenshot")
            if shot:
                return shot
    for img in app.get("screenshot_images") or []:
        for url in img.values():
            if url:
                return url
    return None


def description(app):
    texts = [hp.get("description") for hp in app.get("hardware_platforms") or []
             if hp.get("name") == PREFERRED_PLATFORM]
    texts += [app.get("description")]
    texts += [hp.get("description") for hp in app.get("hardware_platforms") or []]
    text = next((t for t in texts if t and t.strip()), "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 160:
        text = text[:157].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"
    return md_escape(text)


def md_escape(text):
    text = (text or "").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace("[", "\\[").replace("]", "\\]")


def letter(title):
    c = title.strip()[:1].upper()
    return c if "A" <= c <= "Z" else "#"


def render(apps, kind_label):
    today = datetime.date.today().isoformat()
    lines = [
        BEGIN, "",
        f"*{len(apps)} open source {kind_label} from the "
        f"[Pebble App Store](https://apps.repebble.com/) with a published source code link. "
        f"Updated {today}. Screenshots are from the Pebble Time 2 where available.*",
        "",
    ]
    groups = {}
    for a in apps:
        groups.setdefault(letter(a["title"]), []).append(a)
    order = sorted(groups, key=lambda k: (k != "#", k))
    lines.append(" · ".join(f"[{k}](#{'other' if k == '#' else k.lower()})" for k in order))
    lines.append("")
    for k in order:
        lines += [f"## {'0-9 & other' if k == '#' else k} {{ #{'other' if k == '#' else k.lower()} }}", "",
                  "| Screenshot | Name | Developer | Description |",
                  "|------------|------|-----------|-------------|"]
        for a in sorted(groups[k], key=lambda a: a["title"].lower()):
            shot = f'![{md_escape(a["title"])}]({a["shot"]}){{ loading=lazy width="72" }}' if a["shot"] else ""
            name = f'[{md_escape(a["title"])}]({STORE_URL.format(id=a["id"])})'
            dev = f'[{md_escape(a["author"] or "Source")}]({a["source"]})'
            lines.append(f"| {shot} | {name} | {dev} | {a['desc']} |")
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def update_page(path, block):
    text = path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        text = text[:start] + block + text[end:]
    else:
        text = text.rstrip("\n") + "\n\n" + block
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", help="JSON file with {'watchface': [...], 'watchapp': [...]} raw API apps")
    args = ap.parse_args()
    fixture = json.loads(Path(args.fixture).read_text()) if args.fixture else None

    for app_type, (kind, path) in PAGES.items():
        raw = fixture[app_type] if fixture else fetch_all(kind)
        page_text = path.read_text(encoding="utf-8")
        outside = page_text.split(BEGIN)[0] + (page_text.split(END)[1] if END in page_text else "")
        manual_ids = set(re.findall(r"[0-9a-f]{24}", outside))
        seen, apps = set(), []
        for a in raw:
            if a.get("type") != app_type or a["id"] in seen or a["id"] in manual_ids:
                continue
            if a.get("visible") is False:
                continue
            src = normalise_source(a.get("source"))
            if not src:
                continue
            seen.add(a["id"])
            apps.append({
                "id": a["id"], "title": (a.get("title") or "").strip() or "Untitled",
                "author": (a.get("author") or "").strip(), "source": src,
                "shot": screenshot(a), "desc": description(a),
            })
        label = "watchfaces" if app_type == "watchface" else "watchapps"
        update_page(path, render(apps, label))
        print(f"{path.name}: {len(apps)} {label} (skipped {len(raw) - len(apps)})")


if __name__ == "__main__":
    main()
