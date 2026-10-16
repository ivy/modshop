---
title: Semantic diff
priority: 3
status: idea
depends_on: [inspect-cli]
---

# Semantic diff

Compare two checkpoints by what changed inside each resource — a GFF field, a 2DA cell, a model node or controller — rather than by which files' hashes differ.

## The problem

A checkpoint's `changed.txt` names the paths an entry touched, and that is where a diagnosis starts. What changed inside them takes a one-off script: repair 08's diagnosis compared a mod's room model with the vanilla one by hand to find seven new emitters and their flags and controllers ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). Archives make it worse: a change to one resource inside a `.mod` shows only as the whole archive changing.

## The idea

A command that takes two checkpoint keys (or one, against its parent) and prints, per resource, the structural difference: fields added, removed and changed in GFFs; rows and cells in 2DAs; strings in TLKs; nodes, flags and controllers in models; size and format in textures; resources added, removed and changed inside archives. PyKotor parses every one of these formats and has a diff tool of its own (`pykotor.diff_tool`, and the `diff` command of its CLI), which is the place to start.

It serves [chain bisection](chain-bisect.md), whose answer is an entry, and [patcher parity](patcher-parity.md), whose answer is two trees that should match.

## Unknowns

- How much of this PyKotor's diff already does, and how readable its output is for models.

## First step

Run PyKotor's `diff` on the checkpoint before and after the Diversified Wounded Republic Soldiers entry and see whether repair 08's findings are in its output.
