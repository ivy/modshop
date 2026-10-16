---
title: Device state fetch
priority: p1
status: idea
depends_on: []
---

# Device state fetch

One command on the build host that brings back what the handheld knows right now: the current save, decoded; the logs; the deployed checkpoint; the drift report.

## The problem

When the holograms failed, the question "is this puzzle disabled by the save's state?" could not be answered: the save is on the handheld, excluded from every sync, and nothing reads it. The engine logs nothing about scripts, so the save and the module are the only evidence, and only the module was reachable. The [game README](../../README.md#when-it-breaks) lists four places evidence lives on the device, and each is fetched by hand with a different command.

On 2026-10-15/16 KMRP's events log was fetched by hand over ssh three times (the swoop race, character generation, the debug-level checks), each with its own `grep`. One count came out wrong because the log's lines end in CRLF and `grep 'fire$'` matched nothing. Turning the log on is a build setting now (`[kmrp] debug_logs` in `local.toml`, carried by the deploy); fetching and reading it is not.

## The idea

`modshop kotor fetch`: copy the newest saves, Proton's log, KMRP's logs (line endings normalised, the raw file kept beside it) and the drift report into `data/logs/device/<timestamp>/`, and print a summary: which checkpoint is deployed and whether it drifted, which save is newest and where the player is, and the save's globals and visited modules decoded with PyKotor (`pykotor.extract.savedata`), so a question like "has `Tar_HoloActive` been set" is one grep. [Crash capture](crash-capture.md) is the automatic, per-run version of the same folder; this is the on-demand one, and the decoding is shared.

## Unknowns

- How complete PyKotor's save reader is for K1 saves made by this build with KMRP installed.

## First step

Fetch and decode one save: print its globals, party, current module and the list of modules it holds state for.
