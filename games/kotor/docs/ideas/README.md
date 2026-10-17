# Ideas

Tools that would make building and debugging the modded game cheaper, none of them built yet. Each document has YAML frontmatter with a `priority` and what it depends on, and states the problem with the evidence for it, the idea, what is not known, and the smallest first step.

## How they are ranked

By costs actually paid, not by guesses. The pipeline's first week paid for the patcher silently not doing what its log said (six PyKotor defects, two found by playing, one dropping hundreds of module fixes per build), for rebuilding the whole chain to test a one-entry change (five rebuilds, about two hours), and for writing the same PyKotor one-off scripts for every diagnosis. The controller and engine work of 2026-10-15/16 paid for: waiting on someone to play every controller fix (five of them); reverse engineering from addresses found by grepping KMRP's source, with throwaway disassembly scripts; five rewrites of a resource scanner to follow one chain of references; and two full rebuilds, about 28 minutes each, for code changes that touched one entry. Making the [Juhani mod](../../mods/juhani-clones/README.md) on 2026-10-16/17 paid for: the state of the game at a moment, which a save holds, read by four one-off pykotor scripts, after an hour of guesses and two workarounds, one of which changed the design; the game's own way of doing something, found by `strings` over bytecode and by parsing every dialogue, because module scripts have no source and nothing joins a dialogue node to its animations and scripts; engine behaviour guessed from addresses rather than read, until three decompiles answered it; an on-screen diagnostic that the shipped game does not draw, and live breakpoints that froze the game; Steam recordings joined and cut by hand about eight times; and the owner replaying the whole scene for each of eight deploys, four of their sessions answering nothing new.

- **p0**: do next. A cost being paid now, on most pieces of work, and the idea needs nothing else built first.
- **p1**: soon. Removes a cost paid recently and more than once.
- **p2**: valuable. Removes a cost paid once, guards against a known class of failure, or is what a p0 or p1 idea leads to.
- **p3**: later. Grows out of a p0 or p1 idea once its questions settle.
- **p4**: someday. Depends on an unproven piece and on a question no failure has asked yet.

## p0

- [Device state and saves](device-state.md): a save's globals, party and creatures (tags, effects, local variables, action queues) printed by name. Three of the Juhani mod's causes were read from a save in minutes, after hours of guessing.
- [Script corpus](script-corpus.md): every module script decompiled into the corpus, so "how does the game already do this" is a `grep`; the AI-off cause and most of the mod's precedents were in module scripts with no source.
- [Engine symbols and disassembly helpers](engine-symbols.md): the engine read by name; the click and default-action chain of 2026-10-17 exists only as addresses in one document so far.
- [Inspect command](inspect-cli.md): the questions asked by one-off script, as subcommands; `refs` first, which follows what refers to a strref, resref or tag, the question behind the area-transition investigation.

## p1

- [Asset index](asset-index.md): dialogue nodes, scripts' calls and blueprints joined in SQLite with full-text search; finds the game's own precedent (a prone character got up with 10055 in `banter.dlg`) as a query instead of a scan.
- [Live probes](live-probe.md): read named engine state from the running game, once or as it changes; the question gdb's breakpoints froze the game trying to answer.
- [A script log that works](script-log.md): `AurPostString` draws nothing in the shipped game; find a channel that does, or keep the trace in globals a save carries.
- [Game recordings](recordings.md): Steam's background recordings listed, joined, contact-sheeted and cut by one command.
- [Device fixtures](device-fixtures.md): a save and a scripted action that reproduce one symptom on the handheld; a save after a scene's fight turns a ten-minute replay into a load.
- [Virtual gamepad](virtual-gamepad.md): scripted pad input on the handheld through a device Steam Input treats as a pad, so a controller fix is checked without a person playing it.
- [Patcher audit](patcher-audit.md): read HoloPatcher's log back against the tree after every step and fail the entry on a claim that did not land. Would have caught the module-replacement defect on the first build.
- [Try an entry without committing](chain-try.md): run one entry on a scratch tree, show what it changed, keep nothing. Replaces most full rebuilds during a fix.

## p2

- [Engine tables](engine-tables.md): the dialog animation numbers, the engine's effect types and what each placed camera frames, recovered once; the kneel was dropped and a camera chosen wrong for want of them.
- [Patcher parity](patcher-parity.md): TSLPatcher under Wine beside HoloPatcher on every step; the audit checks claims, parity checks semantics (repair 09's skipped row).
- [Round-trip tests](roundtrip-tests.md): would have caught the empty-tables defect before anything was deployed; cheap over the chain end.
- [Chain lint](chain-lint.md): the case-variant and shadow rules would have caught the duplicate textures; orphan rows and dangling references are the next two.
- [Crash capture](crash-capture.md): every run's evidence in one folder, without anyone remembering to collect it; the per-run version of the device state fetch.
- [Pinned archive store](archive-store.md): the mod archives as a definition, like the vanilla base.
- [Chain bisection](chain-bisect.md): nearly free over checkpoints with `checkout` and `deploy KEY`, once a fixture gives a verdict.
- [Crash signatures](crash-signatures.md): a crash address named by the engine symbols, and crashes at the same place grouped.
- [Driver ergonomics](driver-ux.md): `impact` first, which says before an edit how much of the chain it rebuilds; then watch, wait, stop.

## p3

- [Semantic diff](semantic-diff.md): grows out of the inspect command once its questions stabilise.

## p4

- [Module crawl](module-crawl.md), [mod intake report](mod-intake.md), [runtime trace](runtime-trace.md): each depends on a piece above and on a question no failure has yet asked.
