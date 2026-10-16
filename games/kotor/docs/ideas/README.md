# Ideas

Tools that would make building and debugging the modded game cheaper, none of them built yet. Each document has YAML frontmatter with a `priority` and what it depends on, and states the problem with the evidence for it, the idea, what is not known, and the smallest first step.

## How they are ranked

By costs actually paid, not by guesses. The pipeline's first week paid for the patcher silently not doing what its log said (six PyKotor defects, two found by playing, one dropping hundreds of module fixes per build), for rebuilding the whole chain to test a one-entry change (five rebuilds, about two hours), and for writing the same PyKotor one-off scripts for every diagnosis. The controller and engine work of 2026-10-15/16 paid for: waiting on someone to play every controller fix (five of them); reverse engineering from addresses found by grepping KMRP's source, with throwaway disassembly scripts; five rewrites of a resource scanner to follow one chain of references; and two full rebuilds, about 28 minutes each, for code changes that touched one entry.

- **p0**: do next. A cost being paid now, on most pieces of work, and the idea needs nothing else built first.
- **p1**: soon. Removes a cost paid recently and more than once.
- **p2**: valuable. Removes a cost paid once, guards against a known class of failure, or is what a p0 or p1 idea leads to.
- **p3**: later. Grows out of a p0 or p1 idea once its questions settle.
- **p4**: someday. Depends on an unproven piece and on a question no failure has asked yet.

## p0

- [Inspect command](inspect-cli.md): the questions asked by one-off script, as subcommands; `refs` first, which follows what refers to a strref, resref or tag, the question behind the area-transition investigation.
- [Virtual gamepad](virtual-gamepad.md): scripted pad input on the handheld through a device Steam Input treats as a pad, so a controller fix is checked without a person playing it.

## p1

- [Patcher audit](patcher-audit.md): read HoloPatcher's log back against the tree after every step and fail the entry on a claim that did not land. Would have caught the module-replacement defect on the first build.
- [Try an entry without committing](chain-try.md): run one entry on a scratch tree, show what it changed, keep nothing. Replaces most full rebuilds during a fix.
- [Engine symbols and disassembly helpers](engine-symbols.md): KMRP's named addresses applied to the dumped executable in a saved analysis, and the disassembly helpers kept as commands.
- [Live probes](live-probe.md): read named engine state from the running game, once or as it changes; the Y-in-combat question is one.
- [Device fixtures](device-fixtures.md): a save and a scripted action that reproduce one symptom on the handheld; with the virtual gamepad, the controller fixes' check.
- [Device state fetch](device-state.md): one command that brings the handheld's saves, logs and drift report home, decoded.

## p2

- [Patcher parity](patcher-parity.md): TSLPatcher under Wine beside HoloPatcher on every step; the audit checks claims, parity checks semantics (repair 09's skipped row).
- [Round-trip tests](roundtrip-tests.md): would have caught the empty-tables defect before anything was deployed; cheap over the chain end.
- [Chain lint](chain-lint.md): the case-variant and shadow rules would have caught the duplicate textures; orphan rows and dangling references are the next two.
- [Crash capture](crash-capture.md): every run's evidence in one folder, without anyone remembering to collect it; the per-run version of the device state fetch.
- [Pinned archive store](archive-store.md): the mod archives as a definition, like the vanilla base.
- [Chain bisection](chain-bisect.md): nearly free over checkpoints with `checkout` and `deploy KEY`, once a fixture gives a verdict.
- [Crash signatures](crash-signatures.md): a crash address named by the engine symbols, and crashes at the same place grouped.
- [Driver ergonomics](driver-ux.md): `impact` first, which says before an edit how much of the chain it rebuilds; then watch, wait, stop.

## p3

- [Semantic diff](semantic-diff.md) and [asset index](asset-index.md): grow out of the inspect command once its questions stabilise; the index's reference graph is `refs` without the scan.

## p4

- [Module crawl](module-crawl.md), [mod intake report](mod-intake.md), [runtime trace](runtime-trace.md): each depends on a piece above and on a question no failure has yet asked.
