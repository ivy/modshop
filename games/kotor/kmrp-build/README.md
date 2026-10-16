# Building KMRP's controller module on Linux

KMRP is built with MSVC on Windows by its maintainer, and its docs name nothing else. Its standalone controller module, `patches/kmrp-controller.dll` in the game folder, builds on Linux with the three commits in [`../patches/kmrp/`](../patches/kmrp/README.md). This page is the procedure, the parts that are not upstream, and what goes wrong if a step is skipped.

## What is needed

- **The clone**: `git clone https://github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch` under `~/src/github.com/RayesDiyab/`, then `git am ../patches/kmrp/*.patch` on a branch over master `6d93283`. The project's own `AGENTS.md` forbids committing or pushing there without the maintainer's permission; local branches are fine, nothing is pushed.
- **The compiler**: the container image `docker.io/mstorsjo/llvm-mingw:latest` (clang, lld, llvm-rc). It has no `clang-cl` link; the script runs `clang --driver-mode=cl`.
- **Microsoft's CRT and Windows SDK for x86**: laid out by [xwin](https://github.com/Jake-Shadle/xwin) with `xwin --accept-license --arch x86 --cache-dir ~/.cache/xwin/cache splat --output ~/.cache/xwin/sdk` (about 800 MB; the `--include-debug-libs` flag takes no value).
- **SDL3's headers**: the script fetches `SDL3-devel-3.4.16-VC.zip` into `build/deps/` in the clone when absent. The module loads SDL at run time (`kmrp-sdl3.dll`, a renamed `SDL3.dll` the installer already placed on the handheld), so nothing links against it.
- **Python**: the patcher venv from `build/setup-venv.sh` plus `pip install Pillow numpy fonttools capstone`.
- **Game inputs**, never committed anywhere: `build-inputs/swpc_tex_gui.erf` in the clone (copied from the game's `TexturePacks`) and `build-inputs/vanilla-gui/*.gui`, written once by `python tools/build_controller_assets.py --extract <game folder>` from the game's BIFs. The pristine game copy serves for both.

## The build

```bash
cd ~/src/github.com/RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch
XWIN=~/.cache/xwin/sdk PYTHON=<venv>/bin/python src/controller-native/build_controller_standalone_linux.sh
<venv>/bin/python tools/build_controller_kpatch.py --module build/controller-standalone/kmrp-controller.dll \
  --out dist/controller --version <version> --config-dir dist/controller/config
```

The script runs the two Python steps on the host (the asset bank, about 40 s; the export list), then compiles and links in the container with the same sources, defines and link inputs as the maintainer's `build_controller_standalone.cmd`. The second command packages the module as the `.kpatch` KMRP's installer ships, writes `kmrp-controller.verification.json` (hook count, hashes) and, with `--config-dir`, the module's hook list for the installed game's `patch_config.toml`.

Check the result the way the first one was checked: `llvm-readobj --coff-imports` shows only `KERNEL32.dll`, `USER32.dll`, `GDI32.dll` and `bcrypt.dll` (the CRT is static, `/MT`), `--coff-exports` lists every function `controller-exports.def` names, and the size is near 12 MB. Keep the outputs under `../data/kmrp-build/` with the clone's commit beside them.

## Installing it

The `kmrp-controller` entry of the build manifest runs `install-controller.py` on the working tree right after KMRP's own installer, taking the DLL and hook list from `../data/kmrp-build/`, so the module reaches the handheld with the next deploy. By hand, on any game folder:

```bash
python3 -I install-controller.py <game folder> kmrp-controller.dll kmrp-controller.hooks.toml
```

It replaces `patches/kmrp-controller.dll`, swaps the hooks of the `kmrp-controller` block in `patch_config.toml` for the generated list (the block's own `id` and `dll` lines stay), and sets the SHA-256 in `KMRP_KPM.manifest`'s row for the DLL, so KMRP's Restore Original still recognises the file. The previous three files are kept beside the live ones with a `.prev` suffix. Proof it loaded, after a launch: `kmrp-kpm.log` in the game folder reports KMRP's own runs as before, the Proton log's `loaddll` lines show `patches\kmrp-controller.dll` and the SDL copy, and `kmrp-controller-events.log` grows with `debug-logs=2` in `configs/kmrp-controller.ini`.

## What does not work, and why

- **The GNU ABI (plain mingw).** The sources compile, but two constructs are MSVC-shaped: Itanium mangling leaves calling conventions out, so two `EngineFn<T>` instantiations that differ only in `__thiscall` versus `__cdecl` collide, and mingw's headers declare a POSIX `open` that shadows the file's own function of that name. Targeting `i686-pc-windows-msvc` with Microsoft's headers sidesteps both and matches the maintainer's binary layout.
- **Storing the asset bank instead of compressing it.** The decoder accepts a stored chunk, but the controller's bank is 181 MB uncompressed and the module embeds it as a resource in a 32-bit process that already maps KMRP's 122 MB module. Compressed it is 11 MB. The encoder keeps matches at 17 bytes or fewer so no length byte ever interleaves with the code words; the ratios are within a few percent of zlib's.
- **The bank's LZMS variant** (`--lzms`) needs Windows and the module refuses it anyway.
- **The main module** (`patches/kmrp.dll`) and KMRP's installer (C#) have not been built this way. The installer is .NET Framework WinForms; the module's build is the same shape as the controller's and would likely go the same way, but it is untested.
