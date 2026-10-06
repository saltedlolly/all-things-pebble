#!/usr/bin/env python3
"""Build the open source watchface and watchapp directories.

Where entries come from:
  1. The Pebble App Store (Core Devices): every watchface/watchapp whose
     developer has published a source code link.
  2. The Rebble App Store: any further open source apps that aren't in the
     Pebble App Store (or don't list their source there).
  3. data/manual-apps.yml: open source apps added by hand.

What it remembers between runs (committed to the repo):
  - data/store-apps.json: every open source store app ever seen. Apps that
    leave both stores stay listed, linking to their source code, for as long
    as that source code is still online.
  - docs/images/apps/: a copy of each app's screenshot, so the directory
    doesn't depend on the stores' image hosting.

What it writes:
  - docs/watchfaces/<letter>.md and docs/watchapps/<letter>.md: one page per
    letter, store and manual entries merged in alphabetical order.
  - The letter index between the GENERATED markers in docs/watchfaces.md and
    docs/watchapps.md. Everything outside the markers is left alone.

Usage:
    python3 scripts/update_app_directory.py              # normal run
    python3 scripts/update_app_directory.py --offline    # rebuild pages from saved data only
    python3 scripts/update_app_directory.py --fixture F  # test with saved API JSON (no network)
"""

import argparse
import concurrent.futures
import datetime
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml  # installed with mkdocs

PREFERRED_PLATFORM = "emery"  # Pebble Time 2: preferred screenshots and descriptions

# Stores, in order of preference. An app in both is linked to the first.
STORES = {
    "pebble": {
        "name": "Pebble App Store",
        "api": "https://appstore-api.repebble.com/api/v1/apps/collection/all/{kind}",
        # This API can filter to apps with source code, and lists every app
        # whatever hardware is asked for.
        "params": [{"hardware": PREFERRED_PLATFORM, "source": "available"}],
        "url": "https://apps.repebble.com/{id}",
    },
    "rebble": {
        "name": "Rebble App Store",
        "api": "https://appstore-api.rebble.io/api/v1/apps/collection/all/{kind}",
        # No source filter here, so every app is fetched and filtered below.
        # This API only lists apps that support the hardware asked for:
        # emery covers the rectangular watches, chalk the round ones, and
        # aplite catches any apps that only run on the original Pebble.
        "params": [{"hardware": hw} for hw in ("emery", "chalk", "aplite")],
        "url": "https://apps.rebble.io/en_US/application/{id}",
    },
}

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
HEADERS = {"User-Agent": "all-things-pebble (+https://allthingspebble.saltedlolly.com)"}


# ---------------------------------------------------------------- network

def http_get(url, binary=False):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
                return r.read() if binary else json.load(r)
        except Exception as e:
            if attempt == 4:
                raise
            print(f"retrying {url}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)


def fetch_store(store, kind):
    """All apps of one kind from a store, deduplicated by ID."""
    apps = {}
    for params in store["params"]:
        offset = 0
        while True:
            query = urllib.parse.urlencode({**params, "limit": 100, "offset": offset})
            data = http_get(store["api"].format(kind=kind) + "?" + query)["data"]
            for a in data:
                apps.setdefault(a["id"], a)
            if len(data) < 100:
                break
            offset += 100
    return list(apps.values())


def source_online(url):
    """True if the source URL still loads, False if it's gone (404/410),
    None if we couldn't tell (network trouble, rate limiting...)."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers=HEADERS, method=method)
            with urllib.request.urlopen(req, timeout=30):
                return True
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return False
            if e.code == 405 and method == "HEAD":
                continue  # server doesn't do HEAD: try GET
            return None
        except Exception:
            return None
    return None


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


def merge_store(db, store_key, raw_apps, app_type, today):
    """Update the saved data with one store's listing for one app type."""
    seen = set()
    for a in raw_apps:
        if a.get("type") != app_type or a.get("visible") is False:
            continue
        src = normalise_source(a.get("source"))
        if not src:
            continue
        seen.add(a["id"])
        rec = db.setdefault(a["id"], {"id": a["id"], "type": app_type, "stores": [], "first_seen": today})
        if store_key == "pebble" or "pebble" not in rec["stores"]:
            # The Pebble store's details win when an app is in both
            shot = store_screenshot(a)
            if shot != rec.get("screenshot_url"):
                rec["screenshot"] = None  # re-download
            rec.update({
                "title": (a.get("title") or "").strip() or "Untitled",
                "author": (a.get("author") or "").strip(),
                "source": src,
                "description": short(store_description(a), 400),
                "screenshot_url": shot,
            })
        if store_key not in rec["stores"]:
            rec["stores"].append(store_key)
        rec["last_seen"] = today
        rec["source_online"] = True
    # Forget this store for apps it no longer lists
    for rec in db.values():
        if rec["type"] == app_type and rec["id"] not in seen and store_key in rec["stores"]:
            rec["stores"].remove(store_key)
    return seen


def check_departed_sources(db, today):
    """For apps no longer in any store, check their source code is still
    online. Apps whose source has gone are hidden (but remembered, and
    re-checked each run in case it comes back)."""
    todo = [r for r in db.values() if not r["stores"]]

    def check(rec):
        ok = source_online(rec["source"])
        if ok is not None:
            rec["source_online"] = ok
            rec["source_checked"] = today

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(check, todo))
    gone = sum(1 for r in todo if r.get("source_online") is False)
    print(f"checked {len(todo)} apps no longer in a store: {gone} with source code gone")


