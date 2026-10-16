---
title: Inspect command
priority: 1
status: idea
depends_on: []
---

# Inspect command

One script with the handful of questions that were each answered today by a fresh PyKotor one-off.

## The problem

Diagnosing the holograms took five ad-hoc scripts in one evening: list a module's placeables with their use scripts and conversations; compare a module's resources against vanilla's; decompile a script to its engine calls; find which Override files a model name resolves to; diff two 2DAs by cell. Repair 08's diagnosis wrote the same kind of scripts for models. Each took minutes to write and debug (PyKotor's resource objects name things inconsistently: `resref` here, `resname()` there), and none was kept.

## The idea

`tools/inspect.py` with subcommands, each printing plain text an agent can read:

- `which RESREF [--tree DIR]`: where the game would load it from (Override, then the module, then the BIFs), every case-variant that exists, and which entry introduced each (from the checkpoints' `changed.txt`).
- `module NAME [--placeables|--creatures|--scripts|--dialogs]`: the instances with the scripts and conversations they reference, and whether each reference resolves.
- `compare PATH VANILLA`: a module or archive against vanilla, resource by resource: added, removed, changed.
- `decompile RESREF`: the script's engine calls with their names from `nwscript.nss`, constants inline.
- `diff2da A B`, `diffgff A B`: by cell and by field.

This is the small, immediate end of [semantic diff](semantic-diff.md) and [asset index](asset-index.md): the same parsing, without a store, for one question at a time. Those two grow out of it rather than replacing it.

## Unknowns

- How much PyKotor's own CLI (`pykotor` diff, the holocron toolset's tools) already covers; worth an hour before writing anything.

## First step

`which`, `module` and `compare`, reproducing today's hologram diagnosis as three commands.
