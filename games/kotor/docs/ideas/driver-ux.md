---
title: Driver ergonomics
priority: p2
status: idea
depends_on: []
---

# Driver ergonomics

Small additions to the `modshop` package ([`../../../../src/modshop/`](../../../../src/modshop/)) that remove supervision overhead.

## The problem

A chain build is 25 minutes with nothing to do but watch it. On the pipeline's first week that meant three overlapping log watchers that replayed old logs after a restart, a `pkill` by pattern that killed the shell issuing it, and no way to ask before an edit how much of the chain it would invalidate.

The last of those is still paid. On 2026-10-16 a change to `modshop.core.inputs` rebuilt all 190 entries (about 28 minutes) where a moment's warning would have shown it was in the runner's code closure; a change to the `kmrp-controller` entry's arguments rebuilt one entry. The two edits looked alike from the outside. `impact` is that warning.

## The idea

- `modshop kotor status --watch`: one line that updates in place (entry N of 190, current mod, elapsed, last failure), and `modshop kotor wait` that returns when the running build ends, with its exit status.
- `modshop kotor stop`: signal the build holding the lock, which already discards its working tree cleanly.
- `modshop kotor impact [--inputs PATH...] [--code]`: the first entry whose key would change for a given edit, and how many entries follow it, computed from the key material without building.
- `modshop kotor log ENTRY`: the patcher log and the `changed.txt` of an entry's current checkpoint.

## First step

`impact`, since it is the key function applied without side effects.
