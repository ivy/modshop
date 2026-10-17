---
name: debug
description: Use when KotOR (Knights of the Old Republic) crashes, hangs or misbehaves under Proton/Wine on Linux or a Steam Deck-like handheld, when a controller (KMRP's pad module) does nothing on some screen, or when the answer is in swkotor.exe itself — reading a Proton log or glibc heap abort, getting a native stack with gdb, symbolizing Mesa/Wine frames, dumping the SteamStub-encrypted executable, finding an engine function or hook point.
when_to_use: The game crashed at a place, a log shows "Assertion failed" or "free(): invalid pointer", a button or stick works with the keyboard but not the pad, which function decides X in the engine, attach a debugger to the game, a crash only one screen triggers.
allowed-tools:
  - Read
---

# Debugging KotOR under Proton

**Autonomy:** model-invocable · guidance only; the steps it leads to read the device and attach a debugger, and a capture that catches an abort kills the already-dying game

## Arguments
```
$ARGUMENTS
```

## First, whatever the symptom

- **Save the evidence before anyone relaunches.** Proton rewrites its log at every launch. Copy the log, KMRP's logs and the build's identity first ([`evidence.md`](references/evidence.md)).
- **A reproduction costs the player real time.** Before asking for one, have the capture ready and proven on a dummy process, and say exactly what to do and what to note.
- **Victim versus culprit.** The frame that aborts noticed the corruption; it rarely caused it. glibc's heap belongs to the native side (Mesa, Wine's Unix libraries); the game and its mods allocate from Wine's heaps.
- **A workaround is not a diagnosis.** When the game ignores something or does something the scripts don't explain, find the decision in the engine ([`engine.md`](references/engine.md)) or the state it acted on in a save ([`evidence.md`](references/evidence.md)) before changing approach. Routing around it hides the cause and usually costs another play session later.
- **Never edit the device's game folder by hand.** A diagnostic setting belongs in the build; a hand edit is drift and gets reverted under you.

## Then, by symptom

| Symptom or question | Read |
|---|---|
| Crash: what the logs say, where evidence lives, the device over ssh | `evidence.md` |
| Crash: a native stack at the abort; symbolizing it | `gdb.md` and `${CLAUDE_SKILL_DIR}/scripts/` |
| Crash: no stack yet; does it follow a place, what loads there, clearing a library | `isolate.md` |
| A pad button or stick does nothing where the keyboard works | `controller.md` |
| A (or a tap) on a creature does nothing; a companion won't talk | `controller.md`, "A on someone in the world", then a save (`evidence.md`) |
| A script behaves in game unlike its tests; what state a creature or the story is in | `evidence.md`, "A creature's state in a save" |
| Which engine function decides something; an address; a hook; a crash frame in the game | `engine.md` |
| A question about the game's files (who refers to a strref, which copy loads) | [`/kotor:pykotor`](../pykotor/SKILL.md) |

Read only the file the question needs, from `${CLAUDE_SKILL_DIR}/references/`. The scripts are in `${CLAUDE_SKILL_DIR}/scripts/`; where a reference says `scripts/...` or `SKILL_DIR`, it means that directory.

## Reach a verdict

End every step with what is **established** (with the evidence: a log line, a frame, an address, a count of reproductions), what is **not**, and the one next piece of evidence that would decide it. A candidate fix stays a candidate until the same route is played with and without it.

## Examples

- "The game crashed opening the workbench" → `evidence.md` (save the Proton log, read the glibc message), `isolate.md` (does it follow the screen, what loads there), then `gdb.md` for the next reproduction.
- "Y does nothing in combat" → `controller.md` (registration versus delivery, the click handler's gate), a live read of the button's drawn flag.
- "Why can't I leave the area with a companion far away?" → `/kotor:pykotor` follows the message to `k_trg_transfail`, then `engine.md` from the engine string to the check that calls it.
