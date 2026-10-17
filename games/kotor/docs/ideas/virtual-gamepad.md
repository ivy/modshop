---
title: Virtual gamepad
priority: p1
status: idea
depends_on: []
---

# Virtual gamepad

Play a scripted sequence of pad input into the game on the handheld, through a device Steam Input treats as a gamepad, so a controller fix can be checked without a person holding the device.

## The problem

Every controller fix needs someone to play it, and that was the most expensive step of each one:

- **The swoop race** (KMRP pull request 62): the fix was built in minutes; checking it meant the player reaching a swoop track, racing, and reporting which way the bike leaned, and the debug log was read afterwards.
- **Character generation** (KMRP pull request 64): checked by starting a new game and trying every screen with the stick and the D-pad.
- **Y in combat** (open): waiting on the player to be in a fight with actions queued.
- **The dialogue stick and the movement vector** (pull requests 60 and 59) were checked the same way.

The session's waiting was mostly on these. [Device fixtures](device-fixtures.md) plan input through `xdotool`, which sends keyboard and mouse events: the right thing for a crash fixture, the wrong thing here, because the bug is in how a pad's input reaches the engine. KMRP reads the pad through SDL behind Steam Input's Gamepad template ([`../../README.md`](../../README.md), section 6), so the input has to arrive as a pad.

## The idea

- **A uinput device on the handheld** that presents itself as an Xbox controller (the vendor and product ids Steam recognises), created by a small program run over ssh for the duration of a script.
- **A script format** of timed pad states: buttons pressed and released, stick positions, trigger values, with waits. The swoop check becomes "A; left stick at −0.6 for 2 s; +0.6 for 2 s; A".
- **Expectations from the logs and probes**, not from a screen: with `debug_logs = 2`, KMRP's events log records the pad and the module's decisions ("minigame type 1 … stick x=… fire"), and a [live probe](live-probe.md) reads the engine's side. A script passes when the expected lines and values appear.
- **Getting to the place** is a [device fixture](device-fixtures.md)'s job (a save at the swoop track, in a fight, at character generation); this is the input half they share.

## Unknowns

- Whether Steam Input picks up a uinput pad created while the game runs, and whether it maps it with the same template as the built-in controls; the Ally X's own pad arrives through the Handheld Daemon's virtual controller, which is the precedent.
- Whether the real pad has to be released or disabled so the two do not fight, and how a script avoids leaving a button held if it is interrupted (the program must release everything on exit).
- Timing: SDL polls, KMRP reads once per frame, so a press shorter than a frame can be missed; scripts hold each state for several frames.

## First step

From an ssh session, create a uinput Xbox pad, press A at the main menu, and look for the press in `kmrp-controller-events.log` with `debug_logs = 2`.
