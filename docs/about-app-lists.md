# About the App Lists

The [Pebble Watchfaces](watchfaces.md) and [Pebble Apps](watchapps.md) pages list **open source** watchfaces and watchapps for Pebble smartwatches, so developers can learn from and build on each other's work. Every entry links to the app in an app store and to its source code.

## How the lists are made

The lists are updated automatically every week:

1. **Pebble App Store:** every watchface and watchapp in the [Pebble App Store](https://apps.repebble.com/) whose developer has published a link to its source code, or whose website link points to a GitHub, GitLab or Codeberg repository.
2. **Rebble App Store:** any further open source apps from the [Rebble App Store](https://apps.rebble.io/) that aren't in the Pebble App Store.
3. **Added by hand:** open source apps that aren't in either store, listed in [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml).

Everything is merged into one alphabetical list for watchfaces and one for apps.

## What the columns mean

- **Name** links to the app in the Pebble App Store, or the Rebble App Store if it's only there. Apps that aren't in either store link to their source code.
- **View source** (top right of each card) links to the source code. The source can be hosted anywhere.
- **Developer** links to the developer's page in the Pebble or Rebble App Store, so you can find their other apps.
- **Licence** is the licence of the source code, checked automatically for GitHub and GitLab repositories. *No licence* means you can read the code and learn from it, but you don't have permission to reuse it. *See source* means the code is hosted somewhere the licence can't be checked automatically.
- **Version** is the app's latest version in the app store, where known.
- **Updated** is the date of the app's latest release in the app store.
- **Runs on** lists the watches the app supports, as listed in the app store: Round 2, Time 2, Pebble 2 Duo, Pebble 2, Time Round, Time (including Time Steel) and Classic (the original Pebble and Pebble Steel).
- **Screenshots** are copied from the stores. The Pebble Time 2 screenshot is used where there is one, then the Pebble Round 2, then the Pebble 2 Duo, then the original watches.

**Apps that leave the stores stay listed**, linking to their source code, for as long as that source code is still online.

## Add your app or watchface

**If it's in the Pebble or Rebble App Store**, you don't need to do anything here. Add a link to your source code in your app's store listing (the [Pebble Developer Dashboard](https://appstore-api.repebble.com/dashboard) for the Pebble App Store) and it will appear after the next weekly update.

**If it isn't in either store**, add it to [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml) and open a pull request:

1. Add an entry like this to the end of the file:

    ```yaml
    - type: watchface        # or watchapp
      title: My Watchface
      author: Your Name
      source: https://github.com/you/my-watchface
      screenshot: images/watchfaces/my-watchface.png
      description: One or two sentences about what it does.
    ```

2. Add a screenshot to the `docs/images/watchfaces/` or `docs/images/watchapps/` folder, ideally from a Pebble Time 2. The `screenshot` line is optional.
3. Open a pull request. Your app will be slotted into the list in alphabetical order.

The source code must be publicly available, ideally with an open source licence.

## Report a mistake

If an app or watchface listed here isn't actually open source (for example its link doesn't lead to its source code), add it to [`data/excluded-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/excluded-apps.yml) with a pull request, or [open an issue](https://github.com/saltedlolly/all-things-pebble/issues). It will be left out from then on.
