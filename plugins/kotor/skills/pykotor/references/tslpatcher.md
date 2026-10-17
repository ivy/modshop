# TSLPatcher mods: reading `tslpatchdata` and installing headless

A TSLPatcher mod is a `tslpatchdata/` folder: a `changes.ini` (or a `namespaces.ini` naming several option folders, each with its own ini), the files it installs, and the files it patches from. pykotor's `tslpatcher` package reads and applies it; `holopatcher` is the CLI/GUI around it. Paths below are relative to the `pykotor` and `holopatcher` packages.

Install a mod into a game copy, headless, and collect what it logged:

```python
import logging

logging.disable(logging.CRITICAL)
import contextlib, io
from threading import Event
from holopatcher import core
from pykotor.tslpatcher.logger import PatchLogger, LogType

info = core.load_mod(mod_dir)  # the folder holding tslpatchdata/, or tslpatchdata itself
print([ns.name for ns in info.namespaces])  # one entry when there is no namespaces.ini
log = PatchLogger()
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    res = core.install_mod(info.mod_path, game_copy, info.namespaces, info.namespaces[0].name, log, Event())
print(res)  # InstallResult(install_time=..., num_errors=0, num_warnings=0, num_patches=8)
for e in log.all_logs:
    if e.log_type >= LogType.WARNING:
        print(e.log_type, e.message)
```

The same from the shell; exit code 0 is clean, 8 is "completed with errors", 4 a bad option index, 7 an exception:

```bash
holopatcher --game-dir GAME --tslpatchdata MOD_DIR --install --console [--namespace-option-index N]
```

The CLI prints `[Info] Install completed: E errors, W warnings, P patches` on stdout; `[Error]` lines go to stderr among a lot of colored `DEBUG(...)` noise, so grep stderr for `^\[Error\]` and stdout for `^\[Warning\]`. `--validate` parses the selected ini and writes nothing.

## Inspect a mod without installing

```python
from pathlib import Path
from pykotor.tslpatcher.reader import ConfigReader, NamespaceReader
from pykotor.tslpatcher.logger import PatchLogger

tpd = Path(mod_dir) / "tslpatchdata"
for ns in NamespaceReader.from_filepath(tpd / "namespaces.ini"):  # skip if the mod has only changes.ini
    print(ns.namespace_id, ns.name, ns.changes_filepath(), ns.rtf_filepath())

reader = ConfigReader.from_filepath(tpd / "changes.ini", PatchLogger(), tslpatchdata_path=tpd)
cfg = reader.load(reader.config)  # PatcherConfig
print(cfg.window_title, cfg.required_files, cfg.patch_count())
for f in cfg.install_list:
    print("install", f.destination, f.sourcefile, f.replace_file)
for p in cfg.patches_2da:
    print("2da", p.sourcefile, [type(m).__name__ for m in p.modifiers])
for p in cfg.patches_gff:
    print("gff", p.destination, p.sourcefile, "->", p.saveas, len(p.modifiers))
for p in cfg.patches_nss:
    print("compile", p.sourcefile, "->", p.destination, p.saveas)
for p in cfg.patches_ncs:
    print("hack", p.sourcefile, len(p.modifiers))
for p in cfg.patches_ssf:
    print("ssf", p.sourcefile, len(p.modifiers))
print("tlk appends", len(cfg.patches_tlk.modifiers))
```

