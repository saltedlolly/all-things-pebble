# Watchfaces for Pebble

A directory of **open source watchfaces** for Pebble smartwatches, so developers can learn from and build on each other's work. Every entry links to the watchface in an app store and to its source code.

Search for a watchface by name, developer or description using the search box, or browse by letter below.

## How this list is made

The list is updated automatically every week:

1. **Pebble App Store:** every watchface in the [Pebble App Store](https://apps.repebble.com/) whose developer has published a link to its source code, or whose website link points to a GitHub, GitLab or Codeberg repository.
2. **Rebble App Store:** any further open source watchfaces from the [Rebble App Store](https://apps.rebble.io/) that aren't in the Pebble App Store.
3. **Added by hand:** open source watchfaces that aren't in either store, listed in [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml).

Everything is merged into one alphabetical list. A few more things to know:

- **Open source** here means the source code is published. The **Licence** column shows the licence of the code (checked automatically for GitHub and GitLab). *No licence* means you can read the code and learn from it, but you don't have permission to reuse it.
- **Apps that leave the stores stay listed**, linking to their source code, for as long as that source code is still online.
- **Screenshots** are copied from the stores. The Pebble Time 2 screenshot is used where there is one, then the Pebble Round 2, then the Pebble 2 Duo, then the original watches.
- **Updated** shows the date of the app's latest release in the app store.

## Add your watchface

**If it's in the Pebble or Rebble App Store**, you don't need to do anything here. Add a link to your source code in your app's store listing (the [Pebble Developer Dashboard](https://appstore-api.repebble.com/dashboard) for the Pebble App Store) and it will appear after the next weekly update.

**If it isn't in either store**, add it to [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml) and open a pull request:

1. Add an entry like this to the end of the file:

    ```yaml
    - type: watchface
      title: My Watchface
      author: Your Name
      source: https://github.com/you/my-watchface
      screenshot: images/watchfaces/my-watchface.png
      description: One or two sentences about what it does.
    ```

2. Add a screenshot to the `docs/images/watchfaces/` folder, ideally from a Pebble Time 2. The `screenshot` line is optional.
3. Open a pull request. Your watchface will be slotted into the list in alphabetical order.

The source code must be publicly available, ideally with an open source licence.

## Report a mistake

If a watchface here isn't actually open source (for example its link doesn't lead to its source code), add it to [`data/excluded-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/excluded-apps.yml) with a pull request, or [open an issue](https://github.com/saltedlolly/all-things-pebble/issues). It will be left out from then on.

## Browse

<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->

**2,770 open source watchfaces.** Last updated 2026-10-06.

- 1,319 from the Pebble App Store
- 1,451 more from the Rebble App Store
- 0 no longer in either store (source code still online)
- 0 added by hand

| Letter | Count |
|--------|-------|
| [A](watchfaces/a.md) | 139 |
| [B](watchfaces/b.md) | 186 |
| [C](watchfaces/c.md) | 215 |
| [D](watchfaces/d.md) | 138 |
| [E](watchfaces/e.md) | 60 |
| [F](watchfaces/f.md) | 124 |
| [G](watchfaces/g.md) | 70 |
| [H](watchfaces/h.md) | 115 |
| [I](watchfaces/i.md) | 51 |
| [J](watchfaces/j.md) | 29 |
| [K](watchfaces/k.md) | 36 |
| [L](watchfaces/l.md) | 80 |
| [M](watchfaces/m.md) | 195 |
| [N](watchfaces/n.md) | 84 |
| [O](watchfaces/o.md) | 43 |
| [P](watchfaces/p.md) | 237 |
| [Q](watchfaces/q.md) | 6 |
| [R](watchfaces/r.md) | 107 |
| [S](watchfaces/s.md) | 327 |
| [T](watchfaces/t.md) | 259 |
| [U](watchfaces/u.md) | 26 |
| [V](watchfaces/v.md) | 46 |
| [W](watchfaces/w.md) | 85 |
| [X](watchfaces/x.md) | 11 |
| [Y](watchfaces/y.md) | 19 |
| [Z](watchfaces/z.md) | 21 |
| [0–9 & other](watchfaces/other.md) | 61 |

<!-- END GENERATED -->
