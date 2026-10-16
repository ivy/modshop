---
title: Patcher parity
priority: 2
status: idea
depends_on: [inspect-cli]
---

# Patcher parity

Run the original TSLPatcher under Wine beside HoloPatcher on the same mod and the same starting tree, and diff what they produce.

## The problem

The build installs mods with HoloPatcher, a reimplementation of TSLPatcher, and mod authors test against TSLPatcher. Where the two differ, the build is wrong in ways nobody sees until the game misbehaves:

- the series in [`../../patches/pykotor/`](../../patches/pykotor/) fixes a compile list that raised a TypeError, `Required` lists that raised, a `namespaces.ini` that crashed, scripts the compiler refused, and 2DA tables read as empty and written back empty, which blanked every feat name ([`../../README.md`](../../README.md));
- [repair 09](../../repairs/09-blaster-adjustment-orphan-rows/README.md) exists because TSLPatcher skips a row whose section is missing and HoloPatcher raises;
- the [k1cp fix](../../build/fixes/k1cp-sithtroop/README.md) applies an edit HoloPatcher fails on.

Each was found one at a time, by a failure.

## The idea

The build already runs a Windows installer in a container under Wine with no network (the KMRP step in [`build.py`](../../build/build.py), image from [`kmrp-build/wine`](../../kmrp-build/wine/Containerfile)). For each HoloPatcher step in the manifest, restore the parent checkpoint twice, run HoloPatcher on one copy and TSLPatcher in the container on the other, and diff the trees, using [semantic diff](semantic-diff.md) where the bytes differ. One run covers every patcher step in the chain and lists every divergence, each a candidate patch for PyKotor or a known, documented difference.

PyKotor has started on the same idea upstream ("parity harness MVP with HACKList corpus", commit `35d83a860` in OpenKotOR/PyKotor), which is worth reading before building and worth contributing to after.

## Unknowns

- Whether TSLPatcher can be driven without its GUI, or needs synthetic clicks under `xvfb-run`.
- Which differences are expected: TSLPatcher's own bugs, which HoloPatcher deliberately does not reproduce.
- Where TSLPatcher binaries come from; each mod ships its own copy, which may be a different version per mod.

## First step

Repair 09's mod: run its own TSLPatcher in the container on the parent checkpoint and confirm the result matches the build's (HoloPatcher plus the repair).
