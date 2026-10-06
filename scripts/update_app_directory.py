#!/usr/bin/env python3
"""Build the open source watchface and watchapp directories.

Where entries come from:
  1. The Pebble App Store (Core Devices): every watchface/watchapp whose
     developer has published a source code link.
  2. The Rebble App Store: any further open source apps that aren't in the
     Pebble App Store (or don't list their source there).
  3. data/manual-apps.yml: open source apps added by hand.

An app counts as open source if its store listing has a source code link,
or (failing that) its website link points to a GitHub, GitLab or Codeberg
repository. False positives can be listed in data/excluded-apps.yml.

What it remembers between runs (committed to the repo):
  - data/store-apps.json: every open source store app ever seen. Apps that
    leave both stores stay listed, linking to their source code, for as long
    as that source code is still online.
  - docs/images/apps/: a copy of each app's screenshot, so the directory
    doesn't depend on the stores' image hosting.
  - data/licences.json: the licence of each GitHub/GitLab repository, shown
    next to each app. Checked a batch at a time to stay inside GitHub's API
    limits, and re-checked every few months.

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
import email.utils
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml  # installed with mkdocs

PREFERRED_PLATFORM = "emery"  # Pebble Time 2: the platform asked for when fetching
# Which watch's screenshot (and description) to use, in order of preference:
# Pebble Time 2, Pebble Round 2, Pebble 2 Duo, then the original watches.
SCREENSHOT_ORDER = ["emery", "gabbro", "flint", "basalt", "chalk", "diorite", "aplite"]

# Stores, in order of preference. An app in both is linked to the first.
STORES = {
    "pebble": {
        "name": "Pebble App Store",
        "api": "https://appstore-api.repebble.com/api/v1/apps/collection/all/{kind}",
        # Two listings, merged: the apps with a source link (this API can
        # filter on that), and the general listing, to also find apps whose
        # website is a code repository. The general listing only covers part
        # of the store, so it can't replace the filtered one. Both ignore the
        # hardware asked for.
        "params": [{"hardware": PREFERRED_PLATFORM, "source": "available"},
                   {"hardware": PREFERRED_PLATFORM}],
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
LICENCES = DATA / "licences.json"
LICENCE_BATCH = 800      # GitHub allows 1,000 API calls an hour from Actions
LICENCE_RECHECK_DAYS = 90
MANUAL = DATA / "manual-apps.yml"
EXCLUDED = DATA / "excluded-apps.yml"
# Apps with no source link but whose website is one of these are treated as
# open source, since the website is almost certainly the code repository.
CODE_HOST_WEBSITES = {"github.com", "gitlab.com", "codeberg.org"}
IMAGES = DOCS / "images" / "apps"

TYPES = {
    # type: (API kind string, page label, index page, letter page folder)
    "watchface": ("watchfaces", "watchfaces", DOCS / "watchfaces.md", DOCS / "watchfaces"),
    "watchapp": ("watchapps-and-companions", "watchapps", DOCS / "watchapps.md", DOCS / "watchapps"),
}
BEGIN = "<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->"
END = "<!-- END GENERATED -->"

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
    """Return the source code link as a clean URL, or None if there isn't one.
    Source code can be hosted anywhere, so any web link counts."""
    if not src or not isinstance(src, str):
        return None
    src = src.strip()
    if not re.match(r"^https?://", src, re.I):
        # Links like "github.com/user/repo" without the https://
        if re.match(r"^(www\.)?[a-z0-9-]+(\.[a-z0-9-]+)+(/|$)", src, re.I):
            src = "https://" + src
        else:
            return None
    try:
        u = urllib.parse.urlparse(src)
    except ValueError:
        return None
    if not u.hostname or "." not in u.hostname:
        return None
    return src


def platforms_in_order(app):
    """The app's hardware platforms, most preferred first."""
    rank = {name: i for i, name in enumerate(SCREENSHOT_ORDER)}
    return sorted(app.get("hardware_platforms") or [],
                  key=lambda hp: rank.get(hp.get("name"), len(rank)))


def app_source(app):
    """The app's source code link and where it came from ("source" or
    "website"), or (None, None) if it doesn't have one."""
    src = normalise_source(app.get("source"))
    if src:
        return src, "source"
    site = normalise_source(app.get("website"))
    if site:
        u = urllib.parse.urlparse(site)
        host = u.hostname.lower().removeprefix("www.")
        if host in CODE_HOST_WEBSITES and len([p for p in u.path.split("/") if p]) >= 2:
            return site, "website"  # a repository, not just a profile page
    return None, None


