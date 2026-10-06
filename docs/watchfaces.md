# Watchfaces for Pebble

A directory of **open source watchfaces** for Pebble smartwatches, so developers can learn from and build on each other's work. Every entry links to the watchface in an app store and to its source code.

Search for a watchface by name, developer or description using the search box, or browse by letter below.

## How this list is made

The list is rebuilt automatically every week:

1. **Pebble App Store:** every watchface in the [Pebble App Store](https://apps.repebble.com/) whose developer has published a link to its source code.
2. **Rebble App Store:** any further open source watchfaces from the [Rebble App Store](https://apps.rebble.io/) that aren't in the Pebble App Store.
3. **Added by hand:** open source watchfaces that aren't in either store, listed in [`data/manual-apps.yml`](https://github.com/saltedlolly/all-things-pebble/blob/main/data/manual-apps.yml).

Everything is merged into one alphabetical list. A few more things to know:

- **Open source** here means the source code is published. The **Licence** column shows the licence of the code (checked automatically for GitHub and GitLab). *No licence* means you can read the code and learn from it, but you don't have permission to reuse it.
- **Apps that leave the stores stay listed**, linking to their source code, for as long as that source code is still online.
- **Screenshots** are copied from the stores, using the Pebble Time 2 version where there is one.

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

## Browse

<!-- BEGIN GENERATED: do not edit by hand, run scripts/update_app_directory.py -->

*The list is being generated. Check back shortly.*

<!-- END GENERATED -->
