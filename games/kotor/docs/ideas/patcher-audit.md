---
title: Patcher audit
priority: 1
status: idea
depends_on: []
---

# Patcher audit

After every HoloPatcher step, check that what its log claims happened is what the tree now holds, and fail the entry when it is not.

## The problem

Six of the six PyKotor defects in [`../../patches/pykotor/`](../../patches/pykotor/README.md) were silent or nearly so, and the worst two were found by playing. Patch 3's tables were written back empty with no error. Patch 6 is the clearest case: for every `Replace#=` into a module archive the log said "replacing existing file in the 'modules\tar_m03ad.mod' archive" and the archive kept the old bytes, in both the hand build and the chain, across hundreds of replacements per build and most of the Community Patch's module fixes. It was found because one puzzle's holograms stopped responding and the module's script hashed to vanilla's ([patches README](../../patches/pykotor/README.md), item 6). The [k1cp fix](../../build/fixes/k1cp-sithtroop/README.md) is another edit the patcher failed to make.

The patcher's log is a list of claims. Nothing reads it back against the tree.

## The idea

A check that runs as part of the `holopatcher` verb in [`build.py`](../../build/build.py), after the run and before the checkpoint, over the step's own log:

- **InstallList**: for "copying X and saving to the F folder" and "replacing existing file in the A archive", the file in the folder, or the resource in the archive, hashes equal to the mod's source file.
- **2DAList**: for every `ChangeRow`/`AddRow`/`AddColumn`, re-read the table and confirm each named cell holds the value the ini gave (memory tokens resolved from the log's own `2DAMEMORY` notes).
- **GFFList**: re-read the file and confirm each field the ini sets.
- **TLKList**: the appended strings exist at the indices the log reports.
- **CompileList**: every script the ini lists exists compiled at its destination.

A mismatch is an error for the entry, with the claim and what was found. The check is cheap: it reads only what the step touched, and the `changed.txt` the checkpoint already computes is a cross-check (a claim about a path that did not change is a mismatch by itself).

## Unknowns

- How much of the ini's semantics the checker must reimplement to know what to expect; starting with InstallList and `ChangeRow` on named cells covers the two failures seen.
- Whether the log is stable enough to parse, or whether the check should hook HoloPatcher's own patch objects instead (PyKotor's `ModInstaller` exposes them, which is cleaner and version-bound).

## First step

InstallList claims only, as a script over one step's log and tree, run against the Movie-Style Holograms entry on a checkout of its parent with the unpatched venv: it must report the six scripts as claimed-but-absent.
