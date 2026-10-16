# Patch series

Fixes to two other projects, kept as `git format-patch` series over the upstream commit each was written against, per [`../../../docs/conventions.md`](../../../docs/conventions.md). Each patch carries the project's own license. `git am *.patch` applies a series to a fresh clone of the project.

## `pykotor/`: OpenKotOR/PyKotor, base `ca61ce8d5` (master), branch `modshop-patches` on the fork [ivy/PyKotor](https://github.com/ivy/PyKotor)

The library behind HoloPatcher, the Linux TSLPatcher. Six defects the Full Build hits, all still on upstream master at the base commit:

1. `tslpatcher/reader.py`, `load_compile_list`: `ModificationsNSS(file, replace)` is a TypeError; the argument is keyword-only.
2. `tslpatcher/reader.py`, the `Required`/`RequiredMsg` count check: raises on a lone `RequiredMsg=0` or a lone `Required=`; the shorter list is padded instead.
3. `resource/formats/twoda/io_twoda.py`: a 2DA whose header says 0 for its cell-data size (an editor quirk the game ignores; five of the build's mods ship such files) was read as a table of empty cells and written back empty. Cells are read by offset, as the game does.
4. `tslpatcher/reader.py`, `NamespaceReader.load`: a namespace section without `IniName` or `InfoName` raised `KeyError`; TSLPatcher defaults them to `changes.ini` and `info.rtf` (JC's Mandalorian Armor ships such a `namespaces.ini`).
5. `resource/formats/ncs/compiler/lexer.py`: the operator tables typed a mixed int-and-float `+ - * /` as the left operand's type, where the engine's mixed instructions yield a float; `FloatToInt(nInt * fFloat)` was refused as a type mismatch and three of Alignment Affects Force Powers' scripts did not compile.
6. `extract/capsule.py`, `Capsule.add`: the new resource was set first and every existing resource copied over it afterwards, so a `Replace#=` into a `.mod` or `.rim` that already held the resource wrote the old bytes back while the log said it was replacing the file. Hundreds of module fixes per build (most of the Community Patch's) had silently done nothing; the Twisted Rancor Trio holograms, whose use scripts the Movie-Style Holograms mod replaces, were the symptom that exposed it.

The fork's branch is the series applied: its head is the base plus these six commits, and the series is regenerated from it with `git format-patch ca61ce8d5` when the branch moves. `build/setup-venv.sh` applies the series to the installed pykotor 2.3.12 with `patch --strip 4` (the paths are `Libraries/PyKotor/src/pykotor/...`).

## `kmrp/`: RayesDiyab/KMRP-KOTOR-Modern-Restoration-Patch, base `3adb77c` (master), branch `linux-build`

1. `tools/xpress_huff.py`: an XPRESS-with-Huffman encoder in the form the module's decoder reads, so the asset bank can be built where the Windows Compression API is not.
2. `tools/build_native_assets.py`: fall back to that encoder when `ctypes.WinDLL` does not exist.
3. `src/controller-native/build_controller_standalone_linux.sh`: the standalone controller module built with clang in MSVC mode (llvm-mingw image), Microsoft's CRT and SDK from xwin, SDL3's headers. [`../kmrp-build/README.md`](../kmrp-build/README.md) is the procedure.
4. The swoop race and the Ebon Hawk's turret driven from the pad, with the Xbox controls: the left stick steers or aims, A starts the swoop's thrusters and shifts, either trigger fires the turret. The minigames read only keyboard and mouse events whose ids already hold those devices' descriptions, so the pad cannot be bound to them; a hook on the minigame's input step (`0x00670FB0`) feeds it instead. Played in a swoop race; the turret not yet. Upstream as pull request 62.
5. The left stick navigates the screens the engine navigates itself, character generation's among them, by taking the D-pad's path in every menu: the dialogue fold of pull request 60, extended to the GUI class and all four directions. Played. Upstream as pull request 64.

The first three are what make the Linux build possible and are not intended for upstream as they stand; the last two are. The series is regenerated from the branch with `git format-patch 3adb77c` when the branch moves.
