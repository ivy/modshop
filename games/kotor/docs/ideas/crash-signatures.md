---
title: Crash signatures
priority: p2
status: idea
depends_on: [crash-capture, engine-symbols]
---

# Crash signatures

Turn a crash address in `swkotor.exe` into the name of the function it is in, and group crashes that share one.

## The problem

Repair 08's crash was at `0x0048DCBD`. Knowing that address is in the emitter render path took a memory dump of the decrypted executable and reading its disassembly ([`../../README.md`](../../README.md#when-it-breaks), [repair 08](../../repairs/08-wounded-republic-detonate-controller/README.md)); the executable on disk is encrypted and useless to `objdump`. The dump is one command now (`modshop kotor re dump`), but naming the function an address falls in is still reading disassembly by hand, each new crash starts that work again, and two crashes at the same place are not recognised as one bug.

## The idea

A table of function ranges and names for the executable the build deploys, and a command that reads a [crash capture](crash-capture.md)'s Proton log, takes the faulting address and stack frame, and prints the function and the signature. Captures with the same signature are grouped. The table is the [engine symbols](engine-symbols.md) analysis: the dumped executable in Ghidra with KMRP's several hundred named addresses applied, and the community's names where they exist (PyKotor's README points to a reverse-engineering workflow on its wiki). With it, a signature costs a lookup.

## Unknowns

- How much of the executable has community names, and under what licence.
- Whether Wine's one stack frame is enough for a useful signature, or whether a backtrace from `winedbg` is needed.

## First step

Once the symbol snapshot exists, resolve `0x0048DCBD` against it and write the signature format with that one entry.
