---
title: Device state and saves
priority: p0
status: idea
depends_on: []
---

# Device state and saves

One command on the build host that brings back what the handheld knows right now: the current save, decoded; the logs; the deployed checkpoint; the drift report.

## The problem

When the holograms failed, the question "is this puzzle disabled by the save's state?" could not be answered: the save is on the handheld, excluded from every sync, and nothing reads it. The engine logs nothing about scripts, so the save and the module are the only evidence, and only the module was reachable. The [game README](../../README.md#when-it-breaks) lists four places evidence lives on the device, and each is fetched by hand with a different command.

On 2026-10-15/16 KMRP's events log was fetched by hand over ssh three times (the swoop race, character generation, the debug-level checks), each with its own `grep`. One count came out wrong because the log's lines end in CRLF and `grep 'fire$'` matched nothing. Turning the log on is a build setting now (`[kmrp] debug_logs` in `local.toml`, carried by the deploy); fetching and reading it is not.

On 2026-10-17 a save answered three questions about the Juhani mod that had resisted everything else, each in minutes, and each read by a script written for the occasion (four in all):

- **Why the companions ignored the player after the fight.** Their creature records in the grove's module state (`SAVEGAME.sav` → `danm14ac.sav` → `m14ac.git` → `Creature List`) were `Commandable` 1, neutral, carrying no effect of Juhani's, but `SWVarTable.BitArray` had `0x40000000` in its second word: local boolean 62, `SW_FLAG_AI_OFF`. Before the save was read, the same symptom had cost a workaround, a diagnostic build whose output never showed ([script log](script-log.md)), and two live-debugger attempts, one of which froze the game ([live probes](live-probe.md)).
- **Why the mod's scripts never recognised them as down.** The same records gave their tags as the world has them, `carth` and `mission`, where the party blueprints say `Carth` and `Mission`; the mod compared tags case-sensitively.
- **Why the banter never started.** Party members are saved in the outer archive's `AVAILNPC<n>.utc`, with their `ActionList`: Mission's held a standing action (61) with the banter's `ActionStartConversation` queued behind it for ever.

The cost of not having this: each reader took ten to twenty minutes to write against pykotor's structures (which list holds party members, the bit order of `SWVarTable` and of `GLOBALVARS`, a `None` from a list that was not there), and the hour before the first one was spent on guesses.

## The idea

`modshop kotor fetch`: copy the newest saves, Proton's log, KMRP's logs (line endings normalised, the raw file kept beside it) and the drift report into `data/logs/device/<timestamp>/`, and print a summary: which checkpoint is deployed and whether it drifted, which save is newest and where the player is, and the save's globals and visited modules decoded with PyKotor (`pykotor.extract.savedata`), so a question like "has `Tar_HoloActive` been set" is one grep.

`modshop kotor save SAVE [--module M] [--creature TAG]` prints a save's state readably: globals by name (booleans from `ValBoolean`, most significant bit first); the party table; for a creature, wherever it is kept (a module's `Creature List`, the module's own list, or `AVAILNPC<n>.utc` for party members), its tag as the world has it, `Commandable`, faction, animation, effects with type, subtype and creator (named when the creator is an object in the save), local booleans and numbers by index (and by `SW_FLAG_*` name for the AI's), and the action queue with its parameters; the module's pending `EventQueue`. [Crash capture](crash-capture.md) is the automatic, per-run version of the same folder; this is the on-demand one, and the decoding is shared.

## Unknowns

- How complete PyKotor's save reader is for K1 saves made by this build with KMRP installed.

## First step

`modshop kotor save` over one save, reproducing the three findings above from its output alone; then the fetch.
