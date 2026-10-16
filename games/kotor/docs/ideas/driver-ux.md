---
title: Driver ergonomics
priority: 3
status: idea
depends_on: []
---

# Driver ergonomics

Small additions to the `modshop` package ([`../../../../src/modshop/`](../../../../src/modshop/)) that remove supervision overhead.

## The problem

A chain build is 25 minutes with nothing to do but watch it. Today that was three overlapping log watchers that replayed old logs after a restart, a `pkill` by pattern that killed the shell issuing it, and no way to ask before an edit how much of the chain it would invalidate.

## The idea

- `modshop kotor status --watch`: one line that updates in place (entry N of 190, current mod, elapsed, last failure), and `modshop kotor wait` that returns when the running build ends, with its exit status.
- `modshop kotor stop`: signal the build holding the lock, which already discards its working tree cleanly.
- `modshop kotor impact [--inputs PATH...] [--code]`: the first entry whose key would change for a given edit, and how many entries follow it, computed from the key material without building.
- `modshop kotor log ENTRY`: the patcher log and the `changed.txt` of an entry's current checkpoint.

## First step

`impact`, since it is the key function applied without side effects.
