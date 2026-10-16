# Knights of the Old Republic on Linux

The Steam release of KotOR 1, played under Proton on a handheld, with the community **KOTOR 1 Full Build** (Revision 12) installed by script, the **KMRP** interface and controller patch built on Linux, and repairs for what breaks under Proton. Everything here is reproducible from your own copy of the game and the mod archives; see [`../../docs/conventions.md`](../../docs/conventions.md).

Two machines are involved, named in `local.toml`:

- **the handheld**, which runs the game: Steam, Proton, the game folder at `$HOME/.local/share/Steam/steamapps/common/swkotor`;
- **the build host**, where the modded install is assembled. It needs a Python with tkinter (the patcher imports it even headless, and SteamOS-like distributions ship a Python without it), `7zz` (7-Zip; the archives include RAR), `rsync`, and `podman` if you build the KMRP controller module.

## Layout

| Path | What |
| --- | --- |
| `build/` | `download.py` fetches the build's archives, `base.sh` downloads the vanilla game by depot manifest id, `manifest.py` turns the build's instructions into `manifest.json`, `build.py` builds it as a chain of checkpoints, `deploy.py` puts a checkpoint on the handheld, `setup-venv.sh` makes the patcher's venv; `fixes/` holds our own TSLPatcher changes |
| `repairs/` | scripts that patch what the build installs where it is broken under Proton; each has a README with the evidence |
| `patches/` | our fixes to two other projects as `git format-patch` series: pykotor (the patcher's library) and KMRP |
| `kmrp-build/` | building KMRP's controller module on Linux and installing it into the game folder |
| `data/` | gitignored: `archives/` (one folder per mod, the KMRP installer, the Community Patch, the cutscenes), `game/` (`vanilla/`, the checkpoints in `ckpt/`, the working tree, `build` pointing at the chain's end), `stage/`, `logs/`, `venv/`, build outputs |

## Procedure

### 1. The game, pristine

```bash
mise install                     # DepotDownloader, from the repository's mise.toml
build/base.sh <steam account>    # asks for the password and a Steam Guard code the first time
build/build.py base              # normalises timestamps, writes data/game/vanilla/manifest.txt
```

`base.json` names the app, its Windows depot and the exact depot manifest id, so the base is a definition rather than a copy of some install: DepotDownloader (SteamRE's open-source Steam client) fetches that manifest for Windows into `data/game/vanilla/tree`. The handheld's own Steam install is not an input to anything; a fresh install there is not a way back either, since Steam's "verify integrity" rewrites changed files but never deletes added ones. The login state stays under `~/.config/DepotDownloader`, outside the repository and `data/`. (`steamcmd` was tried first: with the platform forced to Windows it writes the depot under a path with literal backslashes, and the container image keeps it outside any mountable volume.)

The build host's `data/game` must be on a filesystem with reflinks (XFS with `reflink=1`, btrfs); `build.py` checks and refuses otherwise. The working tree is a reflink copy of a checkpoint, so a build costs only the bytes each mod rewrites. Checkpoints themselves hardlink what did not change: a whole-tree reflink clone per checkpoint adds an extent-ownership record for every file to XFS's per-allocation-group reserved metadata, and a few hundred such clones of a 20,000-file tree exhausted it here with `ENOSPC` while `df` showed 900 GB free.

### 2. The archives

`build/download.py <file with your Nexus API key>` fetches every mod of the Full Build into `data/archives/NNN-<slug>/`, in the build's order: DeadlyStream as a guest, Nexus through its API (a premium key is needed for direct downloads), mega.nz through `megadl.py`. `k1full.json`, `dsfiles.json` and `nexusfiles.json` are the parsed build page and file listings it works from. One mod (Vurt's Ebon Hawk, on GameFront) cannot be fetched by script. The KMRP installer, the Community Patch and the rescaled cutscenes are fetched by hand into `data/archives/` as well; `data/archives/SHA256SUMS` records what was used.

### 3. The patcher

```bash
build/setup-venv.sh            # data/venv: HoloPatcher 1.5.3 with the pykotor series applied
```

Without the six pykotor fixes in `patches/pykotor/` the build is wrong: a TypeError on one mod's compile list, an exception on two mods' `Required`/`RequiredMsg` lists, a crash on one mod's `namespaces.ini`, three scripts of one mod refused by the compiler, every replacement of a resource inside a module archive silently dropped, and, worst, five mods ship 2DA tables with a zero cell-data size in the header that unpatched pykotor reads as empty tables and writes back empty, which blanks every feat name and crashes character creation.

### 4. The build

```bash
build/manifest.py        # writes build/manifest.json from the build's instructions
build/build.py           # builds the chain, or does nothing if every checkpoint exists
build/build.py status    # which entries have checkpoints
```

`manifest.json` is the build as a list of entries, one per mod, each a few steps: copies, renames, deletions, TLK merges, HoloPatcher runs, with a wildcard-and-case-tolerant path lookup for mods whose archives name files loosely. The first entry makes two symlinks the patcher and some mods' installers need (`Modules` for `modules`, because the patcher opens module paths by exact name, and `override` for `Override`, because some installer files spell it that way); the last entries are the repairs and the cutscene pack. What the manifest skips, and why, is in the file itself: the mods KMRP's author lists as crashing with it, two the build warns crash on Linux, one Steam Deck-incompatible, one unobtainable, and the whole widescreen section, which KMRP replaces. Where the build offers a choice, the manifest records the one made.

`build.py` gives each entry a key that names everything that could change its result (the previous entry's key and tree hash, the entry, the hashes of the files it reads, the driver's verbs and helpers (its orchestration code is left out, so a command-line change does not rebuild the chain), the patcher's venv and patch series, the tool versions) and keeps a checkpoint per key under `data/game/ckpt/`: the game folder after the entry ran (hardlinks to the parent checkpoint's unchanged files, reflink clones of the files the entry changed; nothing ever writes inside a checkpoint), a manifest of every file's hash, and the list of paths the entry changed. A run walks the chain and builds from the first entry whose checkpoint is missing; a run with nothing to do takes a few seconds. Every mod is unpacked fresh for its own steps and the stage deleted after, so nothing outside the checkpoints carries state between runs. After every patcher run the driver keeps one file per case-insensitive name in `Override`, the newest: HoloPatcher writes a file by the exact name its ini spells beside an existing one of another spelling, where Windows would overwrite, and under Wine two such names are one file chosen by chance. Timestamps in a checkpoint are all the same fixed value, so no comparison ever depends on an archive's clock. On a failure the working tree is discarded and the next run restores the last checkpoint. `data/game/build` points at the chain's end. Logs: `data/logs/build.log`, one file per patcher run in `data/logs/holopatcher/`.

Other commands: `verify [KEY]` rehashes a checkpoint in full against its manifest; `checkout KEY DIR` gives a reflink copy of any checkpoint for a bisect; `tag NAME` names one; `gc --keep N` removes checkpoints that are neither in the chain nor tagged nor among the N newest. Archive hashes are cached in `data/archives/.hashcache.json` by size and mtime; the archives are immutable downloads, and the cache is the one place the pipeline trusts a timestamp.

### 5. Repairs

Each folder in `repairs/` is one scripted fix with its README, taking its input from your archives. The ones the build needs are entries at the end of the manifest and run with it. Today:

- `08-wounded-republic-detonate-controller`: a mod's room model carries a `detonate` controller on its bubble emitters that ends the game under Proton the first time the room is in view. In the manifest.
- `07-kmrp-pot-gui-textures`: KMRP's three 768x768 interface textures at a power-of-two size. Unproven, not in the manifest; see its README.
- `09-blaster-adjustment-orphan-rows`: one option of JC's Blaster Adjustment lists two 2DA rows whose sections only its full option has; the rows are dropped from the staged change file before the patcher runs. In the manifest.

### 6. KMRP

KMRP ([RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch](https://github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch)) gives the game a resolution-aware interface and native controller support, applied in memory at every start through a `binkw32.dll` proxy; the executable is untouched. Its installer is a Windows .NET program that refuses a tree without `swkotor.ini`, so the `ini` entry first copies the one Steam's install produced (kept with the other original files under `data/archives/original-steam-files/`) into a tree that lacks it; then the `kmrp` entry runs the installer on the build host under Wine in a container (`podman build -t modshop-wine kmrp-build/wine` once; no network, nothing mounted but the tree and the installer), in place on the working tree, with the handheld's panel size as its argument and the choices its Advanced Settings would hold (driver compatibility, marker fixes, controller support, the High FPS fix) written to its settings file first. The tree is mounted at the path it will have on the handheld, because the installer's state file records the executable's path for its Restore; that path and the panel come from `local.toml` and are part of the step's key. The step then fixes the two timestamps in the state file and recomputes KMRP's manifest row for it, which makes the result a function of its inputs alone: two runs give the same tree.

The next entry, `kmrp-controller`, replaces the installer's controller module with the one built from source ([`kmrp-build/README.md`](kmrp-build/README.md)), which is how an unreleased fix (or ours) gets in. Both entries run on an unlaunched tree, so the handheld needs nothing done by hand.

On the handheld: a Steam file verification puts Steam's `binkw32.dll` back and silently disables KMRP (the drift check shows it; deploy again). The game must use Steam Input's **Gamepad** template or KMRP sees no pad; Steam keeps that selection in memory, so editing the controller config files while Steam runs does nothing. `kmrp-kpm.log` in the game folder proves it loaded; it reports how many of its interface files it left out because `Override` has its own, which is the intended precedence.

### 7. Deploy to the handheld

```bash
build/deploy.py            # the chain's end, by content
build/deploy.py --check    # only report what differs on the handheld
```

`deploy.py` reads the handheld's address and game folder from `local.toml`, refuses while the game runs, and syncs the checkpoint into a reflink copy of the handheld's live folder with `rsync --checksum --delete`, so a rebuilt file with identical content moves nothing and a second run reports nothing to do. When a dry run afterwards finds nothing left, the copy becomes the live folder by rename and the previous one stays beside it as `.prev`, the rollback. One explicit list of paths is outside the comparison and printed on every run: the saves, the logs, and `swkotor.ini`, which the build produces but the game rewrites as it is played, so it is sent only to a handheld that has none. `--check` is the drift check: anything in the handheld's folder that the build did not put there is listed by path. The build assumes a new game: areas a save has already visited keep their old state.

`build/build.py prove` is the reproducibility test: the whole chain built again from vanilla with no checkpoint reused, compared entry by entry with the cached chain, naming the first entry whose tree differs.

## When it breaks

What has been needed to diagnose crashes under Proton, in the order it helped:

- **The drift check**: `build/deploy.py --check` says, by path, how the handheld's folder differs from the build. Run it before and after a debugging session; a difference is either turned into a step (a repair, a manifest entry, a patch) or reverted, never left.
- **Proton's log**: `user_settings.py` in the Proton directory with `PROTON_LOG` and `PROTON_LOG_DIR`. Proton rewrites the log at every launch, so copy it when the game exits (a loop around `pgrep -x swkotor.exe` does). Wine's crash report in it has registers and one stack frame; `PROTON_CRASH_REPORT_DIR` did not produce a minidump here. glibc's own messages (`corrupted double-linked list`) appear in it without a timestamp.
- **KMRP's logs**, with `debug-logs=2` in the module's `configs/*.ini`: the pad on every change and the engine's movement fields in `kmrp-controller-events.log`, timestamped with `GetTickCount`, which is the same clock as the Proton log's seconds.
- **Steam's background recording**, on by default on the handheld: 3-second fMP4 chunks under the Steam userdata directory's `gamerecordings/video/bg_*`. `cat init-stream0.m4s chunk-stream0-*.m4s > clip.mp4` then `ffmpeg -vf fps=2` gives frames to read. It showed what was on screen at each crash when the logs could not.
- **A frozen game is better than a crashed one**: `gdb -p` works on the handheld, wine's `winedbg` attaches from the Proton directory with the prefix's `WINEPREFIX`, the game's windows are on display `:1` under gamescope (`xwininfo`, `xprop`, `xdotool`), and the decrypted executable can be dumped from the process (`gdb -p <pid> -batch -ex 'dump binary memory code.bin 0x401000 0x8c3000'`) and disassembled with `objdump -D -b binary -m i386 --adjust-vma=0x401000`; the executable on disk is encrypted and useless to `objdump`.
- **pykotor** reads everything: modules (`read_erf`, `read_rim`), templates (`read_gff`), tables (`read_2da`), models (`read_mdl` with the `.mdx`), and the game's own data through `Chitin` on `chitin.key`. Its `Installation` class is convenient but logs megabytes of debug output on a Linux layout.
- **Do not** set `glibc.malloc.mmap_threshold=0` through Proton's environment to catch a heap overrun: the prefix's `explorer.exe` never finishes starting with it.

Specific stories, each beside its fix: the detonate controller (`repairs/08-…`), the upgrade-screen heap corruption (`repairs/07-…`), the stick's over-long movement vector and the stick in conversations (`patches/kmrp/`, patches 4 and 5), the minimized game after a movie skip (`../../tools/restore-window/`).
