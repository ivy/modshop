#!/usr/bin/env python3
"""Oops! All Juhani: install the mod's scripts, dialogs, voice and clone blueprints into the build.

    make.py <game dir> <nws> <ffmpeg> <rhubarb>

The clone blueprints are Juhani's own (dan14_juhani.utc, the copy the build loads) with a new tag,
the clone spawn script, no conversation, no floor on her hit points, nothing to drop, and half her
ability scores, hit points and Force points. The scripts compile with the nws given, against the
build's own nwscript.nss and includes. The dialogs are the build's own with SCRIPT.md's scenes added
(scenes.py), voiced from voice/ by voice.py. The story's flags are added to globalcat.2da.
k_pdan_juhani31 and k_pdan_14juh_d replace the game's scripts of those names, so the step stops if
any copy of either in the build is not the game's: a mod's change to it would be dropped.
"""

import hashlib
import logging
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

logging.disable(logging.CRITICAL)  # pykotor logs every path miss

from pykotor.common.misc import ResRef  # noqa: E402
from pykotor.extract.capsule import Capsule  # noqa: E402
from pykotor.extract.installation import Installation  # noqa: E402
from pykotor.resource.formats.gff import bytes_gff, read_gff  # noqa: E402
from pykotor.resource.formats.twoda import bytes_2da, read_2da  # noqa: E402
from pykotor.resource.type import ResourceType  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # isolated mode leaves the script's own folder off the path

import scenes  # noqa: E402
from dialog import Dialog  # noqa: E402
from voice import Line, make_all  # noqa: E402

LIBRARY = "k_oaj_inc"  # included by the others, not compiled on its own
SCRIPTS = tuple(sorted(p.stem for p in HERE.glob("k_*.nss") if p.stem != LIBRARY))
CLONES = ("oaj_juhani1", "oaj_juhani2")
CLONE_SPAWN = "k_oaj_clsp"
JUHANI = "dan14_juhani"
MODULE = "danm14ac"
# The game's scripts these replace, as danm14ac_s.rim ships them
REPLACED_SHA256 = {
    "k_pdan_juhani31": "f684480ac7b9ace19d012f2107eb1f28f916d2f7d349965fe0185559ec44ef28",
    "k_pdan_14juh_d": "02c307ed6ea5ae358fd85ce351ab85dce4f00ec6ecc8d32488f5942351dcef7e",
}
# Her script is BioWare's, decompiled: it compiles to their bytes against their declarations
BIOWARE = ("--declarations", "bioware", "--compat", "bioware")
BIOWARE_SCRIPTS = ("k_pdan_14juh_d",)
# A companion is hidden by a disguise as a creature whose model is the game's invisible placeable's.
# The row copies a small simple creature's (the brith's); for a simple model (S) the model is `race`.
HIDDEN_LABEL = "Juhani_Clones_Hidden"
HIDDEN_FROM = "Creature_Brith"
HIDDEN_MODEL = "PLC_Invis"
GENERATED_INCLUDE = "k_oaj_gen"
# The party's blueprints in NPC_* order (NPC_BASTILA = 0 ... NPC_ZAALBAR = 8): the scripts find a
# companion's NPC number by their tag, the one direction the engine offers
PARTY = ("p_bastilla", "p_cand", "p_carth", "p_hk47", "p_jolee", "p_juhani", "p_mission", "p_t3m4", "p_zaalbar")
# The story's flags (k_oaj_inc): the last insult, a companion down by NPC number, Carth recovered
# (his epilogue question), the banter given
GLOBALS = ("OAJ_SPECIAL", *(f"OAJ_DOWN_{n}" for n in range(len(PARTY))), "OAJ_DONE", "OAJ_BANTER")
STANDARD_FACTION_HOSTILE_1 = 1
HALVED_U8 = ("Str", "Dex", "Con", "Int", "Wis", "Cha")
HALVED_I16 = ("HitPoints", "CurrentHitPoints", "MaxHitPoints", "ForcePoints", "CurrentForce")
# Each dialog the mod adds to, and the scene that does it
DIALOGS: dict[str, Callable[[Dialog], list[Line]]] = {
    "dan14_cutjuh": scenes.cutscene,
    "dan14_juhani": scenes.defeat,
    "k_hcar_dialog": scenes.carth,
    "k_hmis_dialog": scenes.mission,
}
BANTER = "oaj_banter"  # a new dialog, with the settings of the game's party banter (banter.dlg)


