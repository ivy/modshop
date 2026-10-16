---
title: Try an entry without committing
priority: p1
status: idea
depends_on: []
---

# Try an entry without committing

`modshop kotor try ENTRY [--from KEY]`: restore the parent checkpoint into a scratch tree, run one entry's steps, print its changed paths, keep nothing.

## The problem

Every change to a step in the `modshop` package ([`../../../../src/modshop/`](../../../../src/modshop/)) or to the PyKotor patch series invalidates every key, by design, and a full chain is about 25 minutes. Fixing the five problems the first chain build exposed (a namespaces mod, orphan rows, three scripts, case-variant files, the module replacement) took five full rebuilds, about two hours of waiting, most of it to confirm a change that touched one entry. The synthetic harnesses built by hand to avoid that (a tiny vanilla tree, a manifest of two entries) were written twice and thrown away.

It recurs whenever the code moves. On 2026-10-16 two changes in the step runner's import closure (a new script argument kind, then the error a missing podman image raises) each rebuilt all 190 entries, about 28 minutes apiece, and both chains ended on the tree they started from: the change under test touched one entry, `kmrp-controller`, and `try` on that entry was all the check needed.

## The idea

A command that takes an entry name and optionally a checkpoint to start from, reflinks that tree into `data/game/try/`, runs the entry's steps there with the stage extracted fresh, writes the would-be `changed.txt` and the [inspect](inspect-cli.md) summary of what changed, and leaves the tree for inspection until the next `try`. No key, no checkpoint, no effect on the chain. With `--venv PATH` it runs the patcher from a different venv, which is how a PyKotor patch is tested before it is exported.

The same command with a list of entries is the cheap half of the mutation test in the [proposal](../../../../docs/proposals/kotor-build-pipeline.md): change the input, `try` the entries after it, compare with the chain's checkpoints, and only then pay for the real rebuild.

## Unknowns

- Little about plumbing: `prove` already runs entries into a scratch store and a scratch work tree (`Session.work("work-prove")`), and the builder takes its store and work tree as arguments, so `try` is the same with one entry and no store.

## First step

`try` for a single entry on the chain end's parent, used to re-verify repair 09 without a rebuild.
