---
name: pykotor
description: Use when reading, searching or changing Knights of the Old Republic (KotOR, K1/TSL) game files with PyKotor — resources in chitin/BIFs, Override, modules (.mod/.rim/.erf), 2DA, GFF blueprints and dialogs (utc/utp/dlg/git), TLK strrefs, textures (tpc), models, NSS/NCS scripts — or when finding what refers to a strref, resref, tag or script, or inspecting or installing a TSLPatcher/HoloPatcher mod.
when_to_use: Questions like which file the game loads, what uses this strref, who runs this script, read this 2da, edit this utc, compile this nss, disassemble this ncs, what does this changes.ini do, install this mod headless; any script importing pykotor or holopatcher.
allowed-tools:
  - Read
---

# PyKotor by task

**Autonomy:** model-invocable · guidance only; the scripts it leads to read the game and write only to scratch copies

## Before any script

- Use the Python that has pykotor: the project's environment if it pins pykotor (`uv run python`, `.venv/bin/python`), else a venv with `pip install pykotor`. Check `pip show pykotor`: these notes are for 2.3.12, and the version matters (see the stock-vs-patched traps in each file).
- Run with `python -I` from a scratch directory, with `import logging; logging.disable(logging.CRITICAL)` before any pykotor import and `2>/dev/null`: pykotor logs on every path miss and creates `logs/` in the current directory.
- Never write into the game folder or a mod's extraction. Before anything that writes (a patcher install, a capsule rebuild), make the copy first, `cp -a --reflink=auto SRC DST`, and point the script at the copy.
- Build one `Installation` per script and reuse it: indexing costs seconds, lookups after that are sub-millisecond.

## Open the reference for the task

Read only the file the task needs, from `${CLAUDE_SKILL_DIR}/references/`:

| Task | File |
|---|---|
| Find a resource, which copy the game loads, iterate everything, open a .mod/.rim/.erf, strref → text | `installation.md` |
| Read or edit 2DA, GFF, a blueprint or dialog, TLK, ERF/RIM, a texture, model, walkmesh; raw header offsets | `formats.md` |
| What refers to a strref, resref, tag or script; following a chain of references | `references.md` |
| Read, disassemble or compile NSS/NCS | `scripts.md` |
| Inspect what a TSLPatcher mod will do, install it headless, read its log | `tslpatcher.md` |
| A one-line shell answer with the `pykotor` command | `cli.md` |
| A save's globals, party, or a creature's tag, effects, local variables and action queue | [`/kotor:debug`](../debug/SKILL.md)'s `evidence.md`, "A creature's state in a save" |

## Traps that cross every area

- **Three object shapes.** `ResourceResult`/`LocationResult` have attributes (`.data`, `.filepath`); `FileResource` has methods (`.data()`, `.resname()`, `.restype().extension`); `Capsule.resource()` returns bare bytes.
- **`inst.resource()` doesn't apply `.mod`-over-`.rim`.** It can return the `.rim` copy the game ignores. Use `pykotor.common.module.Module`, or `location()` and prefer the `.mod`.
- **Iteration is narrower than lookup.** `for r in inst` and every reference finder skip `patch.erf`, `rims/`, `TexturePacks/` and the stream folders; `resource()` does see `patch.erf`.
- **Generic writers default to `Game.K2` and rewrite the field set.** A K1 creature or dialog written through `write_utc`/`bytes_dlg` gains and loses fields. To change a few fields, edit the raw GFF: it round-trips byte-identically.
- **GFF getters never raise** (a missing field returns the default), and `get_struct`/`get_list` return copies; use `s["Label"]` for the live object.
- **`get_decoded()`/`decode()` are broken**: they return `str(obj)`. Parse `.data` with the format's `read_*`.
- **No decompiler**, and the built-in compiler pushes engine-call arguments in the opposite order from BioWare's. Treat pykotor-compiled scripts as unverified until tested in game.
- **A reference search is per name.** A dialog, the placeable that opens it and the script that spawns it usually have different names; search all of them, and remember matching is whole-value (`x` doesn't match `x1`).

## When the resources run out

If nothing in the resources refers to the last name in a chain, the engine runs it by name: search the executable's strings. Steam's `swkotor.exe` is encrypted on disk, so its code has to come from the running process. `/kotor:debug` covers that, from the engine string to the function that uses it (its `engine.md`).

## Examples

- "Why does the game say 'You must gather your party'?" → `references.md`: strref → dialog → placeable → script, every name searched in one pass.
- "Change which conversation a creature in one module uses" → `installation.md` (find the copy the game loads, via `Module`) then `formats.md` (edit that raw GFF field).
- "Will this mod's changes.ini clobber another mod's 2DA rows?" → `tslpatcher.md`, inspect without installing.
