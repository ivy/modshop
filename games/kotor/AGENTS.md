# AGENTS.md

Onboarding for coding agents working on the KotOR build. The repository's rules are in [`../../CLAUDE.md`](../../CLAUDE.md) and [`../../docs/conventions.md`](../../docs/conventions.md); this file is what is specific to this game.

## Purpose

- Build the modded KotOR 1 install (the community Full Build, KMRP, our repairs) from a pristine Steam copy and the mod archives, as a chain of keyed checkpoints, and deploy it to the handheld by content.
- Success is: nothing changed, nothing happens; one input changed, only the affected tail rebuilds and only the altered paths sync; a clean build matches the cached one; the handheld's folder never drifts from a build.

## Map

| Path | What |
| --- | --- |
| `README.md` | the complete procedure, step by step, and "When it breaks", the diagnosis notes that worked |
| `../../src/modshop/kotor/` | the code for this game: `recipe.py` (the build as entries), `steps.py`, `paths.py`, `patcher.py`, `kmrp.py` |
| `../../src/modshop/core/` | the game-agnostic chain: trees, keys, checkpoints, deploy; never imports `kotor` |
| `build/` | recipe data: `base.json` (vanilla's Steam ids and tree hash), `k1full.json` (the build's mod list), `cleanlist_k1.txt`, `recipe.json` (generated; the text that enters every key) |
| `fixes/` | our own TSLPatcher change files, applied as recipe steps |
| `repairs/` | one folder per scripted fix: `make.py` plus a README with the evidence; inputs come from the user's archives at build time |
| `patches/` | `git format-patch` series over pykotor and KMRP; `patches/README.md` names the base commits and the fork branch |
| `kmrp-build/` | building KMRP's controller module on Linux; the Wine container image for its installer |
| `docs/ideas/` | tooling not yet built, with priorities |
| `docs/research/` | measurements and findings worth referring back to, each dated and reproducible |
| `data/` | gitignored: archives, `game/` (vanilla, `ckpt/`, the work tree, `build` symlink, `legacy/`), stage, logs, `hashcache.json` |

## How to work here

All commands run from the repository root.

- Setup: `mise install && uv sync` (uv, DepotDownloader; the tool, the patcher and the patched pykotor into `.venv`).
- Build and inspect: `modshop kotor build`, `status`, `recipe show [ENTRY]`, `verify [KEY]`, `checkout KEY DIR`; `prove` rebuilds the chain uncached and compares. Every command takes `--help` and `--data DIR`.
- Deploy: `modshop kotor deploy`, and `deploy --check` for the drift report.
- Verify a code change: `mise run check` (ruff, pyright strict, pytest). The synthetic game in `../../tests/integration/` is where chain, key and deploy changes are proved before the real data sees them.
- After editing `recipe.py`: `modshop kotor recipe write`, then commit `build/recipe.json`; a test fails when it is stale.

## Change hygiene

- No mod authors' files or build outputs in git (a mod of our own may commit the game files it is made from, and keeps its recordings in Git LFS), no device identity in git (`local.toml` holds it), nothing placed in a game folder by hand: a fix is a step, a repair folder, or a patch, and the next build carries it.
- A change to a step, to any module the step runner imports, or to `uv.lock`'s patcher packages rebuilds the whole chain (about 25 minutes) by design. Edit orchestration, the command line or docs freely; edit steps deliberately, and test on the synthetic game first.
- A fix to pykotor is a commit on the fork's series branch, exported into `patches/pykotor/`, then pinned in `pyproject.toml`; see `patches/README.md`. Commit messages for upstream carry no AI attribution.
- Run the drift check before and after any debugging session on the handheld; a difference becomes a step or is reverted, never left.
- Keep `README.md` the complete procedure when something changes; diagnosis notes go beside the thing they explain, as current facts, not history.

## Where to look first

- A build or deploy question: `README.md`, then `../../docs/proposals/modshop-cli.md` (the design) and `../../docs/proposals/kotor-build-pipeline.md` (why the chain is shaped this way).
- What an entry does: `modshop kotor recipe show ENTRY`, or `recipe.py` itself.
- A crash or wrong behaviour in the game: `README.md`, "When it breaks", then the repair READMEs for the stories.
- A patcher defect: `patches/README.md` lists the six fixed so far; `data/logs/holopatcher/<entry>-<step>.log` is the run's log.
