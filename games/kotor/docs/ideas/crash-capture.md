---
title: Crash capture
priority: p2
status: idea
depends_on: []
---

# Crash capture

Every run of the game on the handheld leaves one folder with everything needed to diagnose it, collected without anyone remembering to.

## The problem

The evidence for a crash lives in four places, and some of it disappears ([`../../README.md`](../../README.md#when-it-breaks)):

- Proton's log is rewritten at every launch, so it has to be copied before the next one; the README's answer is a loop around `pgrep -x swkotor.exe`.
- KMRP's logs record the pad and the engine's movement fields on the same clock as Proton's log, when the build sets `[kmrp] debug_logs` in `local.toml`; their lines end in CRLF.
- Steam's background recording holds the screen in 3-second chunks, which have to be concatenated and cut into frames with `ffmpeg` to see what was on screen at the crash.
- The deployed checkpoint's key says which build crashed.

Today these are gathered by hand after the fact, when they are gathered at all.

## The idea

A small service on the handheld that watches for `swkotor.exe`, and when it exits writes a folder named by time and checkpoint key holding Proton's log, KMRP's logs, the recording chunks covering the last minute cut to a clip and a strip of frames, and the exit status. [Device fixtures](device-fixtures.md) attach the folder to their verdict; manual play gets the same folder without asking. A command on the build host fetches the folders, so an agent can read a crash without anyone copying files.

## Unknowns

- How long Steam keeps background recording chunks, and whether their names map to wall-clock time without reading the containers.
- Whether the capture needs to run inside the Steam session for access to the recording directory.

## First step

Turn the README's `pgrep` loop into a script that copies Proton's log and KMRP's logs into a folder named by time and the deployed checkpoint key, and run it as a user service on the handheld.
