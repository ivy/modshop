# Evidence on the device

What KotOR under Proton leaves behind, where, and what disappears if nobody copies it. Written for Steam's KotOR 1 (app 32370) on a SteamOS-like Linux device reached over ssh.

## Save it before anything else

- **Proton's log is rewritten at every launch.** With `PROTON_LOG=1` (and `PROTON_LOG_DIR`) in `user_settings.py` in the Proton directory, the run's log is `$PROTON_LOG_DIR/steam-32370.log`. Copy it the moment the game exits; a relaunch to "try again" destroys the crash. A loop that copies it whenever `pgrep -x swkotor.exe` goes from running to not running keeps every run.
- **Everything else from a run**, into one folder named by time: KMRP's `kmrp-*.log` from the game folder, the Proton log, and the deployed build's identity if a build system tracks one.
- `PROTON_CRASH_REPORT_DIR` did not produce a minidump for these crashes, and Wine's own debugger fails to start at an assertion (`"msvcrt.dll" failed to initialize`). Don't wait for either.

## Reading a Proton log crash

- **`wine: Assertion failed at address F7F5B589 (thread 0138)`** with `EXCEPTION_WINE_ASSERTION` at `__kernel_vsyscall` is a native `abort()` on that thread, not a Windows exception. Look a few lines up for glibc's own message, printed without a timestamp: `free(): invalid pointer`, `munmap_chunk(): invalid pointer`, `corrupted double-linked list`. All mean glibc found its heap corrupted when something freed or allocated: the frame that aborts is a **victim**; the write that corrupted the heap happened earlier, elsewhere.
- **Whose heap.** The game, KMRP's modules and Wine's Windows-side DLLs allocate from Wine's heaps. glibc's arena is the native side's: Mesa, Wine's Unix libraries, libc. A glibc heap error therefore most likely comes from native code (the graphics driver above all); Windows-side code would have to write through a pointer into native memory.
- **The log's clock** (`11096.196:0138:013c:`) counts seconds; the first and last timestamps give the session length, which matters: a crash after 23 minutes and one after 90 at the same place follow the place, not the session. KMRP's log lines carry `GetTickCount` milliseconds; whether the two clocks line up has not been checked on one run.
- **No native stack.** Wine prints registers and one frame at most. A native stack needs gdb attached before the crash: [`gdb.md`](gdb.md).

## KMRP's logs

- `configs/kmrp-controller.ini` (and `configs/kmrp.ini`) in the game folder, section `[Patch Options]`, `debug-logs=N`. Level 2 logs the pad on every change, the engine's movement fields and the module's decisions to `kmrp-controller-events.log`. Only KMRP's installer writes these files; the game never does.
- **Lines end in CRLF.** `grep 'x$'` matches nothing; strip `\r` first (`tr -d '\r' < log | grep ...`).
- If the install is built by script, set the level in the build rather than by hand on the device: a hand edit is drift the next deploy reverts (modshop: `[kmrp] debug_logs = 2` in `local.toml`).

## Other places evidence lives

- **Steam's background recording**: 3-second fMP4 chunks under the Steam userdata directory's `gamerecordings/video/bg_*`. `cat init-stream0.m4s chunk-stream0-*.m4s > clip.mp4`, then `ffmpeg -vf fps=2` for frames: what was on screen at the crash when the logs can't say.
- **KMRP's unpacked interface files**: `AppData/Local/Temp/KMR*.tmp/` in the prefix (`compatdata/32370/pfx/drive_c/users/steamuser/`). The textures the game actually loads at the current resolution, which are not the files in KMRP's repository.
- **Saves**: `Saves/` in the game folder; read them with PyKotor ([`/kotor:pykotor`](../../pykotor/README.md)).

## A creature's state in a save

A save holds every creature of each visited module as the engine keeps it, readable with pykotor without running anything: `SAVEGAME.sav` is an ERF holding one `<module>.sav` ERF per module, whose `.git` has the `Creature List`. Each creature carries its `Tag` as the world has it (the grove's Carth is `carth`, his blueprint's `Carth`), `Commandable`, `FactionID`, `Animation`, its `EffectList` (each effect's type, creator id and the creature's own `ObjectId` to compare), and its local variables in `SWVarTable`: `BitArray` is the booleans, 32 to a word, bit `n % 32` of word `n / 32` (so `0x40000000` in the second word is boolean 62, `SW_FLAG_AI_OFF`). `GLOBALVARS.res` has the globals (`CatBoolean` names, `ValBoolean` bits, most significant first). Ask the player to save at the moment in question; it is cheaper and more certain than a debugger. Script-side tracing on screen is not an alternative: `AurPostString`, which the game's own scripts call only when `!ShipBuild()`, draws nothing in the shipped game.

## The device, over ssh

- **The game's process** is the one whose `/proc/<pid>/maps` has a line starting `00400000-` and ending `swkotor.exe`. The pressure-vessel wrappers (`srt-bwrap`, `pv-adverb`) carry `swkotor.exe` in their command lines and are the wrong process. Iterating `/proc` hits `PermissionError` on other users' processes (`/proc/1/maps`); skip them.
- It is a **32-bit** Wine process (`/proc/<pid>/exe` is `wine-preloader`, ELF i386) inside the Steam Runtime's mount namespace: its libraries are visible at `/proc/<pid>/root/...`, not at the host paths.
- `/proc/<pid>/mem` is readable as the same user when `ptrace_scope` is 0 (`/proc/sys/kernel/yama/ptrace_scope`).
- **sshd may refuse connections intermittently** ("Connection refused" on port 22, then fine seconds later). Retry before concluding anything about the device.
- **Shell traps hit while debugging remotely**: `pkill -f PATTERN` matches the shell running it and kills your own session; `cd DIR && cmd &` backgrounds the `cd` too, so the next line runs in the old directory; an `ssh host` inside a remote command connects from the device to itself.
