# `/kotor:debug` — Debugging KotOR under Proton

Gives Claude the playbook for a KotOR crash or misbehaviour under Proton on Linux: what evidence to save and where it lives, how to get a native stack at a glibc abort without losing the reproduction, how to name the frames, how to narrow a crash with no stack, why a pad does nothing on one screen, and how to read the engine's own code. It loads one short index, then the reference the problem needs.

```text
/kotor:debug the game crashed when I opened the workbench
/kotor:debug the left stick doesn't work in character generation
/kotor:debug which engine function refuses the area transition?
```

Claude also loads it on its own when a KotOR crash, a Proton log or a controller problem comes up.

## Why this exists

Each of these cost a session real time, most of it the player's:

- **Evidence lost to a relaunch.** Proton rewrites its log at every launch; the crash that prompted the work is gone the moment someone tries again.
- **A lost reproduction.** A gdb attach that looked fine detached before the crash, three ways: batch mode returned from `continue` at once, a queued `quit` was read while the game ran, and an error in a command list skipped the rest. The player replayed 45 minutes to get back to the crash, and the capture caught nothing. The script here was then proven on a dummy process before the next attempt.
- **The victim taken for the culprit.** glibc aborts where it *notices* heap damage. Reading the frame as the cause, or blaming the game for a heap only native code uses, sends the search the wrong way.
- **Frames with no names.** gdb on the device shows `?? ()` for Mesa and the runtime's libraries; the names were in each library's embedded `.gnu_debugdata` all along.
- **"Registered" read as "works".** KMRP's axes were registered in every input class and polled in none of the minigame's; the swoop race and character generation took the pad's input nowhere for the same kind of reason.
- **Rediscovered engine facts.** SteamStub encryption, which process to read, KPM's hook calling convention and a dozen engine addresses were each found from scratch.

## How it works

`SKILL.md` is the index: the four rules that apply to every problem, a table from symptom to reference, and the verdict each step ends in. The references and scripts:

| File | Covers |
| --- | --- |
| [`evidence.md`](references/evidence.md) | the Proton log and glibc messages, KMRP's logs, recordings, the device's process and shell traps |
| [`gdb.md`](references/gdb.md) | the abort capture, why each part of it is there, symbolizing afterwards |
| [`isolate.md`](references/isolate.md) | narrowing without a stack: place, scripts, mods, textures, clearing a library under ASan, A/B |
| [`controller.md`](references/controller.md) | input classes, event ownership, where a pad's input stops, live reads |
| [`engine.md`](references/engine.md) | dumping and reading `swkotor.exe`, names from KMRP, known addresses, KPM hooks |
| [`scripts/catch-abort.gdb`](scripts/catch-abort.gdb), [`scripts/symbolize.py`](scripts/symbolize.py) | the tested capture, and address → library → function from a maps file and copied libraries |

It works alongside [`/kotor:pykotor`](../pykotor/README.md), which answers the questions about the game's files that a diagnosis keeps running into.

## Where the facts come from

KotOR 1 from Steam under Proton 11 on a Bazzite handheld (Mesa 25.2.4, radeonsi), with KMRP 1.5.1 and the Full Build, in October 2026; the swoop, character generation and party-transition investigations and two workbench crashes. What was not run is marked so in the reference files. Other Proton versions, GPUs and distributions will differ in library paths and symbols; re-check the gdb setup on a dummy process before relying on it.