For a namespace, pass `tpd / ns.changes_filepath()` (it includes the option's `DataPath`). `ConfigReader.load` writes nothing; `PatchLogger` prints every message it records to stdout (errors to stderr) as it records it, so redirect them if the output matters.

## What each list does

Install order in `ModInstaller.install` (`tslpatcher/patcher.py`): InstallList, TLKList, 2DAList, GFFList, CompileList, HACKList, SSFList. A patch's input is the game's file at its destination if one exists and the patch is not a replace; otherwise the copy in `tslpatchdata` (never the game's `chitin` original: a 2DA not yet in `Override` is patched from the one the mod ships). A destination that is a `.mod`/`.erf`/`.rim` is patched inside the capsule, and a missing `modules\X.mod` is first built from `X.rim` + `X_s.rim`.

- **`[InstallList]`** (`mods/install.py`, `InstallFile`): copies files into a folder or capsule. `File#=` skips a file that already exists; `Replace#=` overwrites.
- **`[TLKList]`** (`mods/tlk.py`): `StrRef#=N` appends entry N of the mod's `append.tlk` to `dialog.tlk` (and `dialogf.tlk` if present) and stores the new strref in token `StrRef#` for later lists.
- **`[2DAList]`** (`mods/twoda.py`): `ChangeRow`, `AddRow`, `CopyRow`, `AddColumn` on a 2DA; cells take constants, `StrRef#`, `2DAMEMORY#`, `high()`; `2DAMEMORY#=RowIndex` (or a column) stores a value for later lists.
- **`[GFFList]`** (`mods/gff.py`): `Field=value` modifies a field (path with `\`), `Field(strref)=` a localized string's strref, `AddField#=` / structs into lists, `2DAMEMORY#=!FieldPath`. `!Destination=modules\x.mod` targets a capsule.
- **`[CompileList]`** (`mods/nss.py`, `ModificationsNSS`): copies every `.nss` in the folder to `temp_nss_working_dir/`, replaces `#StrRef#` / `#2DAMEMORY#` tokens, and compiles with pykotor's built-in compiler (off Windows always; see `scripts.md` for what that compiler gets wrong). Includes resolve from that folder first, then pykotor's bundled `k_inc_*`.
- **`[HACKList]`** (`mods/ncs.py`): writes values at byte offsets of an existing NCS (`u8`/`u16`/`u32`, `StrRef#`, `2DAMEMORY#`).
- **`[SSFList]`** (`mods/ssf.py`): sets sound-set slots (`Battlecry 1=StrRef0`) in an SSF.
- **`[Settings]`**: `WindowCaption` (the option's name when there is no namespace), `ConfirmMessage`, `Required`/`RequiredMsg` (files that must already be in `Override`, else `ImportError`), `LookupGameNumber`.

`[HACKList]` is described from source and not verified; the other lists behave as described against a game copy.

## Traps

- **It writes into the mod folder.** Every install creates `backup/<timestamp>/` (a copy of each game file it touches; `dialog.tlk` alone is 5 MB) and `uninstall/` beside `tslpatchdata/`, and a CompileList creates `temp_nss_working_dir/` inside it. Point it at a writable, disposable copy of the mod, never at a shared or read-only extraction.
- **Destination folder case creates folders.** A destination folder is used as spelled even when another spelling exists: a mod whose InstallList says `override` or `OVERRIDE` installs into a new folder beside `Override/` on a case-sensitive filesystem (JC's Mandalorian Armor does this). An existing capsule is found case-insensitively (`Modules\DANM13.mod` patched `modules/danm13.mod`). Symlink the other spellings to the real folder before installing, or merge after.
- **Headless uninstall does not work.** `--uninstall` stops at a Tk confirmation dialog (`TclError: no display name`, exit 7). Restore from a pristine copy instead.
- **`LookupGameNumber` is not the game.** K1 mods commonly carry `LookupGameNumber=2`; it only steers the GUI's folder lookup. The installer detects the game from the game folder (`tools/heuristics.py`, by marker files such as `swkotor.exe`, `rims/`, `data/party.bif`) and refuses a folder it cannot classify.
- **`ConfigReader.from_filepath` without `tslpatchdata_path`** fails with `AssertionError` on any mod with a `[CompileList]` and no `nwnnsscomp.exe` beside the ini.
- **`ModInstaller` directly**: `ModInstaller(tslpatchdata_dir, game_dir, ini_path, logger)` then set `.tslpatchdata_path` before `.install()`; this is what `core.install_mod` does. Patch errors do not raise; they are counted in `logger.errors`.
- **A `.mod` that does not exist yet is built from the `.rim`s** on the first patch into it; the game then prefers it over the `.rim`s.

Stock pykotor 2.3.12 has these defects, fixed by the [patch series](https://github.com/ivy/PyKotor/commits/modshop-patches) on the `modshop-patches` branch of the ivy/PyKotor fork (numbered as there, oldest first); on an unpatched install expect:

- **#1** Any mod with a `[CompileList]` is refused before patching: `ModificationsNSS.__init__() takes 2 positional arguments but 3 were given` (`load_compile_list` passes the keyword-only `replace` positionally).
- **#2** `Required files definitions must match required msg count` on a `changes.ini` with a lone `RequiredMsg=` or a lone `Required=`, which TSLPatcher accepts.
- **#3** A 2DA whose header says 0 for its cell-data size (an editor quirk the game ignores) reads as all-empty cells, and a `[2DAList]` patch writes the emptied table back.
- **#4** `KeyError('ininame')` on a `namespaces.ini` section without `IniName`/`InfoName`; TSLPatcher defaults them to `changes.ini`/`info.rtf`.
- **#6** `Replace#=` into a `.mod`/`.rim` that already holds the resource logs "replacing" but writes the old bytes back (`Capsule.add` copied the existing resources over the new one), so module fixes silently do nothing.
