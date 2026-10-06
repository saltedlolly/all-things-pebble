# Apps for Pebble

A directory of **open source watchapps** for Pebble smartwatches, so developers can learn from and build on each other's work. Every entry links to the watchapp in an app store and to its source code.

Search for a watchapp by name, developer or description using the search box, or browse by letter below.

## How this list is made

The list is updated automatically every week:

1. **Pebble App Store:** every watchapp in the [Pebble App Store](https://apps.repebble.com/) whose developer has published a link to its source code, or whose website link points to a GitHub, GitLab or Codeberg repository.
2. **Rebble App Store:** any further open source watchapps from the [Rebble App Store](https://apps.rebble.io/) that aren't in the Pebble App Store.
3. **Added by hand:** open source watchapps that aren't in either store, listed in [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml).

Everything is merged into one alphabetical list. A few more things to know:

- **Open source** here means the source code is published. The **Licence** column shows the licence of the code (checked automatically for GitHub and GitLab). *No licence* means you can read the code and learn from it, but you don't have permission to reuse it.
- **Apps that leave the stores stay listed**, linking to their source code, for as long as that source code is still online.
- **Screenshots** are copied from the stores. The Pebble Time 2 screenshot is used where there is one, then the Pebble Round 2, then the Pebble 2 Duo, then the original watches.
- **Updated** shows the date of the app's latest release in the app store.

## Add your watchapp

**If it's in the Pebble or Rebble App Store**, you don't need to do anything here. Add a link to your source code in your app's store listing (the [Pebble Developer Dashboard](https://appstore-api.repebble.com/dashboard) for the Pebble App Store) and it will appear after the next weekly update.

**If it isn't in either store**, add it to [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml) and open a pull request:

1. Add an entry like this to the end of the file:

    ```yaml
    - type: watchapp
      title: My Watchapp
      author: Your Name
      source: https://github.com/you/my-watchapp
      screenshot: images/watchapps/my-watchapp.png
      description: One or two sentences about what it does.
    ```

2. Add a screenshot to the `docs/images/watchapps/` folder, ideally from a Pebble Time 2. The `screenshot` line is optional.
3. Open a pull request. Your watchapp will be slotted into the list in alphabetical order.

The source code must be publicly available, ideally with an open source licence.

## Report a mistake

If a watchapp here isn't actually open source (for example its link doesn't lead to its source code), add it to [`data/excluded-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/excluded-apps.yml) with a pull request, or [open an issue](https://github.com/saltedlolly/all-things-pebble/issues). It will be left out from then on.

## Browse

<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->

**1,619 open source watchapps.** Last updated 2026-10-06.

- 1,384 from the Pebble App Store
- 234 more from the Rebble App Store
- 0 no longer in either store (source code still online)
- 1 added by hand

| Letter | Count |
|--------|-------|
| [A](watchapps/a.md) | 54 |
| [B](watchapps/b.md) | 103 |
| [C](watchapps/c.md) | 108 |
| [D](watchapps/d.md) | 76 |
| [E](watchapps/e.md) | 31 |
| [F](watchapps/f.md) | 53 |
| [G](watchapps/g.md) | 49 |
| [H](watchapps/h.md) | 69 |
| [I](watchapps/i.md) | 33 |
| [J](watchapps/j.md) | 13 |
| [K](watchapps/k.md) | 32 |
| [L](watchapps/l.md) | 48 |
| [M](watchapps/m.md) | 95 |
| [N](watchapps/n.md) | 44 |
| [O](watchapps/o.md) | 38 |
| [P](watchapps/p.md) | 199 |
| [Q](watchapps/q.md) | 19 |
| [R](watchapps/r.md) | 75 |
| [S](watchapps/s.md) | 153 |
| [T](watchapps/t.md) | 164 |
| [U](watchapps/u.md) | 26 |
| [V](watchapps/v.md) | 25 |
| [W](watchapps/w.md) | 72 |
| [X](watchapps/x.md) | 5 |
| [Y](watchapps/y.md) | 8 |
| [Z](watchapps/z.md) | 5 |
| [0–9 & other](watchapps/other.md) | 22 |

<!-- END GENERATED -->
