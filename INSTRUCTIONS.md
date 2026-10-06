# All Things Pebble

A community-curated directory of all things related to Pebble smartwatches and other devices based on PebbleOS.

The site is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, and is hosted on GitHub Pages at [allthingspebble.saltedlolly.com](https://allthingspebble.saltedlolly.com).

## How the site is organised

- `docs/` - One Markdown file per section of the site. This is where you add links.
- `docs/images/` - Images used on the site (hardware photos, watchface and watchapp screenshots).
- `mkdocs.yml` - Site settings and the navigation menu. Add new pages to `nav:` here.
- `.github/workflows/deploy.yml` - Builds and publishes the site automatically on every push to `main`.

## Adding a link

1. Find the right page in `docs/` and the right section within it.
2. Add a line in the same format as the others:

   ```markdown
   - [Name](https://example.com) - Short description.
   ```

3. Open a pull request. Once it is merged, the site updates automatically within a couple of minutes.

## Previewing the site locally (optional)

You need Python 3.

```bash
cd ~/Projects/Pebble/all-things-pebble
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). The page reloads automatically as you edit files.

## Watchface and watchapp lists

The Watchfaces and Watchapps pages are built by `scripts/update_app_directory.py`. It combines:

- **The Pebble App Store:** every watchface and watchapp whose developer has published a source code link, fetched from the [Pebble App Store API](https://appstore-api.repebble.com/).
- **`data/manual-apps.yml`:** open source apps added by hand (not in the store, or not listing their source there). The file explains the fields.

Both are merged into one alphabetical list, with one page per letter in `docs/watchfaces/` and `docs/watchapps/`.

- `data/store-apps.json` remembers every store app ever seen. Apps that leave the store stay listed, linking to their source code.
- Screenshots are copied into `docs/images/apps/` so the site doesn't depend on the store's images.
- The deploy workflow runs the script on every push and every Monday, and commits any changes back to the repo. Pull before you push to pick these up.
- Don't edit the generated pages or the text between the `BEGIN GENERATED` / `END GENERATED` markers by hand.
- To rebuild the pages locally from the saved data, run `python3 scripts/update_app_directory.py --offline` (needs `pip install -r requirements.txt`). Leave off `--offline` to fetch from the store and download new screenshots.
