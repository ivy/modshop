# AGENTS.md

Onboarding for coding agents working in this repository. Read [`docs/conventions.md`](docs/conventions.md) first; it is short and it is the part that is not derivable from the tree.

@AGENTS.local.md

## What this is

A public repository of scripts, patches and notes for building modded games on Linux, one directory per game under `games/`. Its reader has none of our context, so every document here is written for them. The person who owns it plays on a handheld running a SteamOS-like distribution and builds on a separate Linux machine; `local.toml` (gitignored) names those machines for you, `AGENTS.local.md` (gitignored, may be absent) describes them, and the docs call them "the handheld" and "the build host".

## The three rules

1. **No game or mod bytes in git.** Archives, game copies, build outputs, logs and venvs live under `games/<game>/data/`, ignored by git. A fix to a mod is a script that patches the mod's file at build time, taking the input from the user's own archive; the patched result is never committed either.
2. **No device identity in git.** Hostnames, usernames, home paths, account ids, tailnet names. They go in `local.toml` or `AGENTS.local.md`; the docs use the role names.
3. **Reproducible and idempotent.** The modded install is built by script from a pristine copy of the game and the archives, every fix is a replayable step, and a problem is fixed in the tool or the mod rather than worked around by hand in the game folder. Nothing is edited in the game folder without a script that reproduces it.

## Fixes to other projects

Kept kernel-maintainer style: one commit per fix with the reason in the message, on a local branch over the upstream commit it was written against, in a clone under `~/src/<host>/<owner>/<repo>`, exported with `git format-patch` into `games/<game>/patches/<project>/`. The series' README names the base commit. `git am` applies it to a fresh clone; a `patch -p<N>` applies it to an installed package. When upstream takes a patch, it leaves the series on the next rebase. Commit messages for upstream carry no AI attribution.

## Working here

- The code is one Python package, `src/modshop/` (`core/` knows nothing about any game; `kotor/` is the game; `cli/` is the command surface), with the command `modshop kotor <command>`. `uv sync` makes its environment; `mise run check` runs ruff, pyright strict and the tests, and a change is not done until it passes. The design and its reasons: `docs/proposals/modshop-cli.md`.
- Reverse engineering: `mise install` provides [REA](https://github.com/morluto/rea), Ghidra 12.1 with JDK 21, and Rizin. `.mcp.json` registers `rea mcp` for this repository, and `.claude/skills/reverse-engineer-anything` is REA's skill, copied from the pinned package by `mise run rea:skill`; rerun it after bumping `rea-agents`. Don't run `rea setup` or `rea update`: they write user-level agent configuration outside this repository. Analysis of game binaries is derived from game bytes, so anything it writes into the tree goes under `games/<game>/data/`. KotOR's executable is encrypted on disk; `modshop kotor re dump` takes the decrypted code from the running game into `data/re/` ([`games/kotor/README.md`](games/kotor/README.md), "When it breaks").
- Game-specific procedure: `games/<game>/README.md`. It is the complete how-to; keep it that way when something changes.
- Diagnosis notes live beside the thing they explain (a repair's README, a tool's README), not in a separate log.
- Documents state current facts, not their history; revision narration belongs in commit messages.
- Markdown: one paragraph per line, no hard wrapping.
- Commits: small and coherent, conventional-commit subjects.
