# Reading an installation and its archives

`pykotor.extract` indexes a game folder (`chitin.key` + BIFs, `Override/`, `modules/`, `lips/`, `TexturePacks/`, the `stream*` folders, `dialog.tlk`) and resolves lookups across it. Source: `pykotor/extract/installation.py`, `capsule.py`, `file.py`, `talktable.py`; modules in `pykotor/common/module.py`.

## Minimal script

```python
import logging

logging.disable(logging.CRITICAL)  # before anything else: pykotor logs DEBUG on every path miss

from pykotor.extract.installation import Installation, SearchLocation
from pykotor.resource.type import ResourceType
from pykotor.resource.formats.twoda import read_2da

inst = Installation("/path/to/swkotor")  # ValueError if the folder has no chitin.key
res = inst.resource("appearance", ResourceType.TwoDA)  # ResourceResult | None
if res is not None:
    print(res.filepath, len(res.data))  # attributes, not methods
    table = read_2da(res.data)
```

Run it from a scratch directory with `2>/dev/null`: pykotor creates `logs/*pykotor*.log` in the current directory, and `logging.disable` does not silence the `print()` calls in `common/module.py`.

`Installation(path)` itself is instant; each source is indexed on first use and cached for the life of the object. The first `resource()` call indexes Override, `modules/` and chitin (~3 s on K1, most of it opening every module capsule); later lookups take ~0.2 ms. Build one `Installation` per script and reuse it.

## Find one resource

- `inst.resource(resname, restype, order=None, *, capsules=None, folders=None, module_root=None) -> ResourceResult | None`. Fields: `.resname`, `.restype`, `.filepath` (the BIF, capsule or loose file it came from), `.data` (bytes). Missing resources return `None`.
- Names are case-insensitive (`"APPEARANCE"` finds `appearance.2da`), and folder names are resolved case-insensitively too.
- Default `order` is `canonical_search_order()` in `pykotor/tools/finder.py`: `CUSTOM_FOLDERS, OVERRIDE, CUSTOM_MODULES, MODULES, CHITIN`. `CHITIN` covers the BIFs and then K1's `patch.erf`. Texture packs, lips and stream folders are **not** searched by default.
- Restrict or extend the search by passing `order` as a list of `SearchLocation`s: `[SearchLocation.CHITIN]` gives the unmodded BIF copy, `[SearchLocation.OVERRIDE]` only Override.
- `module_root="danm13"` limits the `MODULES` step to capsules of that module (`danm13.mod`, `.rim`, `_s.rim`, `_dlg.erf`); other steps still run.
- `capsules=[Capsule(...)]` with `SearchLocation.CUSTOM_MODULES`, or `folders=[Path(...)]` with `CUSTOM_FOLDERS`, searches extra places ahead of the install. Both are in the default order.
- Other sources by `SearchLocation`: `TEXTURES_TPA`/`TPB`/`TPC`/`GUI` (`TexturePacks/swpc_tex_*.erf`), `LIPS`, `MUSIC`, `SOUND` (StreamSounds), `VOICE` (StreamWaves on K1, StreamVoice on K2, searched recursively).
- `inst.resources([ResourceIdentifier(...), ...])` or `inst.resources((["appearance", "baseitems"], [ResourceType.TwoDA]))` batches lookups; returns `dict[ResourceIdentifier, ResourceResult | None]`. `find_one(ResourceQuery(name, type), scope)` is the same lookup under another name.
- `inst.texture(name, order=None) -> TPC | None` searches Override, the texture packs, then chitin, and returns a decoded `TPC`. `inst.sound(name, order=None) -> bytes | None` searches Override, StreamSounds, chitin.

## Where did it come from

```python
for loc in inst.location("appearance", ResourceType.TwoDA):  # list[LocationResult], highest priority first
    print(loc.filepath.relative_to(inst.path()), loc.offset, loc.size)
# Override/appearance.2da 0 101945
# data/2da.bif 42748 98610
```

`location()` takes the same `order`/`capsules`/`folders`/`module_root` as `resource()`, and also accepts a filename: `inst.location("appearance.2da")`. `locations(queries)` is the batch form returning `dict[ResourceIdentifier, list[LocationResult]]`. `loc.as_file_resource()` gives the `FileResource` for reading `.data()`. The first entry is what `resource()` returns; the rest are shadowed copies.

## Iterate everything

```python
for fr in inst.chitin_resources():  # list[FileResource]
    fr.resname(), fr.restype().extension, fr.filename(), fr.filepath(), fr.data()
for name in inst.modules_list():  # filenames: "danm13.mod", "danm13_s.rim", ...
    for fr in inst.module_resources(name):
        ...
inst.override_resources()  # flat list; override_list() gives subfolder keys, "." is the top level
inst.lips_list(), inst.lip_resources(name)
inst.texturepacks_list(), inst.texturepack_resources("swpc_tex_tpa.erf")
inst.core_resources()  # chitin + patch.erf
```

`for fr in inst` yields chitin, Override, modules, lips and the two TLKs (91k entries on a modded K1; 1–6 s to index depending on the page cache, instant after); `inst.iter_all_resources()` also forces StreamMusic/Sounds/Waves and the texture packs (118k). Both yield every copy, not just the winning one: 118k entries were 76k distinct identifiers. Reading `.data()` for all 91k took ~8 s with a warm page cache.