def download_screenshots(db):
    """Copy any screenshots we don't have yet into docs/images/apps/."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    todo = [r for r in db.values() if r.get("screenshot_url") and not (
        r.get("screenshot") and (DOCS / r["screenshot"]).exists())]

    def fetch(rec):
        url = rec["screenshot_url"]
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
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
    for i, e in enumerate(entries):
        if not all(e.get(k) for k in ("type", "title", "source")) or e["type"] not in TYPES:
            sys.exit(f"{MANUAL.name} entry {i + 1}: needs type (watchface or watchapp), title and source")
    return entries


# ---------------------------------------------------------------- rendering

def entries_for(app_type, db, manual):
    """Merge store and manual entries for one type. A manual entry overrides
    the store's details for the same app (matched by the ID in its store link)."""
    entries = {}
    for rec in db.values():
        if rec["type"] != app_type or rec.get("source_online") is False:
            continue
        store = next((s for s in STORES if s in rec["stores"]), None)
        entries[rec["id"]] = {
            "title": rec["title"], "author": rec["author"], "source": rec["source"],
            "description": rec["description"], "screenshot": rec.get("screenshot"),
            "store": STORES[store]["url"].format(id=rec["id"]) if store else None,
            "store_name": STORES[store]["name"] if store else None,
            "departed": not store,
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
            "store_name": None if m.get("store") else base.get("store_name"),
            "departed": False,
        }
    return sorted(entries.values(), key=lambda e: (e["title"].lower(), e["author"].lower()))


def render_row(e):
    shot = ""
    if e["screenshot"]:
        shot = f'![{md_escape(e["title"])}](../{e["screenshot"]}){{ loading=lazy width="72" }}'
    name = f'[{md_escape(e["title"])}]({e["store"] or e["source"]})'
    if e["store_name"] == "Rebble App Store":
        name += "<br><small>Rebble App Store</small>"
    elif e["departed"]:
        name += "<br><small>No longer in the app stores</small>"
    elif not e["store"]:
        name += "<br><small>Not in the app stores</small>"
    dev = f'[{md_escape(e["author"] or "Source code")}]({e["source"]})'
    return f"| {shot} | {name} | {dev} | {md_escape(short(e['description']))} |"


def letter_nav(by_letter, current=None):
    links = []
    for l in LETTERS:
        if l in by_letter:
            label = letter_label(l)
            links.append(f"**{label}**" if l == current else f"[{label}]({l.lower()}.md)")
    return " · ".join(links)


def write_pages(app_type, entries, updated):
    _, label, index_page, folder = TYPES[app_type]
    by_letter = {}
    for e in entries:
        by_letter.setdefault(letter_of(e["title"]), []).append(e)

    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.md"):
        old.unlink()
    for l, items in by_letter.items():
        lines = [
            "<!-- Generated by scripts/update_app_directory.py: do not edit by hand -->",
            f"# {label.capitalize()}: {letter_label(l)}", "",
            f"[← About this list](../{index_page.name}) · {letter_nav(by_letter, l)}", "",
            f"*{len(items)} {label} · Last updated {updated}*", "",
            "| Screenshot | Name | Developer | Description |",
            "|------------|------|-----------|-------------|",
            *[render_row(e) for e in items], "",
        ]
        (folder / f"{l.lower()}.md").write_text("\n".join(lines), encoding="utf-8")

    counts = {
        "pebble": sum(1 for e in entries if e["store"] and e["store_name"] == "Pebble App Store"),
        "rebble": sum(1 for e in entries if e["store_name"] == "Rebble App Store"),
        "departed": sum(1 for e in entries if e["departed"]),
    }
    counts["manual"] = len(entries) - sum(counts.values())
    block = [
        BEGIN, "",
        f"**{len(entries):,} open source {label}.** Last updated {updated}.", "",
        f"- {counts['pebble']:,} from the Pebble App Store",
        f"- {counts['rebble']:,} more from the Rebble App Store",
        f"- {counts['departed']:,} no longer in either store (source code still online)",
        f"- {counts['manual']:,} added by hand", "",
        "| Letter | Count |", "|--------|-------|",
        *[f"| [{letter_label(l)}]({folder.name}/{l.lower()}.md) | {len(by_letter[l]):,} |"
          for l in LETTERS if l in by_letter],
        "", END,
    ]
    text = index_page.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        text = text[:text.index(BEGIN)] + "\n".join(block) + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + "\n".join(block)
    index_page.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    print(f"{label}: {len(entries)} entries on {len(by_letter)} pages {counts}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="don't call the stores; rebuild pages from saved data")
    ap.add_argument("--fixture",
                    help="JSON {'pebble': {'watchface': [...], 'watchapp': [...]}, 'rebble': {...}} of raw API apps")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()

    db = load_db()
    manual = load_manual()
    if not args.offline:
        fixture = json.loads(Path(args.fixture).read_text()) if args.fixture else None
        for store_key, store in STORES.items():
            for app_type, (kind, *_rest) in TYPES.items():
                raw = fixture[store_key][app_type] if fixture else fetch_store(store, kind)
                if not raw:
                    # Treat an empty listing as the store being broken, not as
                    # every app having left it.
                    sys.exit(f"{store['name']} returned no {app_type}s; not updating.")
                found = merge_store(db, store_key, raw, app_type, today)
                print(f"{store['name']}: {len(found)} open source {app_type}s")
        if not args.fixture:
            check_departed_sources(db, today)
            download_screenshots(db)
        save_db(db)
        (DATA / "last-updated.txt").write_text(today + "\n")

    updated_file = DATA / "last-updated.txt"
    updated = updated_file.read_text().strip() if updated_file.exists() else today
    for app_type in TYPES:
        write_pages(app_type, entries_for(app_type, db, manual), updated)


if __name__ == "__main__":
    main()
