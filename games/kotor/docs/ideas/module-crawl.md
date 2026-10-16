---
title: Module crawl
priority: 3
status: idea
depends_on: [device-fixtures]
---

# Module crawl

Load every area of the game in turn on the handheld and report the ones the game does not survive.

## The problem

Repair 08's crash happened on an area's first frame: entering Upper City South from the north ended the game every time ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). A crash like that is only found by walking there, so every area the player has not yet reached is untested, and a mod added to the chain can break an area nobody visits until hours into a playthrough.

## The idea

A [device fixture](device-fixtures.md) per module, generated from the build's `modules/` folder: arrive, wait, record pass or fail. The crawl is the list of those fixtures run in order against one deployed checkpoint, with each failure's [capture](crash-capture.md) kept. Its result is a table of module, verdict and capture, which is also the smoke test that [chain bisection](chain-bisect.md) uses.

Arrival by warp puts the player at the module's default entry. Where an area has several doors and the crash depends on the view from one of them, as repair 08's did, a crawl by warp can miss it; the crawl catches the class, and a door-specific fixture catches the instance.

## Unknowns

- Everything in [device fixtures](device-fixtures.md), on which this depends.
- How long a crawl of every module takes, and whether a crash leaves the device in a state the next fixture can start from.

## First step

After the first fixture works, generate fixtures for every module of one planet and run them against the current build.
