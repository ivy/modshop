# Finding references

"What uses this strref / resref / tag / script?" Answer it by parsing, not by byte-grepping: parse every GFF and walk its fields, decode NCS instructions, read 2DA columns. Timings below are for an unmodded K1 install (about 65,000 resources); a modded install with a large Override is about 1.7 times slower.

Run Python with `-I`, from a scratch directory (importing pykotor writes `logs/` into the current directory), and call `logging.disable(logging.CRITICAL)` before importing pykotor so the console is not flooded.

## Fastest: one pass for every name in the chain

pykotor's finders re-read and re-parse the whole installation on every call (6-14 s each). When you are following a chain you want several names and strrefs at once; this script answers all of them in one pass (7 s on vanilla K1). Names match whole values, case-insensitively, in GFF `ResRef`/`String` fields and NCS string constants; numbers match GFF `LocalizedString` strrefs and NCS integer constants.

```python
# whouses.py GAME_ROOT NAME_OR_STRREF...
import logging, struct, sys, time

logging.disable(logging.CRITICAL)
from pykotor.extract.installation import Installation
from pykotor.resource.formats.gff import GFFFieldType, read_gff
from pykotor.resource.formats.ncs import NCSInstructionType, read_ncs
from pykotor.resource.type import ResourceType

inst = Installation(sys.argv[1])
names = {a.lower() for a in sys.argv[2:] if not a.isdigit()}
strrefs = {int(a) for a in sys.argv[2:] if a.isdigit()}
S = GFFFieldType


def walk(st, path, hit):
    for label, ft, v in st:
        p = f"{path}.{label}" if path else label
        if ft in (S.ResRef, S.String) and str(v).lower() in names:
            hit(p, str(v))
        elif ft == S.LocalizedString and v.stringref in strrefs:
            hit(p, v.stringref)
        elif ft == S.Struct:
            walk(v, p, hit)
        elif ft == S.List:
            for i, item in enumerate(v):
                walk(item, f"{p}[{i}]", hit)


needles = [n.encode() for n in names] + [b"\x04\x03" + struct.pack(">i", s) for s in strrefs]
t = time.perf_counter()
for res in inst:
    rt = res.restype()
    where = f"{res.filename()} ({res.filepath().name})"
    hit = lambda p, v: print(f"{where}  {p} = {v}")
    if rt.is_gff():
        try:
            walk(read_gff(res.data()).root, "", hit)
        except ValueError, OSError:
            pass
    elif rt == ResourceType.NCS:
        data = res.data()
        if not any(n in data.lower() if n[:2] != b"\x04\x03" else n in data for n in needles):
            continue
        for ins in read_ncs(data).instructions:
            if ins.ins_type == NCSInstructionType.CONSTS and ins.args[0].lower() in names:
                hit("CONSTS", ins.args[0])
            elif ins.ins_type == NCSInstructionType.CONSTI and ins.args[0] in strrefs:
                hit("CONSTI", ins.args[0])
print(f"{time.perf_counter() - t:.1f}s", file=sys.stderr)
```

```bash
python -I whouses.py "$GAME" 42724 44230 k_transabort k_trans_abort k_trg_transfail k_trg_transfail1
```

Output lines are `resource (container)  field.path = value`; the container is the BIF, RIM or MOD it came from. It does not read 2DA or SSF; use `find_strref_references` below for strrefs in those.

## pykotor's finders

`pykotor/tools/reference_finder.py` (resref/tag/script finders) and `pykotor/tools/reference_cache.py` (strref finders). All take an `Installation` and iterate it: `chitin.key` BIFs, `Override`, `modules/` (RIM, `_s.rim`, MOD), `lips/` and `dialog.tlk`. Iteration does **not** cover `rims/`, `patch.erf`, `TexturePacks/` or the stream folders, so neither do the finders, although `inst.resource()` does find `patch.erf` entries.

