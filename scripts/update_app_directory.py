#!/usr/bin/env python3
"""Build the open source watchface and watchapp directories.

Sources of entries:
  1. The Pebble App Store API: every watchface/watchapp whose developer has
     published a source code link.
  2. data/manual-apps.yml: open source apps added by hand (apps that aren't
     in the store, or don't list their source there).

What it keeps between runs (committed to the repo):
  - data/store-apps.json: every store app ever seen. Apps that disappear from
    the store are kept and shown with a link to their source only.
  - docs/images/apps/: a copy of each app's screenshot, so the directory
    doesn't depend on the store's image hosting.

What it writes:
  - docs/watchfaces/<letter>.md and docs/watchapps/<letter>.md: one page per
    letter, manual and store entries merged in alphabetical order.
  - The letter index between the GENERATED markers in docs/watchfaces.md and
    docs/watchapps.md. Everything outside the markers is left alone.

Usage:
    python3 scripts/update_app_directory.py                 # normal run
    python3 scripts/update_app_directory.py --offline       # rebuild pages from saved data only
    python3 scripts/update_app_directory.py --fixture F     # test with saved API JSON, no downloads
"""

import argparse
import concurrent.futures
import datetime
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml  # installed with mkdocs

API = "https://appstore-api.repebble.com/api/v1/apps/collection/all/{kind}"
STORE_URL = "https://apps.repebble.com/{id}"
PREFERRED_PLATFORM = "emery"  # Pebble Time 2

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"
STORE_DB = DATA / "store-apps.json"
MANUAL = DATA / "manual-apps.yml"
IMAGES = DOCS / "images" / "apps"

TYPES = {
    # type: (API kind string, page label, index page, letter page folder)
    "watchface": ("watchfaces", "watchfaces", DOCS / "watchfaces.md", DOCS / "watchfaces"),
    "watchapp": ("watchapps-and-companions", "watchapps", DOCS / "watchapps.md", DOCS / "watchapps"),
}
BEGIN = "<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->"
END = "<!-- END GENERATED -->"

CODE_HOSTS = {
    "github.com", "gist.github.com", "gitlab.com", "codeberg.org",
    "bitbucket.org", "git.sr.ht", "hg.sr.ht", "sourceforge.net",
    "cloudpebble.net", "notabug.org", "framagit.org", "gitgud.io",
}
FORGE_HINTS = ("git", "hg.", "mercurial", "forge", "gitea", "sr.ht", "svn")
LETTERS = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["other"]


# ---------------------------------------------------------------- fetching

def http_get(url, binary=False):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "all-things-pebble"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read() if binary else json.load(r)
        except Exception as e:
            if attempt == 4:
                raise
            print(f"retrying {url}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)


def fetch_store(kind):
    apps, offset = [], 0
    while True:
        query = urllib.parse.urlencode({"hardware": PREFERRED_PLATFORM, "source": "available",
                                        "limit": 100, "offset": offset})
        data = http_get(API.format(kind=kind) + "?" + query)["data"]
        apps.extend(data)
        if len(data) < 100:
            return apps
        offset += 100


# ---------------------------------------------------------------- cleaning

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
    host = (u.hostname or "").lower().removeprefix("www.")
    parts = [p for p in u.path.split("/") if p]
    if host in ("github.com", "gitlab.com", "codeberg.org", "bitbucket.org"):
        if len(parts) < 2:  # a user profile rather than a repository
            return None
    elif host not in CODE_HOSTS and not any(h in host for h in FORGE_HINTS):
        return None
    return src


def store_screenshot(app):
    for hp in app.get("hardware_platforms") or []:
        if hp.get("name") == PREFERRED_PLATFORM and (hp.get("images") or {}).get("screenshot"):
            return hp["images"]["screenshot"]
    for img in app.get("screenshot_images") or []:
        for url in img.values():
            if url:
                return url
    return None


def store_description(app):
    texts = [hp.get("description") for hp in app.get("hardware_platforms") or []
             if hp.get("name") == PREFERRED_PLATFORM]
    texts += [app.get("description")]
    texts += [hp.get("description") for hp in app.get("hardware_platforms") or []]
    return next((t for t in texts if t and t.strip()), "")


def short(text, limit=160):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) > limit:
        text = text[:limit - 3].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"
    return text


