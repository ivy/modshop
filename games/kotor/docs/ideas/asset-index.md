---
title: Asset index
priority: p1
status: idea
depends_on: [script-corpus]
---

# Asset index

Every resource in every checkpoint, parsed once, queryable three ways: as structured facts, as a graph of references, and as text.

## The problem

The questions asked while diagnosing have been structural, not textual:

- Repair 08's cause was found by comparing a mod's seven bubble emitters with the game's own 54: emitter flags 266 against 2, and a `detonate` controller none of the game's emitters has ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). That is a query over every model's nodes and controllers.
- Repair 07 turned on which GUI textures are not a power of two in size ([its README](../../repairs/07-kmrp-pot-gui-textures/README.md)), a query over every texture's header.
- Repair 09 and the [k1cp fix](../../fixes/k1cp-sithtroop/README.md) were a reference to something that does not exist and an edit that did not land: questions about references.
- Seven of the twelve entries skipped in [`recipe.json`](../../build/recipe.json) are skipped because they crash with KMRP, which is a question of what two mods both touch.
- Why an area transition refuses to start while a companion lags behind was five hops of "what refers to this" across a strref, a conversation, a placeable blueprint, a script and the engine ([inspect](inspect-cli.md) has the chain); each hop was a full scan of the build's 43,000 resources.

Each was answered by writing a one-off script against PyKotor.

Making the Juhani mod (2026-10-16/17) asked the same kind of question about the game's own conventions, and each answer, when one came, was a precedent found by scanning:

- **How the game lays a character down and gets them up.** `banter.dlg` has Bastila trip Mission: a script plays `ANIMATION_LOOPING_PRONE` and the next node's `AnimList` gets her up with 10055. Found by searching every dialogue for the script that plays a prone animation; the mod copies it.
- **Which dialog animation kneels.** Every dialogue in the build was parsed looking for "kneel" in a node's comment or text; one hit, a creature's own animation. The question went unanswered and the kneel was dropped ([engine tables](engine-tables.md)).
- **How the game makes a party member start a conversation, and how it starts banter.** `k_trg_partyinit` and `k_bant_trig`, found by `grep` over the global source after the mod's banter hung behind a queued action.
- **Who switches the party's AI off before the grove's cutscene.** `strings` over the module's bytecode ([script corpus](script-corpus.md)).
- **How the Taris rakghoul transformation is staged**, and whether the rancor scene uses a horror effect: the module scripts referring to `rakghoul` or `rancor` by `strings`, then decompiled one by one.

Every one of these is a join: a dialogue node with its speaker, text, voice file, animations and scripts; a script with the routines it calls and their literal arguments; a blueprint with its scripts. Without the joins, the mod was built twice on guesses (a staging choice, a camera, the kneel) that a query would have settled, and each guess cost a play session to find wrong.

## The idea

Three layers over the same parse:

- **Facts**, in DuckDB or SQLite: a row per GFF field, 2DA cell, TLK entry, model node and controller, and texture header (size, format, mipmaps), each with the resource it came from. Repair 08's comparison is a `GROUP BY`.
- **References**: resrefs are the game's symbols. A dialog names scripts, an item names a model, a 2DA row names a TLK string, a module names its areas. The graph answers what uses a resource, which references dangle, and which of mod B's inputs mod A changed.
- **Text**: hybrid keyword and semantic search over item names, descriptions, dialogue and script source, for questions like "the conversation where…".

The build makes this cheap. Each checkpoint's `manifest.txt` lists every file's SHA-256, so the index is keyed by content hash and a file is parsed once however many checkpoints hold it; `changed.txt` says what a new checkpoint needs indexed. Every checkpoint becomes queryable, and provenance comes free: the first checkpoint in which a hash appears names the mod that introduced it.

For archives (`.mod`, `.rim`, `.erf`, the BIFs behind `chitin.key`), the unit is the resource inside, keyed by its own hash.

## What to leave out at first

- **Voice transcription** mostly repeats the TLK, whose entries already pair a line's text with its sound resref. It is worth doing only to find lines whose audio does not match their text, and for audio with no text (sound sets' barks, ambient voices, movies). What is worth taking from the voice files is each line's duration (`ffprobe`), for timing a scene.
- **Decompiled scripts** are lossy. Where a script's source exists (the game's include files, most mods' `.nss`), index the source and fall back to decompilation.
- **Embeddings of images** answer "textures that look like this", which no problem so far has asked.

## Unknowns

- The index's size across every checkpoint, and how long the first full parse takes.
- How much of the reference graph PyKotor already computes (`pykotor.tools.references` and `reference_finder` are candidates to read first).
- Whether the graph should include the engine's own references (a script or resource the executable names, such as `k_trg_transfail` at `0x007499C4`); they come from the [engine symbols](engine-symbols.md) work, not from parsing resources, and they are where a chain of references ends.

## Shape

SQLite with full-text search rather than a graph database: the questions so far are two or three joins deep, and FTS over node text, comments and script source covers the "the conversation where…" kind. The rows a dialogue contributes (entry or reply, index, speaker, listener, text or strref, voice resref, script, condition, each `AnimList` participant and number, camera angle and id, comment) are what the questions above needed; a script's rows come from the [script corpus](script-corpus.md)'s call index.

## First step

Dialogues and the script corpus's calls over the current chain end; reproduce the prone and get-up precedent (`banter.dlg`'s `k_swg_bantforce` and 10055) and the AI-off finding (`k_pman_aioff` called from `k_pdan_juhani27`) as queries. Then models and texture headers, reproducing repair 08's comparison.
