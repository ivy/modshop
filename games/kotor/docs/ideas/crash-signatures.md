---
title: Crash signatures
priority: 3
status: idea
depends_on: [crash-capture]
---

# Crash signatures

Turn a crash address in `swkotor.exe` into the name of the function it is in, and group crashes that share one.

## The problem

Repair 08's crash was at `0x0048DCBD`. Knowing that address is in the emitter render path took a memory dump of the decrypted executable and reading its disassembly ([`../../README.md`](../../README.md#when-it-breaks), [repair 08](../../repairs/08-wounded-republic-detonate-controller/README.md)); the executable on disk is encrypted and useless to `objdump`. Each new crash starts that work again, and two crashes at the same place are not recognised as one bug.

## The idea

A table of function ranges and names for the executable the build deploys, and a command that reads a [crash capture](crash-capture.md)'s Proton log, takes the faulting address and stack frame, and prints the function and the signature. Captures with the same signature are grouped. The table comes from an analysis of the dumped executable (Ghidra or similar), seeded with names from the community's reverse-engineering work on the game where it exists; PyKotor's README points to a reverse-engineering workflow on its wiki.

## Unknowns

- How much of the executable has community names, and under what licence.
- Whether Wine's one stack frame is enough for a useful signature, or whether a backtrace from `winedbg` is needed.

## First step

Load the dumped executable into Ghidra, name the function holding `0x0048DCBD`, and write the table format with that one entry.
