# modshop

Scripts, patches and notes for building modded games on Linux, written so that someone with none of the context can clone this and reproduce the result from their own copies of the game and the mods. One directory per game under `games/`; shared helpers under `tools/`.

**Nothing in this repository is a game file or a mod file**, and nothing here will download one for you that you could not get yourself. The scripts take the archives you fetched from the mods' own pages, the game you own through Steam, and build the modded install from those. Fixes to mods are expressed as scripts that patch the mod's bytes at build time, never as patched copies.

## What is here

| Path | What |
| --- | --- |
| [`src/modshop/`](src/modshop/) | the `modshop` command: a chain of keyed checkpoints built from a pristine game and the mod archives, deployed to the handheld by content; `core/` is game-agnostic, one subpackage per game beside it |
| [`games/kotor/`](games/kotor/) | Knights of the Old Republic (Steam, Proton): the community Full Build installed by script, the KMRP interface and controller patch built on Linux, repairs for things that break under Proton, and the diagnosis notes behind them |
| [`tools/restore-window/`](tools/restore-window/) | un-minimize a wine game that lost its window under gamescope, where there is no taskbar to get it back |
| [`docs/conventions.md`](docs/conventions.md) | the rules every game directory follows: what goes in git, where data lives, how fixes to other projects are kept |

## Quick start

1. Clone, `mise install` (uv, Rust and the Steam downloader), `mise run nws:build` (the NWScript compiler), `uv sync` (the tool and the patcher), then read the game's README: `games/kotor/README.md` is the whole procedure for that game.
2. Copy `local.example.toml` to `local.toml` and fill in your machine names and paths. The docs say "the handheld" and "the build host"; that file says which is which for you.
3. Each game keeps its archives, game copies, logs and build outputs under `games/<game>/data/`, which git ignores. The scripts find it by default; `KOTOR_DATA` (for KotOR) points them elsewhere.

## License

ISC, see [`LICENSE`](LICENSE), for everything that is ours. The patch series under `games/*/patches/` modify other projects and carry those projects' licenses; each series' README names the project and the commit it is based on.