def module_copies(game: Path, resname: str, restype: ResourceType) -> dict[str, bytes]:
    copies: dict[str, bytes] = {}
    for capsule in (game / "Modules").glob(f"{MODULE}*"):
        data = Capsule(capsule).resource(resname, restype)
        if data is not None:
            copies[capsule.name] = data
    return copies


def loaded(inst: Installation, game: Path, resname: str, restype: ResourceType) -> bytes:
    """The copy the game loads: Override's, then the module's (its .mod over its .rim), then the
    game's own."""
    loose = game / "Override" / f"{resname}.{restype.extension}"
    if loose.exists():
        return loose.read_bytes()
    copies = module_copies(game, resname, restype)
    for name in (f"{MODULE}.mod", f"{MODULE}.rim", f"{MODULE}_s.rim"):
        if name in copies:
            return copies[name]
    res = inst.resource(resname, restype)
    if res is None:
        raise SystemExit(f"the build has no {resname}.{restype.extension}")
    return res.data


def check_replaced(game: Path, override: Path) -> None:
    for script, sha256 in REPLACED_SHA256.items():
        if (override / f"{script}.ncs").exists():
            raise SystemExit(f"Override already holds a {script}.ncs from another mod")
        copies = module_copies(game, script, ResourceType.NCS)
        if not copies:
            raise SystemExit(f"no {script} in {MODULE}")
        for name, data in copies.items():
            if hashlib.sha256(data).hexdigest() != sha256:
                raise SystemExit(f"{name}'s {script} is not the game's; the replacement would drop what it does")


