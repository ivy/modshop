---
title: Chain lint
priority: p2
status: idea
depends_on: [inspect-cli]
---

# Chain lint

Static checks that run as entries in the chain, so every finding is pinned to the mod that introduced it and found before anything is deployed.

## The problem

Several faults in this build were visible in the files without running the game:

- [repair 09](../../repairs/09-blaster-adjustment-orphan-rows/README.md): an ini lists rows whose sections do not exist;
- [repair 07](../../repairs/07-kmrp-pot-gui-textures/README.md): GUI textures that are not a power of two in size;
- [repair 08](../../repairs/08-wounded-republic-detonate-controller/README.md): emitters carrying a controller none of the game's own emitters use;
- the `dedupe_tpc` step in the `modshop` package ([`../../../../src/modshop/`](../../../../src/modshop/)): a `.tpc` beside a same-named `.tga` or `.dds`, which crashes the game.

Each was found by a crash or a patcher error.

## The idea

A lint step after each entry, checking only what that entry changed (`changed.txt`), against rules like:

- references that do not resolve: a resref naming no resource, a strref past the end of the TLK, an ini row naming a missing section;
- textures with a non-power-of-two size, and texture formats the game does not handle;
- model features outside what the game's own models use, from the [asset index](asset-index.md)'s facts over vanilla;
- case-variant duplicates and `.tpc` shadows in Override.

Findings go into the checkpoint beside `changed.txt`, so `modshop kotor status` can show which entries introduced warnings. A rule that has caused a crash fails the build; the rest warn.

## Unknowns

- How noisy "outside what vanilla uses" is across a couple of hundred mods. It needs an allow list from the start.
- Whether lint output should be part of a checkpoint's key. It changes nothing in the tree, so it belongs beside the checkpoint rather than in it.

## First step

The four rules above as a script, run over the chain end, with each finding traced to its entry through `changed.txt`.
