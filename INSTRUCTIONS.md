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