def load_excluded():
    """Store IDs and source links of apps to leave out (false positives)."""
    if not EXCLUDED.exists():
        return set()
    entries = yaml.safe_load(EXCLUDED.read_text(encoding="utf-8")) or []
    out = set()
    for i, e in enumerate(entries):
        if not (e.get("id") or e.get("source")):
            sys.exit(f"{EXCLUDED.name} entry {i + 1}: needs an id or a source")
        for key in ("id", "source"):
            if e.get(key):
                out.add(str(e[key]).strip().rstrip("/").lower())
    return out


def is_excluded(app_id, source, excluded):
    return (app_id or "").lower() in excluded or (source or "").rstrip("/").lower() in excluded


def store_screenshot(app):
    for hp in platforms_in_order(app):
        shot = (hp.get("images") or {}).get("screenshot")
        if shot:
            return shot
    for img in app.get("screenshot_images") or []:
        for url in img.values():
            if url:
                return url
    return None


def store_description(app):
    texts = [hp.get("description") for hp in platforms_in_order(app)] + [app.get("description")]
    return next((t for t in texts if t and t.strip()), "")


def store_updated(app):
    """Date of the app's latest release in the store, as YYYY-MM-DD, if known.
    The Pebble API uses ISO dates, the Rebble API uses RFC 1123 dates."""
    for value in ((app.get("latest_release") or {}).get("published_date"),
                  app.get("published_date"), app.get("created_at")):
        if not value:
            continue
        try:
            return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
        try:
            return email.utils.parsedate_to_datetime(value).date().isoformat()
        except (TypeError, ValueError):
            pass
    return None


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
        src, found_in = app_source(a)
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
                "source_from": found_in,
                "description": short(store_description(a), 400),
                "screenshot_url": shot,
            })
        # Remember the latest release date in each store; show the newest
        updated = store_updated(a)
        if updated:
            rec.setdefault("store_updated", {})[store_key] = updated
        if store_key not in rec["stores"]:
            rec["stores"].append(store_key)
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


class RateLimited(Exception):
    pass


