---
title: Inspect command
priority: p0
status: idea
depends_on: []
---

# Inspect command

One script with the handful of questions that were each answered today by a fresh PyKotor one-off.

## The problem

Diagnosing the holograms took five ad-hoc scripts in one evening: list a module's placeables with their use scripts and conversations; compare a module's resources against vanilla's; decompile a script to its engine calls; find which Override files a model name resolves to; diff two 2DAs by cell. Repair 08's diagnosis wrote the same kind of scripts for models. Each took minutes to write and debug (PyKotor's resource objects name things inconsistently: `resref` here, `resname()` there), and none was kept.

The question asked most often is "what refers to this?", and nothing answers it. Finding why an area transition refuses to start while a companion lags behind (2026-10-16) was a chain of them: the message's strref (42724) → the conversation that holds it (`k_transabort.dlg`) → the placeable whose conversation that is (`k_trans_abort.utp`) → the script that spawns the placeable (`k_trg_transfail.ncs`) → the engine string that runs the script (`0x007499C4`), and from there into the disassembly. Each step was one throwaway scanner over every resource of the build, about 43,000 of them in chitin, the modules and Override, rewritten five times for the next kind of reference: a strref big-endian behind `CONSTI` in compiled scripts, little-endian in GFF fields, a resref as a string. One pass searched for the conversation's name where the script names the placeable, and reported that no script referred to it: a false negative a tool with the reference kinds built in would not make. Half the scans' matches were coincidental byte patterns in models.

## The idea

`modshop kotor inspect` with subcommands, each printing plain text an agent can read:

- `refs THING [--tree DIR] [--kind script|gff|2da|any]`: everything that refers to a strref, a resref or a tag, by the way each format refers: `CONSTI`/`CONSTS` operands in compiled scripts, `CExoLocString` strrefs and `ResRef` fields in GFFs (conversations, blueprints, area instances), cells in 2DAs. Prints the resource, where it lives (Override, module, BIF), the field or instruction, and for a GFF field its path. Models and textures are not searched: they hold no references by name that the game resolves this way, and they are where byte scans find coincidences.
- `which RESREF [--tree DIR]`: where the game would load it from (Override, then the module, then the BIFs), every case-variant that exists, and which entry introduced each (from the checkpoints' `changed.txt`).
- `module NAME [--placeables|--creatures|--scripts|--dialogs]`: the instances with the scripts and conversations they reference, and whether each reference resolves.
- `compare PATH VANILLA`: a module or archive against vanilla, resource by resource: added, removed, changed.
- `decompile RESREF`: the script's engine calls with their names from `nwscript.nss`, constants inline.
- `diff2da A B`, `diffgff A B`: by cell and by field.

This is the small, immediate end of [semantic diff](semantic-diff.md) and [asset index](asset-index.md): the same parsing, without a store, for one question at a time. Those two grow out of it rather than replacing it; `refs` is the asset index's reference graph answered by a scan, slower (a minute or two over the build) but needing nothing kept.

Commands go under `modshop kotor inspect`, since the package is where the tool lives now, and the pieces already there are reused: the game tree's case-insensitive lookup (`modshop.kotor.paths`), checkpoint keys for `--tree`, and the build's own PyKotor.

## Unknowns

- How much PyKotor's own CLI (`pykotor` diff, the holocron toolset's tools) already covers; worth an hour before writing anything.
- How long `refs` takes over the whole build, and whether it needs a cache by content hash (the [asset index](asset-index.md)'s keying) to be pleasant; the throwaway scanner took a few minutes per pass.

## First step

`refs`, reproducing the transition chain above (strref 42724 to `k_trg_transfail`) in three invocations and no false negatives; then `which` and `module`, reproducing the hologram diagnosis.
