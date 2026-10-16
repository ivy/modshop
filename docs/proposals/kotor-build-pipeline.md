# Proposal: a reproducible, incremental build and deploy pipeline for KotOR

Status: accepted plan, not yet built. The KotOR procedure in [`../../games/kotor/README.md`](../../games/kotor/README.md) works today but is resumable rather than incremental, has no pristine base, and ends in hand steps on the handheld. This document is the next shape of that pipeline and the reasons for it. The README stays the how-to; this is the why and the what.

## The goal

Iterate rapidly on mods and fixes without drift. Concretely: a change to any input, from a mod archive to a one-line repair, produces a new game folder on the handheld by running the pipeline, nothing else; and at any moment it is possible to say, by content, whether the folder on the handheld is what the pipeline built. Debugging must not be able to accumulate into an unreconcilable game state. The section [How debugging stays out of the build](#how-debugging-stays-out-of-the-build) is the part that serves that last sentence; the rest is machinery.

## The problem

The modded install is 196 mods (`games/kotor/build/manifest.json`, 12 of them skips), 236 steps in all, applied in order by `install.py` to a game folder: 130 file copies and renames, TLK merges, and 79 HoloPatcher runs that rewrite 2DA tables and GFF templates in place. Each mod mutates the tree the next one reads, so the order is fixed and a mod's result depends on everything before it. The full run takes hours. After it come scripted repairs (`games/kotor/repairs/`), KMRP's installer (a Windows program that today runs inside the game's Proton prefix on the handheld), a controller module built from source, the 12 GB cutscene pack copied into `movies` by hand, and an `rsync` to the handheld typed from memory.

What is wrong with it:

- **Not incremental.** `install.py` records finished mods in a state file and skips them, so a stopped run resumes. Changing mod 120 means deleting the game copy and rebuilding from mod 1.
- **No base.** The only vanilla copy was the handheld's Steam install, since modded. Steam's "verify integrity" rewrites changed files but never deletes added ones, so it is not a way back.
- **Hand steps hiding in the procedure.** The README describes a `Modules` link and a merge of a lower-case `override` folder into `Override`; neither is in `install.py`. They were done by hand during the first build. The cutscenes are copied by hand. The KMRP installer and the controller install run on the handheld by hand.
- **Hidden state.** Mods are unpacked once into `data/stage/` and reused across runs; twelve entries share one `mega` stage and some steps edit it in place; a run killed mid-extract leaves a partial folder that later runs take as complete.
- **Nondeterminism.** The case-insensitive path lookup takes the first match from an unsorted directory listing. Files copied from archives keep the archive's timestamps, which have 2-second resolution and collide across mods.
- **No proof.** Nothing records what the built tree should hash to, so there is no way to say whether a second build matches the first, or whether the handheld's folder has drifted.

## What the pipeline must do

1. Produce the modded tree from a defined vanilla tree and the archives, by script, with every input named and hashed, and nothing done by hand.
2. After a change to one input, redo only the mods it affects.
3. Restore the tree as it was after any mod, quickly, for bisecting a crash.
4. Prove reproducibility: a clean build and an incremental build from the same inputs give the same tree, and a mismatch names the mod where they diverged.
5. Deploy to the handheld by content: a second deploy sends nothing, and a drift check compares content, never timestamps.
6. Keep the repository rules: no game or mod bytes in git, no device identity, everything replayable.

### Determinism, stated as behaviour

- **Nothing changed, nothing happens.** Every key in the chain matches an existing checkpoint, so the build does no work and ends at the same final checkpoint; the deploy's checksum comparison then sends nothing and its dry run prints no lines. Normalised timestamps are what make the second half true: without them `rsync --archive` would still touch mtimes on files whose content matched.
- **One mod changed, only its effect syncs.** The build necessarily replays every mod after the changed one, because the chain cannot know in advance which later mods read what the changed one wrote. But replaying is not resending: mods that did not depend on the change write byte-identical files, the final manifest differs only where the change propagated, and the deploy sends exactly those paths. The cost of a mid-chain change is therefore build time for the tail, never deploy time or drift. If the tail's build time turns out to matter, the per-checkpoint changed-path lists give each mod's write set, and a mod whose read and write sets miss every changed mod's write set could be skipped; that is a later optimisation on data the chain records anyway, not part of this plan.

Constraints: the build host is XFS with reflinks (`cp --reflink=always` fails loudly where it is not); the handheld's home is btrfs; the game tree is about 15 GB and tens of thousands of files, the movies 12 GB more; the patcher mutates files in place; the only Windows-only tool is KMRP's installer.

## Phase 0: measure

Before building any of this, two measurements from the existing logs and tree, because they decide how much of phase 2 is worth building:

- Where the hours go. If patcher start-up dominates the 79 runs (pykotor's `Installation` scans and logs the whole tree on a Linux layout), one patcher process for many mods, or quieter logging, shortens the build more than checkpointing does.
- What a checkpoint costs: the time and inode count of one reflink copy of the built tree, and the bytes each mod rewrites (from a before-and-after file listing), since a reflink checkpoint costs every rewritten version of every patched table and module. `du` overcounts reflinked trees; only `df` is true.

## Phase 1: the base, and the installer

**The base.** Download the vanilla game on the build host with `steamcmd`, platform forced to Windows (`@sSteamCmdForcePlatformType windows`), into `games/kotor/data/game/vanilla/`. Commit the app id, the depot ids, the exact depot manifest ids and the sorted SHA-256 manifest of the resulting tree: integers and hashes, not game bytes. The downloaded tree is kept; the manifest ids are provenance rather than the only way back, since whether Steam serves old manifests indefinitely is unknown. The same bound applies to the archives: the committed per-mod hashes detect a file replaced upstream but cannot recover it, so replayability is bounded by what upstream still serves and by the archive copies kept under `data/`.

`steamcmd`'s cached login is a long-lived account credential. It lives in its own directory outside the repository and `data/`, mode 0700, and nothing else in the pipeline runs as a user that can read it (see the installer below).

Why not a fresh install on the handheld copied over: Steam's client URLs raise confirmation dialogs, validate does not remove added files, and a copy of an install is a copy where a pinned manifest id is a definition. The handheld's own Steam install can auto-update past the pinned base; the deploy compares the two versions and says so.

Unverified: that `steamcmd` serves this game's Windows depot to an owning account from Linux. DepotDownloader is the fallback. Cost: one Steam Guard code at first login. A `steamcmd` download has never been run, so it will lack `swkotor.ini`; the file is generated as a step with the panel's `Width` and `Height` from `local.toml`, which makes the one device parameter in the build explicit and keyed.

**The installer.** Run KMRP's installer under Wine on the build host against a copy of the built tree, inside a sandbox (a podman container or bubblewrap) with only that copy mounted and no network, because it is a downloaded Windows binary and Wine maps the host's root as `Z:`. This is load-bearing: today `swkotor.ini` and `binkw32.dll` are excluded from the sync because the installer changes them on the handheld, which leaves the deployed folder a function of the build plus a hand step. If the installer runs on the build host, its output is one more keyed mod and the handheld becomes a pure deploy target. If it does not, it stays a handheld step, keyed and hash-checked like the others, and the proof in phase 4 covers the pre-KMRP tree only; the README says so rather than hiding it. Either way its idempotence when run twice is tested, since requirement 5 depends on it.

## Phase 2: the checkpointed build

**Unit of work: the mod.** `install.py` already treats the mod as its atom; a mod with several steps does not resume mid-mod. A checkpoint is taken after every mod unless phase 0 shows that is too expensive, in which case after every patcher mod, with up to a few cheap copy-only mods replayed on restore. The cadence is a number in the driver, set from the measurement, not a design decision.

**Input key.** Each mod gets a key: the hash of the previous mod's key and of the previous checkpoint's tree manifest (so a change that leaves the tree identical stops invalidating there); the mod's manifest entry; the hashes of every file in the mod's archive folder, and of any other path the entry resolves (`data/...` references reach into other mods' folders); the hash of `install.py`'s syntax tree (`ast.dump`, so a comment edit invalidates nothing and a code edit invalidates everything it could affect, without hand-listing which helpers each verb calls); the venv's installed package versions and the pykotor patch series; and the versions of `7zz` and Python. A key missing an input is a bug of the same class as the hidden stage: it makes "built once" and "rebuilt from a checkpoint" differ silently, and the mutation test in phase 4 is what catches it.

**Stage.** Each mod is extracted fresh into a temporary stage at its step, used, and deleted. The `mega` folder is split so that each entry names its own archive; the entries that edited the shared stage become steps on their own extraction. The stage is no longer state, and the tens of GB it occupied are not kept.

**Checkpoints.** After a mod completes, the game folder is reflink-copied into `data/game/ckpt/<key>.tmp`, synced, and renamed to `<key>`, so a kill mid-copy leaves nothing that looks valid; stale `.tmp` directories are removed at start. Beside each checkpoint goes its full tree manifest (every file hashed, no timestamp shortcuts: hashing 15 GB with a fast hash is tens of seconds, small next to the patcher) and the list of paths that changed since the parent checkpoint, which is the first thing a bisect asks for. Timestamps in the tree are normalised to a fixed value at the end of each mod, so no later comparison can depend on an archive's clock. A build walks the chain, reflinks the last existing checkpoint to the working copy, verifies it against its manifest, and replays from there. On any failure the working copy is discarded and restored from the last checkpoint. The state file goes away. A lock file prevents two builds on one tree; a preflight checks that `data/game` is on one reflink-capable filesystem; patcher runs have a timeout.

Checkpoints are not made read-only: reflink copies preserve modes, a read-only checkpoint would restore as a read-only working copy, and a write to a reflink copy never touches the source's extents anyway. The manifest check on restore is the protection.

**Garbage collection.** Keys are never reused, so checkpoints accumulate; `gc --keep-last N` keeps the current chain's newest N and anything tagged (`known-good`), removes the rest, and reports what `df` gave back.

**Everything else becomes a mod.** The `Modules` link, the `override` merge, each repair, the cutscenes as an input, the generated `swkotor.ini`, the KMRP installer's output if phase 1 succeeds, and the controller module (keyed on its source commit and the build container's image digest): all entries in the same chain, keyed the same way, so "the build" is one named checkpoint and there is no second list of things to do.

**Case lookup** sorts its candidates so a tie resolves the same way every time.

### Alternatives considered

- **ostree.** A commit per mod gives a content-addressed store, a Merkle root per commit, `ostree diff` and deduplication. It does not know when a mod's inputs changed, so the key logic above is needed anyway. Its checkouts are hardlinks into the object store, which an in-place patcher would corrupt, so every checkout would need `--force-copy`; libostree may attempt a reflink first, which is cheap to test on XFS. Held in reserve if checkpoint space becomes a problem after measuring.
- **DVC.** The closest off-the-shelf input-addressed stage graph, with a run cache and a reflink cache type. Not adopted because, as far as we understand it, a stage's outputs cannot be its inputs, and this pipeline is one tree mutated in place; unverified, and worth an hour if the driver grows past a few hundred lines.
- **`podman build` with one `RUN` per mod.** Layer caching is exactly the incremental semantics wanted, and about 184 layers is under the kernel's overlay stack limit (about 500). But the build would run inside a container with the venv, 7-Zip and archives mounted, and the tree would be copied out of the image for every deploy. Nothing else here is a container except the sandboxes.
- **btrfs subvolume snapshots on the build host.** The build host is XFS; a loop-mounted btrfs image is a second filesystem for the effect reflinks already give.
- **restic or borg.** Deduplicate and verify, but a restore is a full copy, which defeats requirement 3.
- **Nix.** Each mod a derivation over the previous output. Correct by construction, but the patcher needs tkinter and a venv, the archives would be fixed-output inputs, and nothing else here is Nix.

## Phase 3: deploy

The deployed tree is defined as the final checkpoint, nothing more: the cutscenes, the ini and the KMRP output are inside it after phase 2. `deploy.py` reads `local.toml` for the handheld's address and paths and runs `rsync --archive --checksum --delete` from the checkpoint into a reflink copy of the handheld's live folder, with one explicit exclusion set, printed on every run: `Saves`, the game's own log files, and, only if the installer could not move to the build host, `swkotor.ini` and `binkw32.dll`. Checksum mode compares content on both sides (minutes of reading per deploy, acceptable for one person) so a rebuild that rewrote files with identical content sends nothing, and the same command with `--dry-run --itemize-changes` is the drift check. When the post-deploy check passes, the new copy is swapped into place by rename and the previous one kept as the rollback; a kill mid-deploy leaves the live folder untouched. The copy that passed is also what `known-good` names. The deploy refuses to run while the game is running.

## Phase 4: proof

Two tests, both scripts that print differing paths and exit non-zero:

- **Determinism.** Build clean from vanilla into a separate checkpoint namespace and compare the final manifest with the cached chain's; on a mismatch, walk the per-checkpoint manifests to the first mod that diverged. If the patcher is the cause, the fix belongs in the pykotor patch series. Both builds run on the same host, so this says nothing about host dependence; that is accepted.
- **Key completeness.** Change one input mid-chain (a byte in an archive file, a verb, a patch), rebuild incrementally, build clean in a fresh namespace, compare. Run it whenever the key function changes. This is the test that catches a missing key input; the determinism test cannot, since unchanged inputs agree whether or not the key sees them.

## How debugging stays out of the build

The risk being guarded against: a crash is chased for an evening, files are moved aside, a DLL is swapped, a texture is resampled, something works, and a month later nobody can say which of those is why the game runs. The rules that prevent it:

- **The handheld's game folder is an output.** Nothing is an input to the pipeline because it is on the handheld. Anything found there that the build did not put there is drift, and the drift check lists it by path.
- **Experiments happen in a copy.** A reflink copy of the live folder (on the handheld, or of any checkpoint on the build host) is free; an experiment runs there and the live folder is swapped to it by rename only for the test. When the test ends, the copy is deleted or its finding is written down; it is never left as the live folder.
- **A finding has exactly two fates.** Either it becomes a step (a repair folder, a manifest entry, a patch in a series) and the next build carries it, or it is discarded. There is no third state where a fix lives only in a game folder. The drift check after every debugging session is the enforcement: it must come back clean, or the difference must be named and turned into a step before the session is called done.
- **Anything put aside is put aside with its hash.** A file moved out of `Override` for a test goes into a dated folder under `data/aside/` with a note of what it was and why, so an experiment can be reversed and its result attributed.
- **The known-good tag is earned.** It is set only by a deploy whose check passed, never by hand.

These are rules for people and agents, and the drift check is what makes them checkable rather than aspirational. The existing items that violate them today (the controller module installed by hand, three textures parked aside, the repaired model placed directly in `Override`) are regularised by the first build on the new pipeline, which rebuilds them all as steps.

## Open questions

- Phase 0's numbers: patcher time breakdown; checkpoint cost per mod.
- Does KMRP's installer run under Wine in a sandbox on the build host, and is it idempotent?
- Does `steamcmd` serve the Windows depot from Linux to an owning account?
- Is HoloPatcher deterministic?
