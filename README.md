# modshop

Scripts, patches and notes for building modded games on Linux, written so that someone with none of the context can clone this and reproduce the result from their own copies of the game and the mods. One directory per game under `games/`; shared helpers under `tools/`.

**Nothing in this repository is a game file or a mod file**, and nothing here will download one for you that you could not get yourself. The scripts take the archives you fetched from the mods' own pages, the game you own through Steam, and build the modded install from those. Fixes to mods are expressed as scripts that patch the mod's bytes at build time, never as patched copies.

## What is here

| Path | What |
| --- | --- |
| [`src/modshop/`](src/modshop/) | the `modshop` command: a chain of keyed checkpoints built from a pristine game and the mod archives, deployed to the handheld by content; `core/` is game-agnostic, one subpackage per game beside it |
| [`games/kotor/`](games/kotor/) | Knights of the Old Republic (Steam, Proton): the community Full Build installed by script, the KMRP interface and controller patch built on Linux, repairs for things that break under Proton, and the diagnosis notes behind them |
| [`plugins/`](#claude-code-plugins) | Claude Code plugins, one per game, published from this repository as a marketplace |
| [`tools/restore-window/`](tools/restore-window/) | un-minimize a wine game that lost its window under gamescope, where there is no taskbar to get it back |
| [`docs/conventions.md`](docs/conventions.md) | the rules every game directory follows: what goes in git, where data lives, how fixes to other projects are kept |

## Quick start

1. Clone, `mise install` (uv, Rust and the Steam downloader), `mise run nws:build` (the NWScript compiler), `uv sync` (the tool and the patcher), then read the game's README: `games/kotor/README.md` is the whole procedure for that game.
2. Copy `local.example.toml` to `local.toml` and fill in your machine names and paths. The docs say "the handheld" and "the build host"; that file says which is which for you.
3. Each game keeps its archives, game copies, logs and build outputs under `games/<game>/data/`, which git ignores. The scripts find it by default; `KOTOR_DATA` (for KotOR) points them elsewhere.

## Claude Code plugins

This repository is also a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/overview) named `modshop`, listed in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Its plugins carry what we learned working on each game's files, for an agent to use on anyone's copy of the game; they contain no game or mod data. Add the marketplace once in a Claude Code session, then install a plugin by name:

```text
/plugin marketplace add ivy/modshop
/plugin install kotor@modshop
```

| Plugin | What |
| --- | --- |
| [`kotor`](plugins/kotor/README.md) | Knights of the Old Republic: reading, searching and patching the game's files with PyKotor, and debugging the game under Proton |

Each plugin's README covers its requirements, the other install scopes, and updating. Working in this repository needs no install: [`.claude/settings.json`](.claude/settings.json) registers the marketplace and enables its plugins for the project.

## License

ISC, see [`LICENSE`](LICENSE), for everything that is ours. The patch series under `games/*/patches/` modify other projects and carry those projects' licenses; each series' README names the project and the commit it is based on.