`FileResource` exposes **methods**: `resname()`, `restype()`, `size()`, `offset()`, `filepath()`, `filename()` (`"name.ext"`), `identifier()`, `data()`. For a BIF entry `filepath()` is the `.bif`; for a capsule entry it is the capsule.

## Open one archive

```python
from pykotor.extract.capsule import Capsule

cap = Capsule(inst.module_path() / "danm13.mod")  # .mod/.rim/.erf/.sav; ValueError on other extensions
len(cap)  # entries
for fr in cap:
    ...  # FileResource
cap.resource("m13aa", ResourceType.GIT)  # bytes | None (not a ResourceResult)
cap.info("m13aa", ResourceType.GIT)  # FileResource | None
cap.contains("M13AA", ResourceType.GIT)  # True, case-insensitive
```

`Capsule` reads the archive's table once at construction; `resource`/`info`/`contains` are linear scans of that table. A `Capsule` is itself a `FileResource` for the archive file, so `cap.resname()` is `"danm13"`. Writing into a capsule (`Capsule.add`/`delete`) is unreliable on stock pykotor 2.3.12; build archives with the format writers instead.

## A module as the game sees it

```python
from pykotor.common.module import Module

m = Module(
    "danm13", inst, load_textures=False
)  # uses danm13.mod if present, else .rim + _s.rim (+ _dlg.erf on K2)
m.capsules()  # the capsules actually used
git = m.git()  # ModuleResource | None; also are(), ifo(), layout(), creatures(), ...
git.active(), git.resource()  # path it loads from, decoded GIT object
m.resource("m13aa", ResourceType.GIT).data()
```

`Module` is the only API here that applies the engine's rule that `<root>.mod` replaces `<root>.rim` and `<root>_s.rim`. `use_dot_mod=False` gives the `.rim` view. `load_textures=True` (the default) walks every model for textures: 2.7 s versus 0.06 s for one area. `ModuleResource.data()` re-parses the capsule on every call (~16 ms each).

## Strings and game detection

```python
inst.talktable().string(42)  # str; "" for -1 or out of range
inst.talktable().batch(
    [42, 43]
)  # {strref: StringResult(text, sound)} with one file handle; 49k entries in 0.2 s
inst.talktable().size(), inst.talktable().sound(42)
inst.string(locstring)  # LocalizedString -> text, falling back to its embedded substrings
inst.female_talktable()  # dialogf.tlk, present only in some localisations
inst.game()  # Game.K1 / Game.K2 (pykotor.common.misc.Game); .is_k1(), .is_k2()
```

## Traps

- **`resource()` does not apply `.mod`-over-`.rim`.** Within the `MODULES` step it takes the first hit in directory-listing order. On a modded K1, 160 `.rim`/`_s.rim` files list before their `.mod`, so `resource("m42aa", GIT)` returned `unk_m42aa.rim` while the game loads `unk_m42aa.mod`. Use `Module`, or `location()` and prefer the `.mod` entry yourself.
- **Two object shapes.** `ResourceResult` and `LocationResult` are dataclasses with attributes (`.data`, `.filepath`); `FileResource` uses methods (`.data()`, `.filepath()`, `.restype().extension`). `Capsule.resource()` returns plain bytes.
- **The index is a snapshot.** Files added or deleted after first use are invisible or raise `FileNotFoundError` on read. `load_override()` is a no-op once loaded; use `reload_override(".")` (or the subfolder), `reload_module("name.mod")`, or a new `Installation`.
- **`get_decoded()`, `get_utc()`, `get_utp()`, `ResourceResult.decode()` are broken**: they return `str(obj)` (`"<...UTC object at 0x...>"`), and for types without a registered decoder (2DA) raise `UnicodeDecodeError`. Parse `.data` with the format reader (`read_2da`, `read_gff`, `read_utc`, ...).
- **`sound()` misses voice-over and alters bytes.** Its default order omits `VOICE`; pass `[SearchLocation.VOICE]`. It returns a re-encoded WAV (58 bytes shorter than the file); use `resource(name, ResourceType.WAV, [SearchLocation.VOICE])` for the raw file.
- **Texture packs are outside the default order.** `resource("<tex>", ResourceType.TPC)` returns `None` for a texture that only lives in `swpc_tex_tpa.erf`; pass the `TEXTURES_*` locations or use `texture()`.
- **K1 Override subfolders are counted twice.** A file in `Override/sub/` appears under both `"sub"` and `"."`, so `override_resources()` and `location()` list it twice.
- **`module_names()` is not a module list.** It opens every module to read its ARE name (~1.7 s) and returns `{filename: area name}`. Use `modules_list()` for filenames.
- **Missing names are quiet.** `module_resources("typo.mod")` prints to stderr and returns `[]`; `resource()` with a list of restypes returns `None` if none match.
- **Logging.** Every resolution of a path that does not exist logs a DEBUG line from `pykotor/tools/path.py`; repeated lookups against absent files (e.g. a missing `patch.erf` or `dialogf.tlk`) fill stderr. `logging.disable(logging.CRITICAL)` first.
