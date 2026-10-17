# Reading and writing resource formats

Verified against pykotor 2.3.12 with the [patch series](https://github.com/ivy/PyKotor/commits/modshop-patches) applied, and a vanilla KotOR 1 install. Source paths are package-relative. Set `logging.disable(logging.CRITICAL)` before importing; pykotor logs heavily and writes a `logs/` directory into the current directory.

| Format | Read / write | Module |
|--------|--------------|--------|
| GFF (any) | `read_gff`, `write_gff`, `bytes_gff`, `detect_gff` | `pykotor.resource.formats.gff` |
| 2DA | `read_2da`, `write_2da`, `bytes_2da` | `...formats.twoda` |
| TLK | `read_tlk(src, language=None)`, `write_tlk`, `bytes_tlk` | `...formats.tlk` |
| ERF/MOD/SAV | `read_erf`, `write_erf`, `bytes_erf` | `...formats.erf` |
| RIM | `read_rim`, `write_rim`, `bytes_rim` | `...formats.rim` |
| KEY / BIF | `read_key`; `read_bif(src, key_source=None)` | `...formats.key`, `...formats.bif` |
| TPC/TGA/DDS | `read_tpc(src, txi_source=None)`, `write_tpc`, `bytes_tpc` | `...formats.tpc` |
| TXI | `read_txi`, `write_txi`, `bytes_txi` | `...formats.txi` |
| MDL+MDX | `read_mdl(mdl, source_ext=mdx)`, `write_mdl(m, tgt, fmt, target_ext=)`, `bytes_mdl` | `...formats.mdl` |
| WOK/DWK/PWK | `read_bwm`, `write_bwm`, `bytes_bwm` (all take `regenerate_derived=True`) | `...formats.bwm` |
| LYT / VIS | `read_lyt`/`bytes_lyt`; `read_vis`/`bytes_vis` | `...formats.lyt`, `...formats.vis` |
| LIP / SSF / LTR / WAV | `read_lip`, `read_ssf`, `read_ltr`, `read_wav` (+ `write_*`, `bytes_*`) | `...formats.<name>` |
| NCS | `read_ncs`, `write_ncs`, `bytes_ncs` (compiling NSS: see the scripts reference) | `...formats.ncs` |
| UTC UTI UTP UTD UTE UTM UTS UTT UTW ARE GIT IFO JRL FAC PTH GUI DLG | `read_X`, `write_X`, `bytes_X`, `construct_X(gff)`, `dismantle_X(obj, game)` | `pykotor.resource.generics.<x>` (DLG: `generics.dlg`) |

## The universal pattern

- `read_X(source, offset=0, size=None, ...)`. `source` is a path (`str` or `Path`), `bytes`/`bytearray`/`memoryview`, or a binary stream. `offset`/`size` read a slice, e.g. `read_gff(blob, offset=4, size=n)`.
- `write_X(obj, target, file_format)`. `target` is a path, a `bytearray` (appended to) or a stream. Passing `bytes` is not supported, and a `BytesIO` target is closed after writing, so `getvalue()` then raises. Use `bytes_X(obj, file_format)` to get the bytes.
- `file_format` is a `ResourceType` or a `ToolsetFormat` (text forms: `GFF_XML`, `GFF_JSON`, `TwoDA_CSV`, `TwoDA_JSON`, `TLK_XML`, `TLK_JSON`, `MDL_ASCII`, `SSF_XML`, `LIP_XML`, ...). Both are in `pykotor.resource.type`; `ResourceType.GFF_XML` is an alias for `ToolsetFormat.GFF_XML`.
- On read, `*_auto.py` detects the format from the bytes (binary vs XML/JSON/CSV), so `read_2da("t.2da.csv")` and `read_gff(xml_bytes)` work without a format argument.
- `bytes_2da`, `bytes_gff`, `bytes_mdl` and `bytes_tpc` return `bytes`; `bytes_lyt`, `bytes_vis` and `bytes_ncs` return `bytearray`.

Loading from a game install (resolves Override, modules, BIFs):

```python
from pykotor.extract.installation import Installation
from pykotor.resource.type import ResourceType

inst = Installation(game_dir)
res = inst.resource("appearance", ResourceType.TwoDA)  # None if not found
res.data, res.filepath.name, res.restype  # bytes, e.g. "2da.bif"
inst.talktable().string(31360)  # strref -> text
```

## GFF

```python
from pykotor.resource.formats.gff import (
    read_gff,
    bytes_gff,
    GFF,
    GFFStruct,
    GFFList,
    GFFFieldType,
    GFFContent,
)
from pykotor.common.misc import ResRef
from pykotor.common.language import LocalizedString, Language, Gender

g = read_gff(data)
s = g.root  # g.content is GFFContent.UTC etc. (the 4-byte file type)
for label, ftype, value in s:
    ...  # ftype is a GFFFieldType
s.get_string("Tag")
s.get_resref("Conversation")
s.get_uint8("Gender")
s.get_int32(...)
s.get_single(...)
s.get_locstring("FirstName").stringref  # 31360; text lives in the TLK
s.acquire("Tag", "")  # default required; also the type to match
s.exists("Tag")
s.what_type("Tag")  # GFFFieldType.String == 10
s.set_string("Tag", "x")
s.set_resref("Conversation", ResRef("k_foo"))
s.set_uint8("New", 3)
s.set_locstring("FirstName", LocalizedString.from_english("Bas"))  # stringref -1
s.set_locstring("LastName", LocalizedString(12345))  # strref only
items = s["Equip_ItemList"]  # live GFFList; s.get_list(...) is a copy
st = items.add(struct_id)
st.set_resref("EquippedRes", ResRef("g_w_blstrpstl01"))
new = GFF(GFFContent.UTI)  # header "UTI V3.2"; GFF() gives "GFF V3.2"
```

Field types: `UInt8 Int8 UInt16 Int16 UInt32 Int32 UInt64 Int64 Single Double String ResRef LocalizedString Binary Struct List Vector3 Vector4`. Each has `get_<type>`/`set_<type>` (`get_vector3`, `get_binary`, `get_struct`, `get_list`, ...). `g.print_tree()` dumps the tree to stdout.

Text dumps: `bytes_gff(g, ToolsetFormat.GFF_XML)` writes and reads back losslessly except for the file type: the read-back has `content == GFFContent.GFF`, so set `g.content = GFFContent.UTC` before writing binary or the header says `GFF `. With that set, a UTC and a UTI round-tripped through XML byte-identically. `GFF_JSON` writes but cannot be read back (see Traps). Binary GFF read→write is byte-identical.

## Generics: typed objects vs raw GFF

```python
from pykotor.resource.generics.utc import read_utc, bytes_utc, construct_utc, dismantle_utc
from pykotor.common.misc import Game

u = read_utc(data)  # u.tag, u.first_name (LocalizedString), u.appearance_id, u.conversation
out = bytes_utc(u, Game.K1)  # same as bytes_gff(dismantle_utc(u, Game.K1))
```

Use a generic to read many fields by name or build a resource from scratch. Use raw GFF to change a few fields in an existing file: it round-trips byte-identically and keeps every field. The generic writer emits its own field set: on a vanilla K1 creature it added `ItemList`, `Morale*`, `Save*`, `Portrait`; on a K1 dialog it dropped `AmbientTrack`, `AnimatedCut`, `ComputerType`, `OldHitCheck`, `UnequipHItem`, `UnequipItems`; any field it does not model is dropped. `use_deprecated=False` drops more (`Deity`, `Phenotype`, `TemplateList`, ...).

DLG (`pykotor.resource.generics.dlg`): `dlg.starters` is a list of `DLGLink`; `link.node` is a `DLGEntry` (NPC line), whose `.links` lead to `DLGReply` nodes, and so on alternately. A link carries the condition (`active1`, `active2`, a ResRef, plus `*_not` and `*_param*`) and `is_child` (true for a link into a node that is owned elsewhere). Nodes are shared: several links can point at the same node object, so walk with a visited set, or use `dlg.all_entries()` / `dlg.all_replies()`. Node fields include `text` (LocalizedString), `speaker`, `listener`, `script1`, `vo_resref`, `sound`, `comment`.

Other generics: `GIT` has `.creatures`, `.doors`, `.placeables`, ... each with `.resref` and `.position`; `IFO` has `.entry_position`, `.on_enter`, ...; `JRL` has `.quests[i].entries`.

## 2DA

```python
from pykotor.resource.formats.twoda import TwoDA, read_2da, bytes_2da

t = read_2da(data)
t.get_headers()  # column names, excluding the row-label column
t.get_height(), t.get_width()
for row in t:
    row.label(), row.get_string("name"), row.get_integer("page", -1)  # -1 if blank
t.get_cell(i, "name")
t.set_cell(i, "page", 5)  # values stored as str
t.get_column("name")
t.get_label(i)
t.find_row("action203")  # TwoDARow or None
i = t.add_row(str(t.get_height()), {"name": "Test"})  # missing columns blank, unknown keys ignored
t.add_column("newcol")
t.remove_column("newcol")
t.copy_row(row, "80")
```

A column called `label` (as in `appearance.2da`) is an ordinary column, distinct from `row.label()`. `get_cell` with an unknown column raises `KeyError`. Binary 2DA read→write is byte-identical. K1 `keymap.2da` columns: `disabled actionstrref descstrref language0 character page sortpos name remappable forcedisplay icpc icminigame icpcgui icdialog icfreelook icmovie repeatable repeatwait repeatrate scale scalemag scaleexp`; row labels are `action200`, ...

## TLK

```python
from pykotor.resource.formats.tlk import TLK, read_tlk, bytes_tlk

tlk = read_tlk(game_dir / "dialog.tlk")  # tlk.language == Language.ENGLISH
e = tlk.entries[42]
e.text, str(e.voiceover)  # voiceover is a ResRef ("" if none)
tlk.get(n)  # TLKEntry or None when out of range
new_ref = tlk.add("text", "vo_resref")
tlk.replace(new_ref, "changed")
```

Text is encoded by the TLK's language (`Language.ENGLISH.get_encoding()` is `cp1252`). Read→write keeps every text and voiceover but is not byte-identical: the writer recomputes each entry's flags.

## ERF / MOD / RIM

```python
from pykotor.resource.formats.erf import ERF, ERFType, read_erf, write_erf
from pykotor.resource.formats.rim import read_rim

rim = read_rim(game_dir / "modules/danm13.rim")
for r in rim:
    str(r.resref), r.restype, r.data
rim.get("module", ResourceType.IFO)  # bytes or None
mod = ERF(ERFType.MOD)
for r in rim:
    mod.set_data(str(r.resref), r.restype, r.data)
write_erf(mod, "out/danm13.mod")  # header "MOD V1.0"
```

The header comes from `erf_type`, not from `file_format`: `write_erf(ERF(), "x.mod", ResourceType.MOD)` writes `ERF V1.0`. A module's area resources are named after the area (`m13aa.are`), not the module file. `read_bif` without `key_source` returns resources with empty names; pass the `chitin.key`.

## Textures

```python
from pykotor.resource.formats.tpc import read_tpc, bytes_tpc, TPCTextureFormat

tpc = read_tpc(data)  # also reads TGA and DDS (auto-detected)
TPCTextureFormat(tpc.format()).name, tpc.dimensions()  # 'DXT5', (width, height)
tga = bytes_tpc(tpc, ResourceType.TGA)  # also DDS, BMP; decodes DXT itself
tpc.convert(TPCTextureFormat.RGBA)  # required before PIL
tpc.get(0, 0).to_pil_image().save("x.png")  # layer 0, mipmap 0
tpc.txi  # embedded TXI text
```

TGA/DDS/BMP output needs no extra packages. PNG goes through Pillow (`to_pil_image`), which pykotor declares only under its `font` extra. `to_pil_image()` on a DXT mipmap raises `ValueError: unrecognized image mode`; convert to RGBA first. `inst.texture(name)` returns a `TPC` from the install. The TGA reader rejects colour-mapped TGAs.

## Models, walkmeshes, layouts

```python
from pykotor.resource.formats.mdl import read_mdl, write_mdl

m = read_mdl(mdl_bytes, source_ext=mdx_bytes)
m.name, len(m.all_nodes()), m.all_textures()
mdl_out, mdx_out = bytearray(), bytearray()
write_mdl(m, mdl_out, ResourceType.MDL, mdx_out)
bytes_mdl(m, ToolsetFormat.MDL_ASCII)  # ASCII model text
```

Without `source_ext`, `read_mdl` still loads node positions but every mesh has no normals or UVs. MDL write is not byte-identical.

LYT: `read_lyt(d).rooms[i].model`/`.position`, plus `.tracks`, `.obstacles`, `.doorhooks`. VIS: `vis.all_rooms()`, `vis.get_visible(a, b)`, `vis.set_visible(a, b, True)`. BWM: `.faces` (each with `v1 v2 v3 material trans1..3`), `.find_face_at(x, y)`, `.get_height_at(x, y)`.

## ResourceType

`from pykotor.resource.type import ResourceType`. Member names are not extensions: `ResourceType.TwoDA.extension == "2da"`, `str(ResourceType.TwoDA) == "2DA"`, `int(ResourceType.TwoDA) == 2017`. `ResourceType.from_extension(".TPC")` ignores case and a leading dot; `from_extension("2da.csv")` returns `ToolsetFormat.TwoDA_CSV`; an unknown extension returns a falsy invalid member (test with `if not rt`), not an exception. `ResourceType.from_id(2017)`. Equality also matches an extension string or an id: `ResourceType.TwoDA == "2da"` and `== 2017`. `rt.is_gff()` is true for UTC, DLG, ARE, ... K1 names: `TwoDA TLK GFF UTC UTI UTP UTD UTE UTM UTS UTT UTW DLG ARE GIT IFO JRL FAC PTH GUI ERF MOD RIM SAV BIF KEY TPC TGA DDS TXI MDL MDX WOK DWK PWK LYT VIS LIP SSF LTR WAV NCS NSS`.

## Raw bytes

For parsing without pykotor (all little-endian):

- TPC: data size uint32 at 0, alpha-test float at 4, width uint16 at 8, height uint16 at 10 (`formats/tpc/io_tpc.py`). Reading uint16s at 4 gives the float's halves (`0, 16256` for 1.0).
- TGA: width uint16 at 12, height uint16 at 14 (`formats/tpc/tga.py`).
- DDS: `DDS ` magic, header size at 4, flags at 8, height uint32 at 12, width uint32 at 16 (`formats/tpc/io_dds.py`). A 2048×1024 texture has 1024 at 12.
- GFF ResRef field: uint8 length, then that many ASCII bytes; max 16 (`formats/gff/io_gff.py`).
- GFF CExoLocString: uint32 total size, then strref as uint32 (`0xFFFFFFFF` = none, read as -1), then substring count and `(id, length, text)` triples; substring id = language×2 + gender (`common/stream.py`, `read_locstring`).
- 2DA binary: `2DA V2.b\n`, tab-separated headers ended by NUL, uint32 row count, tab-ended row labels, uint16 offset per cell, uint16 cell-data size, then NUL-terminated cell strings.

## Traps

- **Generic writers default to `Game.K2`.** `write_utc(u, path)` writes TSL fields into a K1 file. Always pass `Game.K1`.
- **GFF getters never raise.** A missing field or a type mismatch returns the default: `get_uint8("Tag")` on a String field returns `0`, `get_resref("Nope")` returns `None`. Check `exists()`/`what_type()` when it matters.
- **`get_struct` and `get_list` return copies.** Setting fields on a `get_struct` result, or `add` on a `get_list` result, does not change the file; structs already inside a copied list are shared, so edits to them do. Use `s["Label"]` for the live object, or write back with `set_struct`/`set_list`. `s["X"] = v` raises `TypeError`; use `set_*`. `get_locstring` returns the live object.
- **`set_resref` accepts a plain `str`** and writes it unvalidated. `ResRef("seventeen_chars_x")` silently truncates to 16; `ERF.set_data`/`RIM.set_data` truncate the same way. Non-ASCII raises `InvalidEncodingError`.
- **Encoding:** a GFF String with a character outside cp1252 fails the whole write with the generic `ValueError: Tried to save or load an unsupported or corrupted file.`; LocalizedString substrings and TLK text silently become `?`.
- **`read_gff` of GFF JSON fails** with `AttributeError: ... GFFFieldType has no attribute 'Data'` for any file with a String or ResRef field (`formats/gff/gff_data.py`, `_parse_field_value_static`). Use `GFF_XML` for an editable text form.
- **XML read-back loses the file type** (`GFFContent.GFF`); set `g.content` before writing binary.
- **`add_row(None)` labels the new row with index+1**, not its index. Pass the label: `t.add_row(str(t.get_height()), ...)`. `label_max()` returns max numeric label + 1 and is 0 for tables with non-numeric labels like keymap.
- **2DA files whose header gives 0 for the cell-data size:** with the [patch series](https://github.com/ivy/PyKotor/commits/modshop-patches) pykotor reads cells by offset, as the game does (`formats/twoda/io_twoda.py`). Stock pykotor 2.3.12 reads every cell of such a file as empty, so reading and writing it back on stock pykotor destroys the table.
- **Lossy round trips:** VIS is rewritten lowercased, LF-terminated and reordered; LYT loses its final CRLF; WOK/BWM, MDL, TLK (flags) and WAV are not byte-identical; generics change the field set. Compare semantically, or patch raw GFF/2DA when byte stability matters.
- **`write_X(obj, BytesIO())` closes the stream**; use `bytes_X` or a `bytearray` target.
- **Missing MDX:** `read_mdl(mdl)` without `source_ext` succeeds but drops normals and UVs; writing that model back destroys them.
- **`TPCTextureFormat` values print as ints** (`tpc.format()` shows `3`); wrap in `TPCTextureFormat(...)` for the name.
