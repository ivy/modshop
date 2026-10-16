---
title: Asset index
priority: 3
status: idea
depends_on: [inspect-cli]
---

# Asset index

Every resource in every checkpoint, parsed once, queryable three ways: as structured facts, as a graph of references, and as text.

## The problem

The questions asked while diagnosing have been structural, not textual:

- Repair 08's cause was found by comparing a mod's seven bubble emitters with the game's own 54: emitter flags 266 against 2, and a `detonate` controller none of the game's emitters has ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). That is a query over every model's nodes and controllers.
- Repair 07 turned on which GUI textures are not a power of two in size ([its README](../../repairs/07-kmrp-pot-gui-textures/README.md)), a query over every texture's header.
- Repair 09 and the [k1cp fix](../../build/fixes/k1cp-sithtroop/README.md) were a reference to something that does not exist and an edit that did not land: questions about references.
- Seven of the twelve entries skipped in [`recipe.json`](../../build/recipe.json) are skipped because they crash with KMRP, which is a question of what two mods both touch.

Each was answered by writing a one-off script against PyKotor.

## The idea

Three layers over the same parse:

- **Facts**, in DuckDB or SQLite: a row per GFF field, 2DA cell, TLK entry, model node and controller, and texture header (size, format, mipmaps), each with the resource it came from. Repair 08's comparison is a `GROUP BY`.
- **References**: resrefs are the game's symbols. A dialog names scripts, an item names a model, a 2DA row names a TLK string, a module names its areas. The graph answers what uses a resource, which references dangle, and which of mod B's inputs mod A changed.
- **Text**: hybrid keyword and semantic search over item names, descriptions, dialogue and script source, for questions like "the conversation where…".

The build makes this cheap. Each checkpoint's `manifest.txt` lists every file's SHA-256, so the index is keyed by content hash and a file is parsed once however many checkpoints hold it; `changed.txt` says what a new checkpoint needs indexed. Every checkpoint becomes queryable, and provenance comes free: the first checkpoint in which a hash appears names the mod that introduced it.

For archives (`.mod`, `.rim`, `.erf`, the BIFs behind `chitin.key`), the unit is the resource inside, keyed by its own hash.

## What to leave out at first

- **Voice transcription** mostly repeats the TLK, whose entries already pair a line's text with its sound resref. It is worth doing only to find lines whose audio does not match their text.
- **Decompiled scripts** are lossy. Where a script's source exists (the game's include files, most mods' `.nss`), index the source and fall back to decompilation.
- **Embeddings of images** answer "textures that look like this", which no problem so far has asked.

## Unknowns

- The index's size across every checkpoint, and how long the first full parse takes.
- How much of the reference graph PyKotor already computes (`pykotor.tools.references` and `reference_finder` are candidates to read first).

## First step

Facts and provenance only, for model nodes and controllers and texture headers, over the current chain end. Reproduce repair 08's comparison as a query.
