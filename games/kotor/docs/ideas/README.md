# Ideas

Tools that would make building and debugging the modded game cheaper, none of them built yet. Each document has YAML frontmatter with a `priority` and what it depends on, and states the problem with the evidence for it, the idea, what is not known, and the smallest first step.

## Priorities

Reassessed after the pipeline's first week rather than guessed. The costs actually paid were, in order: the patcher silently not doing what its log said (six PyKotor defects, two of them found by playing, one of them dropping hundreds of module fixes per build); rebuilding the whole chain to test a one-entry change (five rebuilds, about two hours); and writing the same PyKotor one-off scripts again for every diagnosis. Crashes on the device, which most of the original ideas address, were the cost of the week before, and those ideas are also the most uncertain because input automation under gamescope is untested.

- **1**: would have saved hours this week and can start now with no other piece built.
- **2**: removes a cost already paid, or is what a priority-1 or a later idea needs.
- **3**: speculative, or depends on an unproven piece.

## Priority 1

- [Patcher audit](patcher-audit.md): read HoloPatcher's log back against the tree after every step and fail the entry on a claim that did not land. Would have caught the module-replacement defect on the first build.
- [Try an entry without committing](chain-try.md): run one entry on a scratch tree, show what it changed, keep nothing. Replaces most full rebuilds during a fix.
- [Inspect command](inspect-cli.md): the five questions asked by one-off script today, as subcommands.

## Priority 2

- [Patcher parity](patcher-parity.md): TSLPatcher under Wine beside HoloPatcher on every step; the audit checks claims, parity checks semantics (repair 09's skipped row).
- [Round-trip tests](roundtrip-tests.md): would have caught the empty-tables defect before anything was deployed; cheap over the chain end.
- [Chain lint](chain-lint.md): the case-variant and shadow rules would have caught today's duplicate textures; orphan rows and dangling references are the next two.
- [Crash capture](crash-capture.md) and [device state fetch](device-state.md): the per-run and the on-demand versions of bringing the handheld's evidence home, with the save decoded.
- [Pinned archive store](archive-store.md): the mod archives as a definition, like the vanilla base.
- [Device fixtures](device-fixtures.md) and [chain bisection](chain-bisect.md): a bisect over checkpoints is nearly free now that `checkout` and `deploy KEY` exist; the fixture is the unproven part, and a one-day spike settles it.

## Priority 3

- [Semantic diff](semantic-diff.md) and [asset index](asset-index.md): grow out of the inspect command once its questions stabilise.
- [Driver ergonomics](driver-ux.md): watch, wait, stop, impact.
- [Module crawl](module-crawl.md), [mod intake report](mod-intake.md), [crash signatures](crash-signatures.md), [runtime trace](runtime-trace.md): each depends on a piece above and on a question no failure has yet asked.
