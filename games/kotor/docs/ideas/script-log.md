---
title: A script log that works
priority: p1
status: idea
depends_on: []
---

# A script log that works

A way for a mod's scripts to report what they saw, in the shipped game, that a person or the build host can read afterwards.

## The problem

The tests in nws's world model say a script makes the right calls; they cannot say what the engine did with them. When the Juhani mod's companions ignored the player after the fight (2026-10-17), the plan was a diagnostic build that posted each companion's state on screen at every step (`AurPostString`: commandable, AI off, in a conversation, every effect and its creator), so the next session's recording would show where the recovery broke. The assumption came from the game's own debug helper, which calls `AurPostString` only when `!ShipBuild()`, and was read as "it draws in the shipped game". It does not: the recording showed no text at all, even at steps that certainly ran. The build, a deploy and one of the owner's play sessions bought nothing.

What answered the question was a save: the companions' local boolean 62 (`SW_FLAG_AI_OFF`) set, read from the save with pykotor ([device state](device-state.md)). A save holds state but not history: what happened in which order is still unanswered by anything.

## The idea

Candidates, each to be proved on one line before anything relies on it:

- **`SendMessageToPC`** to the game's feedback log, which the player can open and the recording catches; whether K1's feedback screen shows script messages is not known.
- **Globals as a log**: a mod declares a few `OAJ_TRACE_*` numbers or strings in `globalcat.2da` and writes into them; any save then carries the trace, and [device state](device-state.md) prints it. Costs nothing at run time and needs no screen.
- **The debug channel itself**: `ShipBuild()` is a routine; a KPM hook making it return false would turn on every `Db_PostString` in the game's own scripts too, which may be more noise than signal.

## Unknowns

- Which of these display or persist in this build under Proton.

## First step

One script, run from a dialogue line, that does all three; play it once and look.
