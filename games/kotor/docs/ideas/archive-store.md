---
title: Pinned archive store
priority: p2
status: idea
depends_on: []
---

# Pinned archive store

Treat the mod archives the way the vanilla game is treated: pinned by hash, fetched by script, kept, and checked.

## The problem

The vanilla base is a definition now (`base.json`: depot and manifest ids and the tree's hash), but the 190 mod archives are whatever was fetched on 2026-10-14, hashed into a gitignored `SHA256SUMS` and a cache keyed by size and mtime. A file replaced upstream is detected only as a key change with no explanation, and nothing says which version a build used. The reviewers of the [proposal](../../../../docs/proposals/kotor-build-pipeline.md) named this as the remaining hole in "everything replayable".

## The idea

- A committed `archives.json`: per entry, the source URL or site file id, the file names and their SHA-256, and the date fetched. It is hashes and ids, not bytes, so it belongs in git.
- `modshop kotor archives verify` reports every archive whose hash differs from the record, and `archives fetch` fetches only the missing ones.
- The build's input hashing reads the record instead of trusting size and mtime, and refuses an archive that does not match it unless told the record is being updated.

## Unknowns

- Nexus and DeadlyStream file ids are stable; mega links are not, and the one GameFront mod cannot be fetched at all. The record can still hold the hash.

## First step

Generate `archives.json` from the current folder and `SHA256SUMS`, and make `modshop kotor verify --inputs` compare against it.