| Function | Matches | NCS? |
|---|---|---|
| `find_script_references(inst, resref)` | any GFF `ResRef` field | yes, `CONSTS` strings |
| `find_tag_references(inst, tag)` | GFF `String` fields labelled exactly `Tag` | no |
| `find_conversation_references(inst, resref)` | GFF `ResRef` fields labelled `Conversation` | no |
| `find_template_resref_references(inst, resref)` | `TemplateResRef`, `InventoryRes` | no |
| `find_quest_journal_references(inst, tag)` | DLG `Quest` strings, plus NCS strings | yes |
| `find_resref_references(inst, resref, *, field_names=None, field_types={ResRef}, search_ncs=False)` | the general form of the above | if `search_ncs` |
| `find_field_value_references(inst, value, *, field_names=None, field_types={String, ResRef})` | any GFF string or resref field | no |
| `references.find_referrers(inst, value, reference_kind="script"\|"tag"\|"conversation"\|"resref", module_root=None)` | dispatches to the above; `module_root` keeps results whose container path contains it | only for `"script"` |
| `find_strref_references(inst, strref: int)` | GFF `LocalizedString` strrefs, 2DA strref columns (a fixed per-game list in `extract/twoda.py`), SSF slots | **no** |
| `find_all_strref_references(inst, [strrefs])` | the same, many strrefs in one pass; returns `(dict[int, list], cache)` | **no** |

Shared keyword arguments on the string finders: `partial_match=False`, `case_sensitive=False`, `file_pattern` (fnmatch on the resource filename, e.g. `"*.dlg"`), `file_types` (upper-case extensions, e.g. `{"UTP", "NCS"}`), `logger`.

