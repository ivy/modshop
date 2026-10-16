---
title: Device fixtures
priority: p1
status: idea
depends_on: [virtual-gamepad]
---

# Device fixtures

A fixture is a save game plus a scripted action that together reproduce one symptom on the handheld: "load a save outside the Upper City North door and walk south" is repair 08's; "open the workbench upgrade screen" is repair 07's. A fixture turns a crash from something someone has to play into something a script can check.

## The problem

Every diagnosis so far has needed a person on the device. Repair 08's cause was found by testing variants "one at a time on the device" ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). Repair 07 is still a candidate because the route that crashed (Endar Spire into the apartment) and the route that did not (a save inside the apartment) have not been compared under the same build ([its README](../../repairs/07-kmrp-pot-gui-textures/README.md)). Without a reproducible symptom, nothing that depends on running the game — a crawl, a bisect, an A/B of a repair — can be automated.

Controller work pays this cost on every fix, not only on crashes. The swoop race (KMRP pull request 62), character generation's stick (pull request 64), the dialogue stick and the movement vector (pull requests 60 and 59) were each built in minutes and then waited on someone reaching the place and playing it; the Y-in-combat question is waiting the same way. A save at a swoop track, one in a fight with actions queued, and one at character generation would have been three fixtures that each fix used more than once.

## The idea

- **Saves built, not collected.** PyKotor reads and writes save games (`pykotor.extract.savedata`). A save generated from the build's own module files does not carry the stale area state a played save does; the [game README](../../README.md) already warns that areas a save has visited keep their old state after a deploy.
- **A way into an area.** The game's debug console can warp to a module when cheats are enabled in `swkotor.ini`. A fixture can start from any save and warp, or from a save placed in the area.
- **A way to act.** Keyboard and mouse through `xdotool`: the game's window is on display `:1` under gamescope and `xdotool` reaches it ([`tools/restore-window`](../../../../tools/restore-window/README.md)). Pad input through a [virtual gamepad](virtual-gamepad.md), which is what a controller fixture needs: the bug is in how a pad's input reaches the engine, so keyboard events would test something else.
- **A verdict.** For a crash, pass is the game still running a fixed time after the action, and fail is the process gone, with the capture from [crash capture](crash-capture.md) attached. For behaviour, pass is the expected lines in KMRP's events log (with `[kmrp] debug_logs = 2` in `local.toml`) or the expected values from a [live probe](live-probe.md).

A fixture is a small file in this repository (the save's recipe, not the save; the actions; the timeout) and runs against whatever is deployed.

## Unknowns

- Whether warping works under this build with KMRP installed, and whether a warped arrival exercises the same path as walking in (repair 08's crash depended on which door).
- Whether synthetic keyboard input reaches the game under gamescope reliably; pad input has its own unknowns ([virtual gamepad](virtual-gamepad.md)).
- How much of a save PyKotor can write correctly; see [round-trip tests](roundtrip-tests.md).

## First step

One fixture, by hand-built steps: launch the deployed game, load a save, warp to `m02ac`, wait thirty seconds, report whether `swkotor.exe` is still running. Run it against the build with and without repair 08; the first should pass and the second fail.
