---
title: Chain bisection
priority: p2
status: idea
depends_on: [device-fixtures]
---

# Chain bisection

Given a failing [fixture](device-fixtures.md), find the first entry of the chain after which it fails, without anyone choosing builds to try.

## The problem

When a crash is caused by a mod, finding which one means trying builds that include some mods and not others. Repair 08's cause was found by setting the mod's room aside and putting it back, by hand, on the device ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). With a couple of hundred entries in [`recipe.json`](../../build/recipe.json), guessing is slow.

## The idea

The pieces exist already. Every checkpoint is the game after a prefix of the chain, `modshop kotor checkout KEY DIR` produces any of them without a rebuild, and `modshop kotor deploy KEY` puts one on the handheld moving only what differs. A bisection over checkpoints is a binary search over prefixes: deploy the middle one, run the fixture, recurse into the half that contains the change from pass to fail. A chain of about 200 entries takes about eight runs, and the answer is an entry of the manifest together with its `changed.txt`, the paths it touched.

A second mode answers a different question: whether a failure needs a particular earlier mod as well. Removing one entry from the middle of the chain means rebuilding the entries after it; the checkpoints before it are reused, and rebuilt entries become checkpoints too, so a second removal of the same entry costs nothing.

## Unknowns

- Whether a fixture's verdict is reliable enough to bisect on. Repair 07's crash may depend on session history, and an intermittent failure needs several runs per step.
- Whether a save remains loadable across checkpoints; a save that references a resource an earlier prefix does not have fails for the wrong reason.

## First step

Once one fixture works, bisect repair 08's crash with repair 08 removed from the manifest and check that the result is the Diversified Wounded Republic Soldiers entry.
