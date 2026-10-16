# Knights of the Old Republic on Linux

The Steam release of KotOR 1, played under Proton on a handheld, with the community **KOTOR 1 Full Build** (Revision 12) installed by script, the **KMRP** interface and controller patch built on Linux, and repairs for what breaks under Proton. Everything here is reproducible from your own copy of the game and the mod archives; see [`../../docs/conventions.md`](../../docs/conventions.md).

Two machines are involved, named in `local.toml`:

- **the handheld**, which runs the game: Steam, Proton, the game folder at `$HOME/.local/share/Steam/steamapps/common/swkotor`;
- **the build host**, where the modded install is assembled. It needs mise (for uv and DepotDownloader), `7zz` (7-Zip; the archives include RAR), `rsync`, and `podman` for the KMRP installer step and for building the KMRP controller module.

## Layout

| Path | What |
| --- | --- |
| `build/` | the recipe's data: `base.json` (the vanilla game's Steam ids and tree hash), `k1full.json`, `dsfiles.json` and `nexusfiles.json` (the parsed build page and file listings), `cleanlist_k1.txt`, and `recipe.json`, the recipe's canonical form |
| `fixes/` | our own TSLPatcher change files, applied as steps of the recipe |
| `repairs/` | scripts that patch what the build installs where it is broken under Proton; each has a README with the evidence |
| `patches/` | our fixes to two other projects as `git format-patch` series: pykotor (the patcher's library) and KMRP |
| `kmrp-build/` | building KMRP's controller module on Linux and installing it into the game folder |
| `data/` | gitignored: `archives/` (one folder per mod, the KMRP installer, the Community Patch, the cutscenes), `game/` (`vanilla/`, the checkpoints in `ckpt/`, the working tree, `build` pointing at the chain's end), `stage/`, `logs/`, `hashcache.json`, build outputs |

The code is the `modshop` package at the repository root (`src/modshop/`): `core/` is the chain, the checkpoints and the deploy, and knows nothing about the game; `kotor/` is the step kinds, the path rules, the patcher and KMRP runners and the recipe. Every command below is `modshop kotor <command>`; `--data DIR` or `KOTOR_DATA` points it at another data root, and `--help` on any command lists its options. [`../../docs/proposals/modshop-cli.md`](../../docs/proposals/modshop-cli.md) is the design.

## Procedure

### 1. The tool

```bash
mise install    # uv and DepotDownloader, from the repository's mise.toml
uv sync         # the tool, the patcher (HoloPatcher 1.5.3) and the patched pykotor, in .venv
```

`uv.lock` pins pykotor to the head of our series branch on a fork (see [`patches/README.md`](patches/README.md)), as the commit's source archive: without those eight fixes the build is wrong (a TypeError on one mod's compile list, an exception on two mods' `Required`/`RequiredMsg` lists, a crash on one mod's `namespaces.ini`, three scripts of one mod refused by the compiler, every replacement of a resource inside a module archive silently dropped, five mods' 2DA tables read as empty and written back empty, which blanks every feat name and crashes character creation, and every compiled script calling the engine with its arguments in reverse, with no way to run the mod's own compiler instead). The patcher's resolved packages are part of every key, so a change to the lockfile rebuilds the chain. To build with a patcher from another environment (a fix in progress), set `MODSHOP_PATCHER` to its `holopatcher` executable; that environment's package sources are then keyed instead.

The Python uv uses must have tkinter (the patcher imports it even on the console); mise's does, and SteamOS-like distributions' does not, which is one reason the build runs on a separate host.

### 2. The game, pristine

```bash
modshop kotor base fetch <steam account>    # asks for the password and a Steam Guard code the first time
modshop kotor base index                    # normalises timestamps, writes the manifest, checks the hash
```

`build/base.json` names the app, its Windows depot, the exact depot manifest id and the hash of the tree they produce, so the base is a definition rather than a copy of some install: DepotDownloader (SteamRE's open-source Steam client) fetches that manifest for Windows into `data/game/vanilla/tree`, and `base index` refuses a tree whose hash is not the recorded one. The handheld's own Steam install is not an input to anything; a fresh install there is not a way back either, since Steam's "verify integrity" rewrites changed files but never deletes added ones. The login state stays under `~/.config/DepotDownloader`, outside the repository and `data/`.

The build host's `data/game` must be on a filesystem with reflinks (XFS with `reflink=1`, btrfs); the tool checks and refuses otherwise. The working tree is a reflink copy of a checkpoint, so a build costs only the bytes each mod rewrites. Checkpoints themselves hardlink what did not change: a whole-tree reflink clone per checkpoint adds an extent-ownership record for every file to XFS's per-allocation-group reserved metadata, and a few hundred such clones of a 20,000-file tree exhausted it here with `ENOSPC` while `df` showed 900 GB free.

### 3. The archives

`modshop kotor archives fetch <file with your Nexus API key>` fetches every mod of the Full Build into `data/archives/NNN-<slug>/`, in the build's order: DeadlyStream as a guest, Nexus through its API (a premium key is needed for direct downloads); `modshop kotor archives mega <links>` fetches the mega.nz ones into `data/archives/mega/`. One mod (Vurt's Ebon Hawk, on GameFront) cannot be fetched by script. The KMRP installer, the Community Patch and the rescaled cutscenes are fetched by hand into `data/archives/` as well; `data/archives/SHA256SUMS` records what was used.

### 4. The build

```bash
modshop kotor build           # builds the chain, or does nothing if every checkpoint exists
modshop kotor status          # which entries have checkpoints
modshop kotor recipe show     # the entries and what is skipped, and why
```

The recipe (`src/modshop/kotor/recipe.py`) is the build as a list of entries, one per mod, each a few steps: copies, renames, deletions, TLK merges, HoloPatcher runs, with a wildcard-and-case-tolerant path lookup for mods whose archives name files loosely. The first entry makes two symlinks the patcher and some mods' installers need (`Modules` for `modules`, because the patcher opens module paths by exact name, and `override` for `Override`, because some installer files spell it that way); the last entries are the repairs, the cutscene pack and KMRP. What the recipe skips, and why, is in the file itself: the mods KMRP's author lists as crashing with it, two the build warns crash on Linux, one Steam Deck-incompatible, one unobtainable, and the whole widescreen section, which KMRP replaces. Where the build offers a choice, the recipe records the one made. `build/recipe.json` is the recipe's canonical form, the exact text that enters each entry's key; `modshop kotor recipe write` regenerates it and a test fails when it is out of date.

Compiled scripts. Four mods ship NWScript source in a `[CompileList]` for the installer to compile against the game (Kill the Czerka Guard, Bastila has TSL Battle Meditation, Multifire and Autofire, Alignment Affects Force Powers). TSLPatcher compiles them with the `nwnnsscomp.exe` the mod ships (tk102's v0.03b, the same file in all three that ship one); HoloPatcher off Windows would use pykotor's own compiler, whose output differs, and from December 2025 until our patch 7 called every engine function with its arguments reversed (Cure healed nobody). So a HoloPatcher step that compiles says so (`compile=True` in the recipe): its scripts are then compiled by that `nwnnsscomp.exe` under Wine, in the same image as KMRP's installer (`src/modshop/kotor/nwnnsscomp.py`, no network, nothing mounted but the folders the compile reads and writes), and the step fails if any script was compiled by pykotor's compiler instead, or if a step that does not say so compiles at all, so a mod update that adds a compile list stops the build rather than shipping the other compiler's output. Multifire and Autofire ships no compiler (its own installer is a 2024 HoloPatcher, from before the regression), so its step takes TSLPatcher's from Kill the Czerka Guard's archive, checked against the hash pykotor knows it by; the `nwscript.nss` beside it is the one every one of these mods ships, which is the game's own. Alignment Affects Force Powers' three scripts compiled this way are byte-identical to the ones an earlier build compiled with the same file on the handheld.

Each entry gets a key that names everything that could change its result: the previous entry's key and tree hash, the entry's canonical form, the hashes of every file it reads (its archive folder and whatever its steps declare: a repair folder, the installer, the container image, the values from `local.toml`), the code that runs steps (every module the step runner imports, so a change to a step rebuilds the chain and a change to the command line does not), and the patcher's packages and the tool versions. A checkpoint per key lives under `data/game/ckpt/`: the game folder after the entry ran (hardlinks to the parent checkpoint's unchanged files, reflink clones of the files the entry changed; nothing ever writes inside a checkpoint), a manifest of every file's hash, and the list of paths the entry changed. A run walks the chain and builds from the first entry whose checkpoint is missing; a run with nothing to do takes a second. Every mod is unpacked fresh for its own steps and the stage deleted after, so nothing outside the checkpoints carries state between runs. After every patcher run the tool keeps one file per case-insensitive name in `Override`, the newest: HoloPatcher writes a file by the exact name its ini spells beside an existing one of another spelling, where Windows would overwrite, and under Wine two such names are one file chosen by chance. Timestamps in a checkpoint are all the same fixed value, so no comparison ever depends on an archive's clock. The working tree is marked dirty before an entry's first step, so a build that fails or is killed by any means leaves nothing the next run trusts: it restores the last checkpoint. `data/game/build` points at the chain's end. Logs: `data/logs/build.log`, one file per patcher run in `data/logs/holopatcher/`.

Other commands: `verify [KEY]` rehashes a checkpoint in full against its manifest, and `verify --inputs` rehashes every archive and reports any cached hash that lies; `checkout KEY DIR` gives a reflink copy of any checkpoint for a bisect; `tag NAME` names one; `gc --keep N` removes checkpoints that are neither in the chain nor tagged nor among the N newest. Archive hashes are cached in `data/hashcache.json` by path, size and mtime; the archives are immutable downloads, and the cache is the one place the pipeline trusts a timestamp.

### 5. Repairs

Each folder in `repairs/` is one scripted fix with its README, taking its input from your archives. The ones the build needs are entries of the recipe and run with it; the whole folder, README included, is part of the entry's key. Today:

- `08-wounded-republic-detonate-controller`: a mod's room model carries a `detonate` controller on its bubble emitters that ends the game under Proton the first time the room is in view. In the recipe.
- `07-kmrp-pot-gui-textures`: KMRP's three 768x768 interface textures at a power-of-two size. Unproven, not in the recipe; see its README. It needs Pillow: `uv sync --extra repairs`.
- `09-blaster-adjustment-orphan-rows`: one option of JC's Blaster Adjustment lists two 2DA rows whose sections only its full option has; the rows are dropped from the staged change file before the patcher runs. In the recipe.
- `10-no-minimize-under-proton`: the game minimises itself when the logo movie hands it focus, and under gamescope its next frame then waits forever: a black screen on about one start in three. A KPM byte patch in `patch_config.toml` removes the minimise until a KMRP release carries its own fix (`patches/kmrp/`, patch 6). In the recipe, after KMRP.

### 6. KMRP

KMRP ([RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch](https://github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch)) gives the game a resolution-aware interface and native controller support, applied in memory at every start through a `binkw32.dll` proxy; the executable is untouched. Its installer is a Windows .NET program that refuses a tree without `swkotor.ini`, so the `ini` entry first copies the one Steam's install produced (kept with the other original files under `data/archives/original-steam-files/`) into a tree that lacks it; then the `kmrp` entry runs the installer on the build host under Wine in a container (`podman build -t modshop-wine kmrp-build/wine` once, and again after a `podman system prune --all`, which removes it unless told to spare its `io.modshop.keep=true` label with `--filter label!=io.modshop.keep=true`; no network, nothing mounted but the tree and the installer), in place on the working tree, with the handheld's panel size as its argument and the choices its Advanced Settings would hold (driver compatibility, marker fixes, controller support, the High FPS fix) written to its settings file first. The tree is mounted at the path it will have on the handheld, because the installer's state file records the executable's path for its Restore; that path and the panel come from `local.toml` and are part of the step's key. The step then fixes the two timestamps in the state file and recomputes KMRP's manifest row for it, which makes the result a function of its inputs alone: two runs give the same tree. The container has one fixed name, and a build removes any left by a run that was killed before touching the working tree.

The next entry, `kmrp-controller`, replaces the installer's controller module with the one `modshop kotor kmrp build` built from source into `data/kmrp-build/` ([`kmrp-build/README.md`](kmrp-build/README.md)), which is how an unreleased fix (or ours) gets in. Both entries run on an unlaunched tree, so the handheld needs nothing done by hand.

On the handheld: a Steam file verification puts Steam's `binkw32.dll` back and silently disables KMRP (the drift check shows it; deploy again). The game must use Steam Input's **Gamepad** template or KMRP sees no pad; Steam keeps that selection in memory, so editing the controller config files while Steam runs does nothing. `kmrp-kpm.log` in the game folder proves it loaded; it reports how many of its interface files it left out because `Override` has its own, which is the intended precedence.

### 7. Deploy to the handheld

```bash
modshop kotor deploy            # the chain's end, by content
modshop kotor deploy --check    # only report what differs on the handheld
```

The deploy reads the handheld's address and game folder from `local.toml`, refuses while the game runs, and syncs the checkpoint into a reflink copy of the handheld's live folder with `rsync --checksum --delete`, so a rebuilt file with identical content moves nothing and a second run reports nothing to do. When a dry run afterwards finds nothing left, the copy becomes the live folder by rename and the previous one stays beside it as `.prev`, the rollback (a rename by hand). One explicit list of paths is outside the comparison and printed on every run: the saves, the logs, `swkotor.ini`, and `K1DriverCompat.ini`, the settings template KMRP's driver-compatibility patch writes at launch. `swkotor.ini` is managed rather than synced, because the game rewrites it as it is played (the movies seen, the key map, the options menu): a handheld without one gets the build's whole, and otherwise only the display keys the build decides are set to the build's values, `Width`, `Height`, `FullScreen` and `AllowHighMonitorFrequency` in `[Graphics Options]` (the list is `MANAGED` in `src/modshop/kotor/target.py`); every other line stays as the player left it. `--check` is the drift check: anything in the handheld's folder that the build did not put there is listed by path, and a managed key with another value is listed as `~setting swkotor.ini [section] key=live (build: value)`. The build assumes a new game: areas a save has already visited keep their old state. The `known-good` tag is set by hand (`modshop kotor tag known-good`) once a deployed build has been played.

`modshop kotor prove` is the reproducibility test: the whole chain built again from vanilla with no checkpoint reused, into `data/game/ckpt-prove/`, compared entry by entry with the cached chain, naming the first entry whose tree differs.

### 8. Working on the tool

```bash
mise run check    # ruff, pyright strict, pytest
mise run test
```

The tests build a synthetic game of a dozen files with a fake patcher under `tests/integration/`, which is where a change to the chain, the keys or the deploy is proved before it meets the real data; `tests/real_fs/` holds the few that need a reflink filesystem and skip without one. A change to a step's code, to a module it imports, or to the patcher's packages rebuilds the real chain by design.

## When it breaks

What has been needed to diagnose crashes under Proton, in the order it helped:

- **The drift check**: `modshop kotor deploy --check` says, by path, how the handheld's folder differs from the build. Run it before and after a debugging session; a difference is either turned into a step (a repair, a manifest entry, a patch) or reverted, never left.
- **Proton's log**: `user_settings.py` in the Proton directory with `PROTON_LOG` and `PROTON_LOG_DIR`. Proton rewrites the log at every launch, so copy it when the game exits (a loop around `pgrep -x swkotor.exe` does). Wine's crash report in it has registers and one stack frame; `PROTON_CRASH_REPORT_DIR` did not produce a minidump here. glibc's own messages (`corrupted double-linked list`) appear in it without a timestamp.
- **KMRP's logs**: `debug_logs = 2` under `[kmrp]` in `local.toml`, then `modshop kotor build` and `deploy` (only the `kmrp-controller` entry rebuilds), puts `debug-logs=2` in the controller's `configs/kmrp-controller.ini`; remove the line and do the same to turn it off. The module then logs the pad on every change, the engine's movement fields and the minigames' input in `kmrp-controller-events.log`, timestamped with `GetTickCount`, which is the same clock as the Proton log's seconds. Its lines end in CRLF. Editing the ini on the handheld by hand works for one session but is drift, and something has been seen to put it back.
- **Steam's background recording**, on by default on the handheld: 3-second fMP4 chunks under the Steam userdata directory's `gamerecordings/video/bg_*`. `cat init-stream0.m4s chunk-stream0-*.m4s > clip.mp4` then `ffmpeg -vf fps=2` gives frames to read. It showed what was on screen at each crash when the logs could not.
- **A frozen game is better than a crashed one**: `gdb -p` works on the handheld, wine's `winedbg` attaches from the Proton directory with the prefix's `WINEPREFIX`, the game's windows are on display `:1` under gamescope (`xwininfo`, `xprop`, `xdotool`), and the decrypted executable comes out of the running game with `modshop kotor re dump` (below).
- **pykotor** reads everything: modules (`read_erf`, `read_rim`), templates (`read_gff`), tables (`read_2da`), models (`read_mdl` with the `.mdx`), and the game's own data through `Chitin` on `chitin.key`. Its `Installation` class is convenient but logs megabytes of debug output on a Linux layout.
- **The engine's code**: `.text` of the executable on disk is SteamStub-encrypted, so `modshop kotor re dump`, with the game running, reads the image from the Wine process over ssh and writes `data/re/swkotor.unpacked.exe`: a PE a disassembler opens as it is (REA and Ghidra, from `mise install`), with every section but `.text` from the file on disk and KPM's hook sites in `.text` put back to the bytes `patch_config.toml` records. `data/re/dump.json` lists what it restored and the call and jump sites that point into small anonymous allocations or the game folder's DLLs: candidates for redirects KMRP's modules make without a `patch_config.toml` entry, left as they are because nothing records what they replaced, and to be confirmed in the disassembler before an address near one is trusted.
- **Do not** set `glibc.malloc.mmap_threshold=0` through Proton's environment to catch a heap overrun: the prefix's `explorer.exe` never finishes starting with it.

Specific stories, each beside its fix: the detonate controller (`repairs/08-…`), the upgrade-screen heap corruption (`repairs/07-…`), the stick's over-long movement vector and the stick in conversations (`patches/kmrp/`, patches 4 and 5), the black screen after the logo movies (`repairs/10-…`).
