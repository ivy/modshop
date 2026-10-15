# Knights of the Old Republic on Linux

The Steam release of KotOR 1, played under Proton on a handheld, with the community **KOTOR 1 Full Build** (Revision 12) installed by script, the **KMRP** interface and controller patch built on Linux, and repairs for what breaks under Proton. Everything here is reproducible from your own copy of the game and the mod archives; see [`../../docs/conventions.md`](../../docs/conventions.md).

Two machines are involved, named in `local.toml`:

- **the handheld**, which runs the game: Steam, Proton, the game folder at `$HOME/.local/share/Steam/steamapps/common/swkotor`;
- **the build host**, where the modded install is assembled. It needs a Python with tkinter (the patcher imports it even headless, and SteamOS-like distributions ship a Python without it), `7zz` (7-Zip; the archives include RAR), `rsync`, and `podman` if you build the KMRP controller module.

## Layout

| Path | What |
| --- | --- |
| `build/` | `download.py` fetches the build's archives, `manifest.py` turns the build's instructions into `manifest.json`, `install.py` applies it to a game folder, `setup-venv.sh` makes the patcher's venv |
| `repairs/` | scripts that patch what the build installs where it is broken under Proton; each has a README with the evidence |
| `patches/` | our fixes to two other projects as `git format-patch` series: pykotor (the patcher's library) and KMRP |
| `kmrp-build/` | building KMRP's controller module on Linux and installing it into the game folder |
| `data/` | gitignored: `archives/` (one folder per mod, the KMRP installer, the Community Patch, the cutscenes), `game/` (the pristine and the built game copies), `stage/`, `logs/`, `venv/`, build outputs |

## Procedure

### 1. The game, pristine

On the handheld, install KotOR from Steam into an empty folder (Steam's "verify integrity" is not a way back to vanilla: it rewrites changed files but never deletes added ones). Copy it to the build host as `data/game/vanilla/` and never touch that copy; the build works on a copy of it. On a copy-on-write filesystem (btrfs, XFS) `cp -a --reflink=always data/game/vanilla data/game/build` is instant and free.

Keep `swkotor.ini`, `binkw32.dll`, the `movies` folder and the saves out of any sync: the first two are changed on the handheld by KMRP's installer, the movies are replaced on the handheld by the cutscene pack, and saves are the player's.

### 2. The archives

`build/download.py <file with your Nexus API key>` fetches every mod of the Full Build into `data/archives/NNN-<slug>/`, in the build's order: DeadlyStream as a guest, Nexus through its API (a premium key is needed for direct downloads), mega.nz through `megadl.py`. `k1full.json`, `dsfiles.json` and `nexusfiles.json` are the parsed build page and file listings it works from. One mod (Vurt's Ebon Hawk, on GameFront) cannot be fetched by script. The KMRP installer, the Community Patch and the rescaled cutscenes are fetched by hand into `data/archives/` as well; `data/archives/SHA256SUMS` records what was used.

### 3. The patcher

```bash
build/setup-venv.sh            # data/venv: HoloPatcher 1.5.3 with the pykotor series applied
```

Without the three pykotor fixes in `patches/pykotor/` the build is wrong: a TypeError on one mod's compile list, an exception on two mods' `Required`/`RequiredMsg` lists, and, worst, five mods ship 2DA tables with a zero cell-data size in the header that unpatched pykotor reads as empty tables and writes back empty, which blanks every feat name and crashes character creation.

### 4. The build

```bash
build/manifest.py                                              # writes build/manifest.json from the build's instructions
KOTOR_GAME=$PWD/data/game/build HOLOPATCHER=$PWD/data/venv/bin/holopatcher python3 -I build/install.py
```

`install.py` applies `manifest.json` step by step: copies, renames, deletions, TLK merges, HoloPatcher runs, with a wildcard-and-case-tolerant path lookup for mods whose archives name files loosely. It logs to `data/logs/install.log`, keeps each patcher run's output in `data/logs/holopatcher/`, and records finished steps in `data/logs/install.state.json`, so a stopped run resumes and a finished one is a no-op. `python3 -I build/install.py <mod folder>` reruns one mod.

What the manifest skips, and why, is in `manifest.json` itself: the mods KMRP's author lists as crashing with it, two the build warns crash on Linux, one Steam Deck-incompatible, one unobtainable, and the whole widescreen section, which KMRP replaces. Where the build offers a choice, the manifest records the one made.

Two things about the patcher's path handling matter on Linux: it matches module names exactly, so the game folder gets a `Modules` link beside `modules` and per-run case aliases, which the installer makes; and some mods' installer files spell `override` in lower case, so a second folder appears and is merged into `Override` afterwards, newer file winning.

### 5. Repairs

Each folder in `repairs/` is one scripted fix with its README. Run the ones the build needs after the build, pointing at the built game's `Override`; they take their inputs from your archives. Today:

- `08-wounded-republic-detonate-controller`: a mod's room model carries a `detonate` controller on its bubble emitters that ends the game under Proton the first time the room is in view. Needed.
- `07-kmrp-pot-gui-textures`: KMRP's three 768x768 interface textures at a power-of-two size. Unproven; see its README.

### 6. KMRP

KMRP ([RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch](https://github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch)) gives the game a resolution-aware interface and native controller support, applied in memory at every start through a `binkw32.dll` proxy; the executable is untouched. Its installer is a Windows program and runs inside the game's Proton prefix on the handheld, without a window:

```bash
DISPLAY=:0 protontricks-launch --appid 32370 <KMRP installer.exe> --in-place 'Z:\<game folder as a Windows path>\swkotor.exe'
```

(`--restore` in place of `--in-place` undoes it; the Flatpak protontricks needs access to the Steam directory.) Headless, it guesses the display, so set `Width` and `Height` in `swkotor.ini` (CRLF) to the panel first. A Steam file verification puts Steam's `binkw32.dll` back and silently disables KMRP: patch again. The game must use Steam Input's **Gamepad** template or KMRP sees no pad; Steam keeps that selection in memory, so editing the controller config files while Steam runs does nothing. `kmrp-kpm.log` in the game folder proves it loaded; it reports how many of its interface files it left out because `Override` has its own, which is the intended precedence.

Building the controller module from source, which is how an unreleased fix (or ours) gets onto the handheld, is [`kmrp-build/README.md`](kmrp-build/README.md).

### 7. Sync to the handheld

`rsync` the built game folder over the handheld's, mirroring `Override` and `modules` with `--delete` and merging the rest, excluding `binkw32.dll`, `swkotor.ini`, `Saves` and `movies`. The cutscene pack's `.bik` files go into `movies` on the handheld directly (12 GB; KMRP plays them at the game's resolution). Then take a copy-on-write copy of the result on the handheld as the known-good reference. The build assumes a new game: areas a save has already visited keep their old state.

## When it breaks

What has been needed to diagnose crashes under Proton, in the order it helped:

- **Proton's log**: `user_settings.py` in the Proton directory with `PROTON_LOG` and `PROTON_LOG_DIR`. Proton rewrites the log at every launch, so copy it when the game exits (a loop around `pgrep -x swkotor.exe` does). Wine's crash report in it has registers and one stack frame; `PROTON_CRASH_REPORT_DIR` did not produce a minidump here. glibc's own messages (`corrupted double-linked list`) appear in it without a timestamp.
- **KMRP's logs**, with `debug-logs=2` in the module's `configs/*.ini`: the pad on every change and the engine's movement fields in `kmrp-controller-events.log`, timestamped with `GetTickCount`, which is the same clock as the Proton log's seconds.
- **Steam's background recording**, on by default on the handheld: 3-second fMP4 chunks under the Steam userdata directory's `gamerecordings/video/bg_*`. `cat init-stream0.m4s chunk-stream0-*.m4s > clip.mp4` then `ffmpeg -vf fps=2` gives frames to read. It showed what was on screen at each crash when the logs could not.
- **A frozen game is better than a crashed one**: `gdb -p` works on the handheld, wine's `winedbg` attaches from the Proton directory with the prefix's `WINEPREFIX`, the game's windows are on display `:1` under gamescope (`xwininfo`, `xprop`, `xdotool`), and the decrypted executable can be dumped from the process (`gdb -p <pid> -batch -ex 'dump binary memory code.bin 0x401000 0x8c3000'`) and disassembled with `objdump -D -b binary -m i386 --adjust-vma=0x401000`; the executable on disk is encrypted and useless to `objdump`.
- **pykotor** reads everything: modules (`read_erf`, `read_rim`), templates (`read_gff`), tables (`read_2da`), models (`read_mdl` with the `.mdx`), and the game's own data through `Chitin` on `chitin.key`. Its `Installation` class is convenient but logs megabytes of debug output on a Linux layout.
- **Do not** set `glibc.malloc.mmap_threshold=0` through Proton's environment to catch a heap overrun: the prefix's `explorer.exe` never finishes starting with it.

Specific stories, each beside its fix: the detonate controller (`repairs/08-…`), the upgrade-screen heap corruption (`repairs/07-…`), the stick's over-long movement vector and the stick in conversations (`patches/kmrp/`, patches 4 and 5), the minimized game after a movie skip (`../../tools/restore-window/`).