def md_escape(text):
    text = (text or "").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace("[", "\\[").replace("]", "\\]")


def letter_of(title):
    c = title.strip()[:1].upper()
    return c if "A" <= c <= "Z" else "other"


def letter_label(letter):
    return "0–9 & other" if letter == "other" else letter


# ---------------------------------------------------------------- data

def load_db():
    if STORE_DB.exists():
        return json.loads(STORE_DB.read_text(encoding="utf-8"))
    return {}


def save_db(db):
    DATA.mkdir(exist_ok=True)
    ordered = dict(sorted(db.items(), key=lambda kv: (kv[1]["type"], kv[1]["title"].lower(), kv[0])))
    STORE_DB.write_text(json.dumps(ordered, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def merge_store(db, raw_apps, app_type, today):
    """Update the saved store data with a fresh API listing."""
    seen = set()
    for a in raw_apps:
        if a.get("type") != app_type or a.get("visible") is False:
            continue
        src = normalise_source(a.get("source"))
        if not src:
            continue
        seen.add(a["id"])
        old = db.get(a["id"], {})
        db[a["id"]] = {
            "id": a["id"], "type": app_type,
            "title": (a.get("title") or "").strip() or "Untitled",
            "author": (a.get("author") or "").strip(),
            "source": src,
            "description": short(store_description(a), 400),
            "screenshot_url": store_screenshot(a),
            "screenshot": old.get("screenshot") if old.get("screenshot_url") == store_screenshot(a) else None,
            "in_store": True,
            "first_seen": old.get("first_seen", today),
            "last_seen": today,
        }
    # Apps that have left the store (or stopped listing their source) stay in
    # the directory, linking to their source code only. If the API returned
    # nothing at all, assume it's broken rather than that every app is gone.
    if not seen:
        sys.exit(f"The store returned no {app_type}s with source code; not updating.")
    for app_id, rec in db.items():
        if rec["type"] == app_type and app_id not in seen:
            rec["in_store"] = False
    return db


def download_screenshots(db):
    """Copy any screenshots we don't have yet into docs/images/apps/."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    todo = [r for r in db.values() if r.get("screenshot_url") and not (
        r.get("screenshot") and (DOCS / r["screenshot"]).exists())]

    def fetch(rec):
        url = rec["screenshot_url"]
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".png"
        if ext not in (".png", ".gif", ".jpg", ".jpeg", ".webp"):
            ext = ".png"
        path = IMAGES / f"{rec['id']}{ext}"
        try:
            path.write_bytes(http_get(url, binary=True))
            rec["screenshot"] = path.relative_to(DOCS).as_posix()
        except Exception as e:
            print(f"screenshot failed for {rec['title']}: {e}", file=sys.stderr)

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(fetch, todo))
    print(f"downloaded {len(todo)} screenshots")


def load_manual():
    if not MANUAL.exists():
        return []
    entries = yaml.safe_load(MANUAL.read_text(encoding="utf-8")) or []
    out = []
    for i, e in enumerate(entries):
        missing = [k for k in ("type", "title", "source") if not e.get(k)]
        if missing or e["type"] not in TYPES:
            sys.exit(f"{MANUAL.name} entry {i + 1}: needs type (watchface/watchapp), title and source")
        out.append(e)
    return out


# ---------------------------------------------------------------- rendering

def entries_for(app_type, db, manual):
    """Merge store and manual entries for one type. Manual entries override
    store data for the same app (matched by store ID in the store URL)."""
    entries = {}
    for rec in db.values():
        if rec["type"] != app_type:
            continue
        entries[rec["id"]] = {
            "title": rec["title"], "author": rec["author"], "source": rec["source"],
            "description": rec["description"], "screenshot": rec.get("screenshot"),
            "store": STORE_URL.format(id=rec["id"]) if rec["in_store"] else None,
            "removed": not rec["in_store"],
        }
    for m in manual:
        if m["type"] != app_type:
            continue
        ids = re.findall(r"[0-9a-f]{24}", m.get("store") or "")
        key = ids[0] if ids else "manual:" + m["title"]
        base = entries.get(key, {})
        entries[key] = {
            "title": m["title"], "author": m.get("author") or base.get("author", ""),
            "source": m["source"],
            "description": m.get("description") or base.get("description", ""),
            "screenshot": m.get("screenshot") or base.get("screenshot"),
            "store": m.get("store") or base.get("store"),
            "removed": False,
        }
    return sorted(entries.values(), key=lambda e: (e["title"].lower(), e["author"].lower()))


def render_row(e):
    shot = ""
    if e["screenshot"]:
        shot = f'![{md_escape(e["title"])}](../{e["screenshot"]}){{ loading=lazy width="72" }}'
    link = e["store"] or e["source"]
    name = f'[{md_escape(e["title"])}]({link})'
    if e["removed"]:
        name += "<br><small>No longer in the app store</small>"
    dev = f'[{md_escape(e["author"] or "Source code")}]({e["source"]})'
    return f"| {shot} | {name} | {dev} | {md_escape(short(e['description']))} |"


def letter_nav(by_letter, current=None):
    links = []
    for l in LETTERS:
        if l not in by_letter:
            continue
        label = letter_label(l) if l == "other" else l
        links.append(f"**{label}**" if l == current else f"[{label}]({l.lower()}.md)")
    return " · ".join(links)


def write_pages(app_type, entries, today):
    _, label, index_page, folder = TYPES[app_type]
    by_letter = {}
    for e in entries:
        by_letter.setdefault(letter_of(e["title"]), []).append(e)

    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.md"):
        old.unlink()
    title = label.capitalize()
    for l, items in by_letter.items():
        lines = [
            f"<!-- Generated by scripts/update_app_directory.py: do not edit by hand -->",
            f"# {title}: {letter_label(l)}", "",
            f"[← All {label}](../{index_page.name}) · {letter_nav(by_letter, l)}", "",
            "| Screenshot | Name | Developer | Description |",
            "|------------|------|-----------|-------------|",
            *[render_row(e) for e in items], "",
        ]
        (folder / f"{l.lower()}.md").write_text("\n".join(lines), encoding="utf-8")

    in_store = sum(1 for e in entries if e["store"])
    block = [
        BEGIN, "",
        f"**{len(entries)} open source {label}**, {in_store} of them in the "
        f"[Pebble App Store](https://apps.repebble.com/). Updated {today}.", "",
        "| Letter | Count |", "|--------|-------|",
        *[f"| [{letter_label(l)}]({folder.name}/{l.lower()}.md) | {len(by_letter[l])} |"
          for l in LETTERS if l in by_letter],
        "", END,
    ]
    text = index_page.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        text = text[:text.index(BEGIN)] + "\n".join(block) + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + "\n".join(block)
    index_page.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    print(f"{label}: {len(entries)} entries ({in_store} in store) on {len(by_letter)} pages")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="don't call the API; rebuild pages from saved data")
    ap.add_argument("--fixture", help="JSON file {'watchface': [...], 'watchapp': [...]} of raw API apps")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()

    db = load_db()
    manual = load_manual()
    if not args.offline:
        fixture = json.loads(Path(args.fixture).read_text()) if args.fixture else None
        for app_type, (kind, *_rest) in TYPES.items():
            raw = fixture[app_type] if fixture else fetch_store(kind)
            merge_store(db, raw, app_type, today)
        if not args.fixture:
            download_screenshots(db)
        save_db(db)

    for app_type in TYPES:
        write_pages(app_type, entries_for(app_type, db, manual), today)


if __name__ == "__main__":
    main()
