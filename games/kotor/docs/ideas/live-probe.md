---
title: Live probes
priority: p1
status: idea
depends_on: [engine-symbols]
---

# Live probes

Read named engine state from the running game on the handheld, once or as it changes, without a debugger and without writing anything.

## The problem

Some questions are about what the engine holds at a moment of play, and neither the code nor the logs answer them:

- **Y in combat** (open, 2026-10-16): the engine's handler for Y returns early unless BTN_CLEARONE carries its "drawn" bit (`[CSWGuiMainInterface+0x6D14] & 2`), and KMRP's controller checks the same bit before pressing it. Whether the bit is set while actions are queued decides where the press is lost. Answering it took a hand-written reader of `/proc/<pid>/mem` that follows the GUI manager (`0x007A39F4`) to its panel array (`+0x88`, count at `+0x8C`), finds the main interface by its vtable (`0x00753F50`) and prints two fields when they change. Its first version died on `/proc/1/maps` (permission denied), the same process-selection trap the first image dump fell into with the pressure-vessel wrapper.
- **The swoop race**: which input class the minigame runs in, and what reaches its control vector, were read from the disassembly and then confirmed only by playing a race with debug logs on.

KMRP's logs answer what the controller module chooses to log; a probe answers anything with an address.

## The idea

`modshop kotor re peek EXPR... [--watch SECONDS] [--interval MS]`, where an expression is a pointer path over names from [engine symbols](engine-symbols.md):

```text
modshop kotor re peek 'gui_manager->panels[*]{vtable=main_interface}.+0x6D14:u8' --watch 300
```

- Runs the same way `re dump` does: a Python program fed to the handheld's `python3` over ssh, finding the Wine process by its image mapping, reading `/proc/<pid>/mem`, writing nothing.
- `--watch` prints a line with a timestamp whenever any value changes; the timestamps are `GetTickCount` milliseconds, the clock KMRP's events log and the Proton log share, so a probe line and a log line from the same moment line up.
- Output is kept under `data/re/probes/` with the expressions, so a finding is evidence that can be cited.
- Read-only by construction: no `ptrace`, no writes; a probe cannot change what it measures.

## Unknowns

- How much expression language is worth having: pointer chains, array scans with a match, and fixed-width reads cover every probe written so far.
- Sampling: a state that lasts a frame can fall between two reads at 50 ms; a tighter interval costs the handheld little but is still sampling, not tracing.
- Whether Steam's sandboxing ever prevents reading `/proc/<pid>/mem` as the same user; `ptrace_scope` is 0 on the handheld today.

## First step

The Y probe as `re peek` with raw addresses, before symbols exist, run during a fight with actions queued.
