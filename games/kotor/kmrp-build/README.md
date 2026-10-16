# Building KMRP's controller module on Linux

KMRP is built with MSVC on Windows by its maintainer, and its docs name nothing else. Its standalone controller module, `patches/kmrp-controller.dll` in the game folder, builds on Linux with the first three commits in [`../patches/kmrp/`](../patches/kmrp/README.md). This page is the procedure, the parts that are not upstream, and what goes wrong if a step is skipped.

## What is needed

- **The clone**: `git clone https://github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch` under `~/src/github.com/RayesDiyab/`, then `git am ../patches/kmrp/*.patch` on a branch over master `3adb77c`. The project's own `AGENTS.md` forbids committing or pushing there without the maintainer's permission; local branches are fine, nothing is pushed.
- **The compiler**: the container image `docker.io/mstorsjo/llvm-mingw:latest` (clang, lld, llvm-rc). It has no `clang-cl` link; the script runs `clang --driver-mode=cl`.
- **Microsoft's CRT and Windows SDK for x86**: laid out by [xwin](https://github.com/Jake-Shadle/xwin) with `xwin --accept-license --arch x86 --cache-dir ~/.cache/xwin/cache splat --output ~/.cache/xwin/sdk` (about 800 MB; the `--include-debug-libs` flag takes no value).
- **SDL3's headers**: the script fetches `SDL3-devel-3.4.16-VC.zip` into `build/deps/` in the clone when absent. The module loads SDL at run time (`kmrp-sdl3.dll`, a renamed `SDL3.dll` the installer already placed on the handheld), so nothing links against it.
- **Python**: the repository's environment (`uv sync`), with Pillow, numpy, fontTools and capstone laid over it by `uv run --with` at the versions `src/modshop/kotor/kmrp_build.py` pins. They are not project dependencies on purpose: `uv.lock` is part of every checkpoint's key, so adding them there would rebuild the whole chain.
- **Game inputs**, never committed anywhere: `build-inputs/swpc_tex_gui.erf` in the clone (copied from the game's `TexturePacks`) and `build-inputs/vanilla-gui/*.gui`, written once by `python tools/build_controller_assets.py --extract <game folder>` from the game's BIFs. The pristine game copy serves for both.

## The build

```bash
modshop kotor kmrp build        # --clone and --xwin when they are not at the paths above
modshop kotor build && modshop kotor deploy
```

It refuses a clone with uncommitted changes, so `COMMIT` always names what was built. It runs the clone's `src/controller-native/build_controller_standalone_linux.sh`, which does the two Python steps on the host (the asset bank, about 40 s; the export list) and then compiles and links in the container with the same sources, defines and link inputs as the maintainer's `build_controller_standalone.cmd`. Then it checks the result: the clone's `tools/check_hook_stolen_bytes.py` on the hook list; `llvm-readobj --coff-imports` shows only `KERNEL32.dll`, `USER32.dll`, `GDI32.dll` and `bcrypt.dll` (the CRT is static, `/MT`); `--coff-exports` lists every function `controller-exports.def` names. KMRP's `tools/build_controller_kpatch.py` packages it as the `.kpatch` KMRP's installer ships, with `kmrp-controller.verification.json` (hook count, hashes) and the module's hook list for the installed game's `patch_config.toml`, labelled `<upstream base>+linux<commits on top>`, from `git merge-base` with `origin/master`.

The five outputs land in `../data/kmrp-build/` with the clone's commit in `COMMIT`. The ones they replace move to `previous-<commit>/`, unless the commit is the same. The build is deterministic: the same commit gives the same DLL, byte for byte.

To check whether a patch applies to upstream without a checkout (the clone's assets do not fit a tmpfs), apply it to a temporary index: `GIT_INDEX_FILE=/tmp/i git read-tree origin/master && git format-patch -1 <commit> --stdout | GIT_INDEX_FILE=/tmp/i git apply --cached --check`.

## Installing it

The `kmrp-controller` entry of the build manifest runs `install-controller.py` on the working tree right after KMRP's own installer, taking the DLL and hook list from `../data/kmrp-build/`, so the module reaches the handheld with the next deploy. By hand, on any game folder:

```bash
python3 -I install-controller.py <game folder> kmrp-controller.dll kmrp-controller.hooks.toml [<debug-logs level>]
```

The entry passes `local.toml`'s `[kmrp] debug_logs` as the fourth argument (0 when absent), so the module's diagnostics are a build setting rather than an edit on the handheld. It replaces `patches/kmrp-controller.dll`, swaps the hooks of the `kmrp-controller` block in `patch_config.toml` for the generated list (the block's own `id` and `dll` lines stay), and sets the SHA-256 in `KMRP_KPM.manifest`'s row for the DLL, so KMRP's Restore Original still recognises the file. The previous three files are kept beside the live ones with a `.prev` suffix. Proof it loaded, after a launch: `kmrp-kpm.log` in the game folder reports KMRP's own runs as before, the Proton log's `loaddll` lines show `patches\kmrp-controller.dll` and the SDL copy, and `kmrp-controller-events.log` grows with `debug-logs=2` in `configs/kmrp-controller.ini`.

## Writing a hook

A hook is an entry in `src/controller-native/kotor1.hooks.toml`, a function in `exports.def`, and the handler. Two things KPM does are easy to get wrong:

- **A stack parameter arrives as the address of its slot.** `source = "esp+4"` hands the handler a pointer to the stack slot, not the value in it, so a pointer argument of the hooked function arrives as `T**` (`NativeMiniGameInputK1`, `NativeRumbleStopK1`). Registers arrive as their values.
- **The order.** The wrapper calls the handler, restores every register not in `exclude_from_restore`, runs the stolen bytes, then tests EAX for `consumed_exit_address`. Stolen bytes must be position-independent unless `skip_original_bytes` is true; `tools/check_hook_stolen_bytes.py` says why, and checks it.

The engine's code to hook comes from `modshop kotor re dump` ([`../README.md`](../README.md), "When it breaks").

## What does not work, and why

- **The GNU ABI (plain mingw).** The sources compile, but two constructs are MSVC-shaped: Itanium mangling leaves calling conventions out, so two `EngineFn<T>` instantiations that differ only in `__thiscall` versus `__cdecl` collide, and mingw's headers declare a POSIX `open` that shadows the file's own function of that name. Targeting `i686-pc-windows-msvc` with Microsoft's headers sidesteps both and matches the maintainer's binary layout.
- **Storing the asset bank instead of compressing it.** The decoder accepts a stored chunk, but the controller's bank is 181 MB uncompressed and the module embeds it as a resource in a 32-bit process that already maps KMRP's 122 MB module. Compressed it is 11 MB. The encoder keeps matches at 17 bytes or fewer so no length byte ever interleaves with the code words; the ratios are within a few percent of zlib's.
- **The bank's LZMS variant** (`--lzms`) needs Windows and the module refuses it anyway.
- **The main module** (`patches/kmrp.dll`) and KMRP's installer (C#) have not been built this way. The installer is .NET Framework WinForms; the module's build is the same shape as the controller's and would likely go the same way, but it is untested.
