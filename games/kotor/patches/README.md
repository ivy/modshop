# Patch series

Fixes to two other projects, kept as `git format-patch` series over the upstream commit each was written against, per [`../../../docs/conventions.md`](../../../docs/conventions.md). Each patch carries the project's own license. `git am *.patch` applies a series to a fresh clone of the project.

## `pykotor/`: OpenKotOR/PyKotor, base `ca61ce8d5` (master), branch `tslpatcher-and-2da-fixes`

The library behind HoloPatcher, the Linux TSLPatcher. Three defects the Full Build hits, all still on upstream master at the base commit:

1. `tslpatcher/reader.py`, `load_compile_list`: `ModificationsNSS(file, replace)` is a TypeError; the argument is keyword-only.
2. `tslpatcher/reader.py`, the `Required`/`RequiredMsg` count check: raises on a lone `RequiredMsg=0` or a lone `Required=`; the shorter list is padded instead.
3. `resource/formats/twoda/io_twoda.py`: a 2DA whose header says 0 for its cell-data size (an editor quirk the game ignores; five of the build's mods ship such files) was read as a table of empty cells and written back empty. Cells are read by offset, as the game does.

`build/setup-venv.sh` applies the series to the installed pykotor 2.3.12 with `patch --strip 4` (the paths are `Libraries/PyKotor/src/pykotor/...`).

## `kmrp/`: RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch, base `6d93283` (master), branch `linux-build`

1. `tools/xpress_huff.py`: an XPRESS-with-Huffman encoder in the form the module's decoder reads, so the asset bank can be built where the Windows Compression API is not.
2. `tools/build_native_assets.py`: fall back to that encoder when `ctypes.WinDLL` does not exist.
3. `src/controller-native/build_controller_standalone_linux.sh`: the standalone controller module built with clang in MSVC mode (llvm-mingw image), Microsoft's CRT and SDK from xwin, SDL3's headers. [`../kmrp-build/README.md`](../kmrp-build/README.md) is the procedure.
4. The stick's movement vector kept inside the unit circle: a thumbstick's corners are up to sqrt(2) long and the module skips the engine's normalize for the analog path, so a flick ran 41% faster and was reported to head the wrong way. Upstream as pull request 59.
5. The left stick walks a conversation's replies as the D-pad does. Upstream as pull request 60.

The first three are what make the Linux build possible and are not intended for upstream as they stand; the last two are.
