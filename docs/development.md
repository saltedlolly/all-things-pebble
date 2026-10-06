# Development

Tools, libraries, languages and environments for building Pebble watchfaces and apps.

## Pebble Platforms

The SDK refers to each watch by its platform codename.

| Watch | Platform |
|-------|----------|
| Pebble (Classic), Pebble Steel | `aplite` |
| Pebble Time, Pebble Time Steel | `basalt` |
| Pebble Time Round | `chalk` |
| Pebble 2 | `diorite` |
| Pebble Time 2 | `emery` |
| Pebble 2 Duo | `flint` |
| Pebble Round 2 | `gabbro` |

## General


- [PebbleKit.ts](https://github.com/jccit/PebbleKit.ts) - A modern Pebble app boilerplate using TypeScript by [@jccit](https://github.com/jccit)
- [microPebble](https://github.com/matejdro/microPebble) - An open source Pebble companion app based on the libpebble3 by [@matejdro](https://github.com/matejdro).
- [Better Pebble Emulator](https://github.com/only-meeps/Better-Pebble-Emulator) - A Pebble emulator for Ubuntu and Debian.
- [PebbleGL](https://github.com/mhungerford/PebbleGL) - OpenGL for Pebble. Uses minimal OpenGL engine (miniGL) for rendering a 3D world on the Pebble Smartwatch.

## Development Environments & Build Tools

- [pebble-wrapper](https://github.com/kennedn/pebble-wrapper) - Wrapper script to run the Pebble SDK in Docker or Podman.
- [docker-pebble-dev](https://github.com/bboehmke/docker-pebble-dev) - Docker image for Pebble development.
- [Docker and the Pebble Emulator](https://github.com/clach04/docker-pebble-dev/wiki) - Guide to running the SDK and emulator in Docker.
- [pebble-setup](https://github.com/andyburris/pebble-setup) - Pebble development setup guide.
- [pebble-devcontainer](https://github.com/FBarrca/pebble-devcontainer) - VS Code devcontainer for Pebble development.
- [pebble-codespace](https://github.com/blockarchitech/pebble-codespace) - Fully featured Pebble dev environment using GitHub Codespaces.
- [pebble-time2-dev-setup](https://github.com/ArtRichards/pebble-time2-dev-setup) - Tested setup guide for a Pebble Time 2 Linux dev machine.
- [pebble-sdk-arm](https://github.com/sethasaurus/pebble-sdk-arm) - Pebble SDK on ARM machines.
- [pebble-bazel](https://github.com/imax9000/pebble-bazel) - Build Pebble apps using Bazel.
- [github_action_pebble_build](https://github.com/clach04/github_action_pebble_build) - GitHub Action for building Pebble apps in CI.
- [pebble_watchface_framework](https://github.com/clach04/pebble_watchface_framework) - Demo watchface built with GitHub Actions, with tips for GitHub Codespaces and importing into CloudPebble.
- [cloudpebble-composed](https://github.com/gfunkmonk/cloudpebble-composed) - Self-hosted CloudPebble using Docker Compose. Not considered safe to expose publicly.
- [Pebble-NMBS](https://github.com/kristofwillen/Pebble-NMBS) - Example of a Docker-based Pebble build running under GitHub Actions.
- [python-pebble-tools](https://github.com/clach04/python-pebble-tools) - Process locker and other helper tools for the Pebble SDK.
- [rebbletool](https://github.com/richinfante/rebbletool) - Python 3 port of pebble-tool. Popular before Core Devices' updated pebble-tool.
- [Building Pebble Watchfaces on Modern Systems](https://rich.sh/2025/02/09/building-pebble-watchfaces-on-modern-systems-sdk) - Blog post on getting the SDK running on modern systems.
- [pebble-wf-agent-skill](https://github.com/priyankark/pebble-wf-agent-skill) - AI agent skill for building Pebble watchfaces end to end.

## Languages & Frameworks

- [pebble-modern-js](https://github.com/Sorixelle/pebble-modern-js) - Use modern JavaScript in PebbleKit JS.
- [pybble](https://github.com/hiway/pybble) - Write Pebble apps in Python.
- [rust4pebble](https://github.com/jbellerb/rust4pebble) - Rust bindings for the Pebble SDK.
- [pebble-rust-2026](https://github.com/cmbartschat/pebble-rust-2026) - Rust wrapper for the Pebble C API.
- [zig-pebble-sdk](https://github.com/vsergeev/zig-pebble-sdk) - Zig SDK for Pebble.
- [Nebble](https://github.com/Brokezawa/nebble) - Modern, type-safe Nim wrapper for the Pebble SDK.
- [pebble-cpp](https://github.com/codaris/pebble-cpp) - C++ wrapper for the Pebble SDK.
- [GeaStack Pebble](https://github.com/geastack/pebble) - Compiles Gea TSX apps into native Pebble apps with no JavaScript engine on the watch.
- [example-pebble-inferencing](https://github.com/edgeimpulse/example-pebble-inferencing) - Run TinyML models on Pebble with Edge Impulse.

## Libraries

- [pebble-scalable](https://github.com/C-D-Lewis/pebble-dev/tree/master/libraries/pebble-scalable) - Library to help scale apps to all Pebble display sizes.
- [pebble-fctx](https://github.com/jrmobley/pebble-fctx) - Anti-aliased vector drawing and text, including rotated text.
- [SDFDemo](https://github.com/utessel/SDFDemo) - Scalable fonts using signed distance fields.
- [EffectLayer](https://github.com/ygalanter/pebble-effect-layer) - Visual effects layer (invert, mirror, blur etc.) for Pebble apps.
- [GBitmap Colour Palette Manipulator](https://github.com/rebootsramblings/GBitmap-Colour-Palette-Manipulator) - Manipulate the colour palettes of GBitmaps at runtime.
- [enamel](https://github.com/gregoiresage/enamel) - Helper for generating Clay settings code.
- [pebble-events](https://github.com/Katharine/pebble-events) - Lets multiple handlers subscribe to Pebble event services.
- [pebble-libraries](https://github.com/CometDog/pebble-libraries) - Collection of libraries, including an accelerated tick timer for debugging.
- [pebble-gbc-graphics](https://github.com/HarrisonAllen/pebble-gbc-graphics) - Game Boy Color style tile-based graphics engine.
- [pebble-math-sll](https://github.com/kmwoley/pebble-math-sll) - Fixed-point maths library.
- [pebble-timeline-js](https://github.com/C-D-Lewis/pebble-timeline-js) - JavaScript library for pushing Timeline pins.
- [Custom Status Bar](https://github.com/rebootsramblings/custom-status-bar-for-pebble) - Custom status bar layer, including a battery indicator.
- [pebble_memory_tools](https://github.com/LeFauve/pebble_memory_tools) - Tools for tracking down memory usage and leaks.

## Integrations & Utilities

- [node-red-pebble-timeline](https://flows.nodered.org/node/@skylord123/node-red-pebble-timeline) - Node-RED nodes for sending Pebble Timeline pins.
- [Pebble-Timeline-Worker](https://github.com/apalumbo2001/Pebble-Timeline-Worker) - Cloudflare Worker for pushing custom Timeline pins.
- [pypebbleapi](https://github.com/clach04/pypebbleapi) - Python client library for the Timeline API (works with Rebble's Timeline service).
- [pebble-image-viewer](https://github.com/gregoiresage/pebble-image-viewer) - Watchapp for previewing images on a Pebble ([app store](https://apps.rebble.io/en_US/application/53bdb1291c6da72083000044)).
- [Preview App by Tack Mobile](https://apps.rebble.io/en_US/application/56240ecbbdf1bfb3cb00009e) - Watchapp for previewing UI mockups on a Pebble.
- [Clay with manual message keys](https://github.com/andrewchilds/t1000-pebble-cgm/blob/main/src/pkjs/index.js) - Example Clay config page with manually defined message keys.
- [pbw-tools](https://github.com/southwolf/pbw-tools) - Tools for inspecting and modifying .pbw files.
- [Pebble App Config Page Backup](https://github.com/Roman-Port/Pebble-App-Config-Page-Backup) - Archived configuration pages for older Pebble apps whose config sites have gone offline.

## Hacking & Reverse Engineering

- [rockgarden](https://github.com/clach04/rockgarden) - Patch and modify existing watchfaces and apps (maintained fork of [cpfair/rockgarden](https://github.com/cpfair/rockgarden)).
- [sand](https://github.com/cpfair/sand) - Remix existing Pebble apps.
- [pebble-pyrite](https://github.com/sethasaurus/pebble-pyrite) - Utilities for working with Pebble app resources.
- [pebble_patch_tts](https://github.com/clach04/pebble_patch_tts) - Patch voice dictation to remove punctuation. Uses rockgarden.
- [pebble-autoconfig](https://github.com/gregoiresage/pebble-autoconfig) - Generate configuration pages, handy for recreating config pages that have gone offline.
- [radare2](https://github.com/radareorg/radare2) - Reverse engineering framework with support for Pebble apps. See [this guide](https://www.reddit.com/r/pebbledevelopers/comments/uc50kw/reverse_engineeringdecompiling_with_radare2r2/).

## Tips

- **PBW files are ZIP files.** You can unzip a `.pbw`, edit its JavaScript (e.g. to fix a dead settings page or weather API), and zip it back up. No checksums or manifest changes are needed.
- **View logs from a real watch.** Enable Developer Mode in the Pebble app, then run `pebble logs --phone <PHONE_IP>` to see logs from both C and JavaScript code.
- **Emulator hung?** Run `pebble kill`, stop any remaining emulator processes, then run `pebble wipe`.
- **SDK versions.** Use SDK 4.x. SDK 3.x can still build apps that run on firmware 4.x. SDK 2 has incompatibilities with SDK 1, and SDK 1 should not be used.
- **Look for unmerged fixes.** Some tool fixes only exist as open pull requests, e.g. [pebble-tool PRs](https://github.com/pebble-dev/pebble-tool/pulls) (such as logging on Windows) and [Clay PRs](https://github.com/pebble/clay/pulls) (such as Clay config working in the emulator with a modern browser). Rebble's [Clay fork](https://github.com/pebble-dev/clay/branches) is active again and published as [@rebble/clay](https://www.npmjs.com/package/@rebble/clay).
- **Download a PBW from the Rebble store.** Add `?dev_settings=true` to an app's Rebble store URL to get a download link for its PBW in your browser.

## Talks & Guides

- [Pebble Dev Retreat 2014: Memory](https://www.youtube.com/watch?v=8tOhdUXcSkw) - Talk on memory usage on Pebble ([slides](https://www.slideshare.net/slideshow/pebble-dev-retreat2014size/40376128)).
- [Rebble boot weather bootstrap](https://github.com/pebble-dev/rebble-boot/blob/master/boot/stage2.py#L182) - Where Rebble's boot process sets the weather service URL.
- [SDK 3 Migration Guide](https://developer.rebble.io/developer.pebble.com/guides/migration/migration-guide-3) - Moving older apps to SDK 3. See also [Remy Sharp's porting notes](https://remysharp.com/2015/07/29/notes-on-porting-my-pebble-app-to-sdk-3).
