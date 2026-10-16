---
title: Mod intake report
priority: 3
status: idea
depends_on: [asset-index, chain-lint]
---

# Mod intake report

Before a mod enters the manifest, a report of what it would do to the current chain: what it overwrites, what it patches, what else touches the same resources, and whether it lints clean.

## The problem

Seven of the twelve entries skipped in [`recipe.json`](../../build/recipe.json) are skipped because the mod crashes with KMRP, which is known only because KMRP's author lists them. Nothing in the build says why they conflict, so a new mod that conflicts the same way is found by playing.

## The idea

A dry run of the proposed entry on a copy of the chain end that, instead of committing a checkpoint, reports:

- files it adds, files it replaces and which entry put each there (provenance from the [asset index](asset-index.md));
- resources its patcher steps edit, and the entries that edited the same resources before;
- the overlap with KMRP's entry in particular;
- [chain lint](chain-lint.md) findings on what it changed.

Run over the mods already skipped for KMRP, the same report shows what they have in common, which may turn a list of names into a rule.

## Unknowns

- Whether the KMRP conflicts are visible statically at all, or only at runtime in KMRP's injected code.

## First step

The report for one of the skipped mods against the chain end, read beside KMRP's issue #15.