def lookup_licence(source):
    """Return (licence, repo_exists) for a GitHub or GitLab repository.
    licence is an SPDX id such as "MIT", "Other" for an unrecognised licence,
    or None for no licence. Returns None if the host isn't supported."""
    u = urllib.parse.urlparse(source)
    host = (u.hostname or "").lower().removeprefix("www.")
    parts = [p for p in u.path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1].removesuffix(".git")
    if host == "github.com":
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {**HEADERS, "Accept": "application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    elif host == "gitlab.com":
        # GitLab projects can be nested in groups, so use the whole path
        path = "/".join(parts[:parts.index("-")] if "-" in parts else parts)
        url = f"https://gitlab.com/api/v4/projects/{urllib.parse.quote(path.removesuffix('.git'), safe='')}?license=true"
        headers = HEADERS
    else:
        return None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return (None, False)
        if e.code in (403, 429):
            raise RateLimited()
        raise
    lic = data.get("license")
    if not lic:
        return (None, True)
    spdx = lic.get("spdx_id") or lic.get("key") or lic.get("nickname")
    return ("Other" if not spdx or spdx.upper() in ("NOASSERTION", "OTHER") else spdx, True)


def check_licences(sources, today):
    """Look up licences for a batch of sources, oldest checks first."""
    cache = json.loads(LICENCES.read_text()) if LICENCES.exists() else {}
    cutoff = (datetime.date.fromisoformat(today) - datetime.timedelta(days=LICENCE_RECHECK_DAYS)).isoformat()
    due = [s for s in sorted(set(sources)) if cache.get(s, {}).get("checked", "") < cutoff]
    due.sort(key=lambda s: cache.get(s, {}).get("checked", ""))  # never-checked first
    checked = 0
    for source in due[:LICENCE_BATCH]:
        try:
            result = lookup_licence(source)
        except RateLimited:
            print("licence checks: rate limited, carrying on next run", file=sys.stderr)
            break
        except Exception as e:
            print(f"licence check failed for {source}: {e}", file=sys.stderr)
            continue
        if result is None:
            cache[source] = {"licence": "unsupported", "checked": today}
        else:
            lic, exists = result
            cache[source] = {"licence": lic, "exists": exists, "checked": today}
        checked += 1
    LICENCES.write_text(json.dumps(dict(sorted(cache.items())), indent=1) + "\n")
    print(f"licence checks: {checked} done, {max(0, len(due) - checked)} still due")
    return cache


def load_licences():
    return json.loads(LICENCES.read_text()) if LICENCES.exists() else {}


def licence_label(source, cache):
    entry = cache.get(source)
    if entry is None:
        return "Not checked yet"
    if entry["licence"] == "unsupported":
        return "See source"
    if entry["licence"] is None:
        return "No licence"
    return entry["licence"]


def manual_screenshots(manual):
    """For hand-added apps with a store link but no screenshot of their own,
    copy the store's screenshot into docs/images/apps/."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    for m in manual:
        ids = re.findall(r"[0-9a-f]{24}", m.get("store") or "")
        if m.get("screenshot") or not ids or list(IMAGES.glob(f"{ids[0]}.*")):
            continue
        for store in STORES.values():
            api = store["api"].split("/collection/")[0] + f"/id/{ids[0]}?hardware={PREFERRED_PLATFORM}"
            try:
                apps = http_get(api)["data"]
                shot = store_screenshot(apps[0]) if apps else None
                if shot:
                    ext = Path(urllib.parse.urlparse(shot).path).suffix.lower() or ".png"
                    (IMAGES / f"{ids[0]}{ext}").write_bytes(http_get(shot, binary=True))
                    break
            except Exception as e:
                print(f"no store screenshot for {m['title']} from {store['name']}: {e}", file=sys.stderr)


def manual_screenshot_path(m):
    if m.get("screenshot"):
        return m["screenshot"]
    ids = re.findall(r"[0-9a-f]{24}", m.get("store") or "")
    found = list(IMAGES.glob(f"{ids[0]}.*")) if ids else []
    return found[0].relative_to(DOCS).as_posix() if found else None


def load_manual():
    if not MANUAL.exists():
        return []
    entries = yaml.safe_load(MANUAL.read_text(encoding="utf-8")) or []
    for i, e in enumerate(entries):
        if not all(e.get(k) for k in ("type", "title", "source")) or e["type"] not in TYPES:
            sys.exit(f"{MANUAL.name} entry {i + 1}: needs type (watchface or watchapp), title and source")
    return entries


# ---------------------------------------------------------------- rendering

def entries_for(app_type, db, manual, licences, excluded):
    """Merge store and manual entries for one type. A manual entry overrides
    the store's details for the same app (matched by the ID in its store link)."""
    entries = {}
    for rec in db.values():
        if rec["type"] != app_type or rec.get("source_online") is False:
            continue
        if is_excluded(rec["id"], rec["source"], excluded):
            continue
        if not rec["stores"] and licences.get(rec["source"], {}).get("exists") is False:
            continue  # left the stores and the repository has been deleted
        store = next((s for s in STORES if s in rec["stores"]), None)
        entries[rec["id"]] = {
            "title": rec["title"], "author": rec["author"], "source": rec["source"],
            "description": rec["description"], "screenshot": rec.get("screenshot"),
            "store": STORES[store]["url"].format(id=rec["id"]) if store else None,
            "store_name": STORES[store]["name"] if store else None,
            "departed": not store,
            "licence": licence_label(rec["source"], licences),
            "updated": max((rec.get("store_updated") or {}).values(), default=""),
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
            "screenshot": manual_screenshot_path(m) or base.get("screenshot"),
            "store": m.get("store") or base.get("store"),
            "store_name": None if m.get("store") else base.get("store_name"),
            "departed": False,
            "licence": licence_label(m["source"], licences),
            "updated": str(m.get("updated") or base.get("updated", "")),
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
    lic = e["licence"]
    if lic in ("No licence", "Not checked yet", "See source", "Other"):
        lic = f"<small>{lic}</small>"
    updated = e["updated"] or "<small>Unknown</small>"
    return f"| {shot} | {name} | {dev} | {lic} | {updated} | {md_escape(short(e['description']))} |"


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
            "| Screenshot | Name | Developer | Licence | Updated | Description |",
            "|------------|------|-----------|---------|---------|-------------|",
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

def snapshot():
    """Fingerprint of the saved data, to tell whether a run changed anything."""
    files = [STORE_DB, LICENCES]
    return (tuple(f.read_text() if f.exists() else "" for f in files),
            tuple(sorted(p.name for p in IMAGES.glob("*"))) if IMAGES.exists() else ())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="don't call the stores; rebuild pages from saved data")
    ap.add_argument("--fixture",
                    help="JSON {'pebble': {'watchface': [...], 'watchapp': [...]}, 'rebble': {...}} of raw API apps")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()

    db = load_db()
    for rec in db.values():  # fields from older versions that changed every run
        rec.pop("last_seen", None)
        rec.pop("source_checked", None)
    manual = load_manual()
    updated_file = DATA / "last-updated.txt"
    if not args.offline:
        before = snapshot()
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
            manual_screenshots(manual)
            check_licences([r["source"] for r in db.values()] + [m["source"] for m in manual], today)
        save_db(db)
        # Only move the "last updated" date when something actually changed,
        # so a run that finds nothing new doesn't produce a commit.
        if snapshot() != before or not updated_file.exists():
            updated_file.write_text(today + "\n")
            print("changes found: last updated date set to", today)
        else:
            print("no changes since last update")

    updated = updated_file.read_text().strip() if updated_file.exists() else today
    licences = load_licences()
    excluded = load_excluded()
    for app_type in TYPES:
        write_pages(app_type, entries_for(app_type, db, manual, licences, excluded), updated)


if __name__ == "__main__":
    main()