def clone_blueprint(juhani: bytes, tag: str) -> bytes:
    gff = read_gff(juhani)
    root = gff.root
    root.set_string("Tag", tag)
    root.set_resref("TemplateResRef", ResRef(tag))
    root.set_resref("ScriptSpawn", ResRef(CLONE_SPAWN))
    root.set_resref("ScriptUserDefine", ResRef(""))
    root.set_resref("Conversation", ResRef(""))
    root.set_uint8("Min1HP", 0)
    root.set_uint8("Plot", 0)
    root.set_uint16("FactionID", STANDARD_FACTION_HOSTILE_1)
    for label in HALVED_U8:
        root.set_uint8(label, max(1, root.get_uint8(label) // 2))
    for label in HALVED_I16:
        root.set_int16(label, max(1, root.get_int16(label) // 2))
    for label in ("ItemList", "Equip_ItemList"):
        if root.exists(label):
            for item in root[label]:
                item.set_uint8("Dropable", 0)
    return bytes(bytes_gff(gff))


def add_hidden_appearance(inst: Installation, override: Path) -> int:
    """The row's index in the build's appearance.2da, which gains it in Override."""
    res = inst.resource("appearance", ResourceType.TwoDA)
    if res is None:
        raise SystemExit("the build has no appearance.2da")
    table = read_2da(res.data)
    source = next((r for r in table if r.get_string("label") == HIDDEN_FROM), None)
    if source is None:
        raise SystemExit(f"appearance.2da has no {HIDDEN_FROM} row")
    if source.get_string("modeltype") != "S":
        raise SystemExit(f"{HIDDEN_FROM} is no longer a simple model")
    index = table.copy_row(source, str(table.get_height()), {"label": HIDDEN_LABEL, "race": HIDDEN_MODEL})
    (override / "appearance.2da").write_bytes(bytes_2da(table))
    return index


def add_globals(inst: Installation, override: Path) -> None:
    """The story's flags in the build's globalcat.2da, which the game needs to declare a global."""
    res = inst.resource("globalcat", ResourceType.TwoDA)
    if res is None:
        raise SystemExit("the build has no globalcat.2da")
    table = read_2da(res.data)
    taken = {row.get_string("name").upper() for row in table}
    for name in GLOBALS:
        if name in taken:
            raise SystemExit(f"globalcat.2da already declares {name}")
        table.add_row(str(table.get_height()), {"name": name, "type": "Boolean"})
    (override / "globalcat.2da").write_bytes(bytes_2da(table))


def party_tags(inst: Installation) -> list[str]:
    tags: list[str] = []
    for resname in PARTY:
        res = inst.resource(resname, ResourceType.UTC)
        if res is None:
            raise SystemExit(f"the build has no {resname}.utc")
        tags.append(read_gff(res.data).root.get_string("Tag"))
    return tags


def generated_include(hidden: int, tags: list[str]) -> str:
    cases = "".join(f'    if (nNPC == {n}) {{\n        return "{tag}";\n    }}\n' for n, tag in enumerate(tags))
    return (
        f"// Generated by Oops! All Juhani's make.py from the build's appearance.2da and party blueprints.\n\n"
        f"int APPEARANCE_HIDDEN = {hidden};\n\n"
        f"string NpcTag(int nNPC)\n{{\n{cases}    return \"\";\n}}\n"
    )


def includes(inst: Installation, out: Path) -> None:
    """nwscript.nss and every include the scripts reach, as the build resolves them; the mod's own
    and the ones make.py writes itself are left where they are."""
    want = ["nwscript", *(m for s in SCRIPTS for m in re.findall(r'#include\s+"(\w+)"', (HERE / f"{s}.nss").read_text()))]
    seen: set[str] = set()
    while want:
        name = want.pop().lower()
        if name in seen or (out / f"{name}.nss").exists():
            continue
        seen.add(name)
        if (HERE / f"{name}.nss").exists():
            source = (HERE / f"{name}.nss").read_text()
        else:
            res = inst.resource(name, ResourceType.NSS)
            if res is None:
                raise SystemExit(f"the build has no {name}.nss")
            (out / f"{name}.nss").write_bytes(res.data)
            source = res.data.decode("latin-1")
        want += re.findall(r'#include\s+"(\w+)"', source)


def compile_scripts(inst: Installation, nws: str, override: Path, hidden: int) -> None:
    with tempfile.TemporaryDirectory(prefix="oops-all-juhani-") as tmp:
        inc = Path(tmp)
        (inc / f"{GENERATED_INCLUDE}.nss").write_text(generated_include(hidden, party_tags(inst)))
        includes(inst, inc)
        for name in SCRIPTS:
            mode = BIOWARE if name in BIOWARE_SCRIPTS else ()
            argv = [nws, "-q", "--game", "k1", *mode, "-I", str(HERE), "-I", str(inc), "compile", str(HERE / f"{name}.nss"), "-o", str(override / f"{name}.ncs")]
            r = subprocess.run(argv, capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(f"{name}.nss does not compile:\n{r.stdout}{r.stderr}")


def dialogs(inst: Installation, game: Path, override: Path) -> list[Line]:
    lines: list[Line] = []
    for name, scene in DIALOGS.items():
        dlg = Dialog(loaded(inst, game, name, ResourceType.DLG))
        lines += scene(dlg)
        (override / f"{name}.dlg").write_bytes(bytes(dlg))
    if (override / f"{BANTER}.dlg").exists():
        raise SystemExit(f"Override already holds a {BANTER}.dlg")
    banter = Dialog.empty_like(loaded(inst, game, "banter", ResourceType.DLG))
    lines += scenes.banter(banter)
    (override / f"{BANTER}.dlg").write_bytes(bytes(banter))
    return lines


def main() -> None:
    game, nws, ffmpeg, rhubarb = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    override = game / "Override"
    check_replaced(game, override)
    inst = Installation(game)
    juhani = loaded(inst, game, JUHANI, ResourceType.UTC)
    lines = dialogs(inst, game, override)
    make_all(lines, ffmpeg, rhubarb, game)
    add_globals(inst, override)
    hidden = add_hidden_appearance(inst, override)
    compile_scripts(inst, nws, override, hidden)
    for tag in CLONES:
        (override / f"{tag}.utc").write_bytes(clone_blueprint(juhani, tag))
    print(f"Oops! All Juhani: {len(SCRIPTS)} scripts, {len(DIALOGS) + 1} dialogs, {len(lines)} voice lines, "
          f"{len(CLONES)} clones of {JUHANI}.utc, appearance {hidden} hidden, {len(GLOBALS)} globals")  # fmt: skip


if __name__ == "__main__":
    main()
