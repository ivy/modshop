---
title: Engine tables
priority: p2
status: idea
depends_on: [engine-symbols]
---

# Engine tables

The numbers the game's files use whose meanings live only in the executable, recovered once by reverse engineering and kept as data beside the [asset index](asset-index.md).

## The problem

Three such tables came up while making the Juhani mod (2026-10-16/17), and each was worked around instead of read:

- **Dialog animations.** A dialogue node's `AnimList` names animations by number (10040, 10042, 10055, 10124, 10148, and 1200-1202 for one creature's own). They are not `animations.2da`'s rows plus 10000: 10055 gets a prone character up in `banter.dlg`, and row 55 is `drink`. The script wanted Juhani kneeling in her defeat; no number for kneeling could be found (one search of every dialogue for "kneel" in comments found only Zaalbar's custom 1202), so the kneel was dropped and she stands.
- **Effect types in saves.** A save's `EffectList` gives each effect an engine type (68, 76, 10, 13, 26, 36, 83 on the companions) that is not the script's `EFFECT_TYPE_*` numbering; reading which effects a companion still carried meant guessing from creators and subtypes.
- **Placed cameras.** A cutscene node names a camera by id; what it frames is known only by playing. Camera 13 was chosen for "the three Juhanis" from its use in the game's own cutscene and showed only ground; finding that cost a play session.

## The idea

- The dialog animation table: find where the engine resolves an `AnimList` number (from the conversation code reached by `ExecuteDialogue`-like routines, with [engine symbols](engine-symbols.md)) and dump it to `data/re/tables/dialog-animations.json`: number, animation name, looping or not.
- The effect type table: the engine's effect constructors write their type; the mapping from script routine to engine type falls out of decompiling each `Effect*` routine's implementation.
- Cameras: compute from the `.git`'s camera position and orientation which objects and waypoints fall in its field of view, so a camera is chosen by what it frames, not by its number.

## Unknowns

- Whether the dialog animation table is a static array or built from a resource at start.

## First step

The dialog animation table, starting from where 10055 is handled.