The string finders return `list[ReferenceSearchResult]`: `file_resource` (`.filename()` is the resource, `.filepath()` its container), `field_path` (`ReplyList[0].Script`, `Placeable List[8].TemplateResRef`, or `(NCS bytecode)`), `matched_value`, `file_type` (`"UTP"`, `"NCS"`), and `byte_offset` (NCS only: the offset of the string's length field). The strref finders return `list[StrRefSearchResult]` with `resource` and `locations`, each a `GFFRefLocation(field_path)`, `TwoDARefLocation(row_index, column_name)` or `SSFRefLocation(sound)`.

The NCS search decodes instructions linearly from the header, it does not byte-match; over all 12,647 vanilla K1 scripts it found exactly the `CONSTS` values `read_ncs` does. The strref NCS scanner exists but is commented out in both `find_strref_references` and the cache, so **no pykotor finder reports strrefs in scripts**.

```python
import logging, sys

logging.disable(logging.CRITICAL)
from pykotor.extract.installation import Installation
from pykotor.tools.reference_cache import find_strref_references
from pykotor.tools.reference_finder import find_script_references, find_tag_references

inst = Installation(sys.argv[1])
for r in find_strref_references(inst, 42724):
    print(r.resource.filename(), r.locations)
for r in find_script_references(inst, "k_trans_abort", file_types={"NCS"}):
    print(r.file_resource.filename(), r.field_path, r.byte_offset)
```

`references.extract_references(gff, "UTP")` goes the other way, listing what one GFF points at as `ExtractedReference(ref_kind, value, field_path)`. On DLGs it also emits bogus `script` entries whose value is a stringified `GFFList`; drop values that are not resref-shaped.

## Encodings, for when you must scan bytes

| Where | Strref | Resref / tag / script name |
|---|---|---|
| NCS | `CONSTI`: `04 03` + big-endian int32 | `CONSTS`: `04 05` + big-endian uint16 length + ASCII bytes |
| GFF | `LocalizedString` (CExoLocString): little-endian int32 | `ResRef`/`String` field: plain ASCII |
| 2DA | decimal text in a strref column | text in a cell |

Layouts per `pykotor/resource/formats/ncs/io_ncs.py`. The `CONSTI` pattern is selective in practice: every prefilter hit tested was confirmed by `read_ncs`. The GFF little-endian int32 is not: for strref 42724, 4 DLGs and 7 models contain the four bytes, and only one is a real `LocalizedString`. Parse GFFs; never trust a raw int32 hit, and always skip `.mdl`/`.mdx`.

Strrefs in scripts, which no pykotor finder covers (4 s on vanilla K1):

```python
import logging, struct, sys

logging.disable(logging.CRITICAL)
from pykotor.extract.installation import Installation
from pykotor.resource.formats.ncs import read_ncs, NCSInstructionType
from pykotor.resource.type import ResourceType

inst = Installation(sys.argv[1])
strref = int(sys.argv[2])
needle = b"\x04\x03" + struct.pack(">i", strref)  # CONSTI: opcode 04, qualifier 03, big-endian int32
for res in inst:
    if res.restype() != ResourceType.NCS:
        continue
    data = res.data()
    if needle not in data:  # fast byte prefilter
        continue
    ncs = read_ncs(data)  # confirm it is a real CONSTI, not operand bytes
    if any(i.ins_type == NCSInstructionType.CONSTI and i.args[0] == strref for i in ncs.instructions):
        print(res.filename(), res.filepath().name)
```

Strref 32128 (a `BarkString` in `k_inc_man.nss`) finds `k_pman_water02..09.ncs` in `manm27aa_s.rim`. A script that computes a strref (`32346 + nState`) carries only the base constant.

## Following a chain

1. Resolve the start: text to strref with `pykotor tlk2json` and `jq` (see the CLI reference); several strrefs often carry the same text, so search all of them.
2. At each hop, collect **every** name the found resource carries: its own resref, its `Tag`, its `TemplateResRef`, and the resrefs in its fields (`Conversation`, `Script*`, `On*`). A blueprint's resref, tag and conversation can all differ.
3. Search for all of them at once (`whouses.py`) and repeat on each new resource.
4. When nothing in the resources references the last name, look in the engine: the executable runs some scripts by fixed name (`grep -a` the executable; Steam's `swkotor.exe` is encrypted on disk, so its code has to be read from the running process). Global scripts usually ship their source: `scripts.bif` holds 1,774 `.nss` beside 1,784 `.ncs`; the 10,863 module scripts have none.

## Worked example (K1)

"[You must gather your party before venturing forth.]" is strrefs 42724 and 44230.

- 44230: `plev_elev_dlg.dlg` (`lev_m40ab_s.rim`) `EntryList[5].Text`, a separate elevator dialog.
- 42724: `k_transabort.dlg` (`templates.bif`) `ReplyList[0].Text`; that reply's `Script` is `k_trg_transfail1`.
- `k_transabort` is the `Conversation` of placeable blueprint `k_trans_abort.utp`, whose `Tag` and `TemplateResRef` are both `k_trans_abort` (one letter-and-underscore off the dialog's name).
- `k_trans_abort` is a `TemplateResRef` in 154 placeable instances in 74 module GITs, a palette entry in `placeablepalstd.itp`, and a `CONSTS` in `k_trg_transfail.ncs`, whose source is `AssignCommand(GetNearestObjectByTag("k_trans_abort"), ActionStartConversation(...))`.
- Nothing in the resources references `k_trg_transfail`; the name is a string in `swkotor.exe`, which runs the script itself.

pykotor's own finders reproduce every resource hop: `find_strref_references` 42724 (8 s), `find_conversation_references` `k_transabort` (6 s), `find_tag_references` `k_trans_abort` (6 s, the UTP only), `find_script_references` `k_trans_abort` (11 s, 157 hits including the NCS), and `find_script_references` `k_trg_transfail` (10 s, 0 hits, correctly). About a minute for the chain, against 7 s for one `whouses.py` pass.

## Traps

- **Search every name in the chain.** Searching the dialog name `k_transabort` finds only the UTP; the script names the placeable `k_trans_abort`. One name per hop gives a false "nothing references it".
- **Whole-value matching.** `k_trg_transfail` does not match `k_trg_transfail1` (default whole-word regex; underscores and digits are word characters). Use `partial_match=True`, or add the variant to the names you search.
- `find_tag_references` reads only GFF `Tag` fields. A tag used by a script (`GetObjectByTag("…")`) appears only through `find_script_references` or `find_resref_references(..., field_types={GFFFieldType.String, GFFFieldType.ResRef}, search_ncs=True)`.
- `find_referrers(kind="resref")` skips NCS; `kind="script"` includes it.
- Strrefs in NCS: not found by any pykotor finder; use the snippet above. 2DA columns that hold resrefs or script names are not searched by the string finders.
- `rims/` and `patch.erf` are outside `Installation` iteration (and so outside every finder); open them with `pykotor.extract.capsule.Capsule` if they matter.
- `find_strref_references` prints tracebacks to stdout for GFFs it cannot parse.
- Instance placement lives in GITs as `TemplateResRef`; a K1 GIT placeable entry holds only `TemplateResRef` and position, so a tag search finds only the blueprint.
