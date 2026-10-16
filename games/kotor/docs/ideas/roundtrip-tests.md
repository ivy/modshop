---
title: Round-trip tests
priority: 2
status: idea
depends_on: []
---

# Round-trip tests

Read every resource the build produces with PyKotor, write it back, and require the same bytes.

## The problem

The worst bug the PyKotor patch series fixes was silent: five mods ship 2DA tables with a zero cell-data size in the header, unpatched PyKotor read them as empty and wrote them back empty, and every feat name was blank until character creation crashed ([`../../README.md`](../../README.md)). Nothing failed at build time. Any format PyKotor reads lossily is a bug of the same kind waiting for the mod that triggers it.

Repairs also have to choose how to edit a file. Repair 08 changes two bytes per emitter in the model rather than going through PyKotor's model API ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). Whether the API would have been safe is not known for any format.

## The idea

For every distinct resource in the chain (keyed by content hash, as in the [asset index](asset-index.md), so each is tested once), read it with the matching PyKotor reader, write it with the matching writer, and compare. A resource that comes back different is either a PyKotor bug or a field PyKotor normalises on purpose, and the result per format says how far a repair can trust the object API for that format.

Run as part of the build, it catches the next lossy read when a new mod brings an unusual file, before anything is deployed.

## Unknowns

- How many formats PyKotor writes back byte-exact by design; GFF field order and padding, and MDL layout, may legitimately differ. Where they do, compare re-read objects rather than bytes.

## First step

Round-trip every 2DA and GFF in the chain end and count the differences per format.
