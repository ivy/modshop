"""The KOTOR 1 Full Build (Revision 12) as entries, minus what KMRP replaces or crashes with and
the two mods that crash on Linux.

Entry names are the archive folder names the downloader makes from the build's mod list
(`NNN-<slug>` from `k1full.json`), so the recipe reads nothing under `data/` and its canonical
JSON (`recipe.json` beside this file's data) is the same on every machine. Where the build
offers a choice, the entry records the one made; what is skipped says why.
"""

from __future__ import annotations

import json
from pathlib import Path

from modshop.core.recipe import Entry, Recipe, Step
from modshop.kotor.archives import folder_name
from modshop.kotor.steps import (
    ArchivePath,
    Copy,
    CopyFiles,
    DataPath,
    DedupeTpc,
    Delete,
    GameDir,
    HoloPatcher,
    Kmrp,
    OverrideDir,
    Rename,
    Script,
    StageCopyAs,
    StageDelete,
    StageDir,
    Symlink,
    Tlk,
)

KMRP = "crashes with KMRP (its issue #15)"
LINUX = "build warns it crashes on Linux"
REPL = "replaced by KMRP"


def mod_folders(game_dir: Path) -> dict[int, str]:
    mods = json.loads((game_dir / "build" / "k1full.json").read_text())
    titles = [m["title"] for m in mods if m["section"] == "Mod List"]
    return {n: folder_name(n, title) for n, title in enumerate(titles, start=1)}


def cp(src: str = "*", **kw: object) -> Copy:
    return Copy(src=src, **kw)  # pyright: ignore[reportArgumentType]


def cpf(src: str, names: list[str], **kw: object) -> CopyFiles:
    return CopyFiles(src=src, names=tuple(names), **kw)  # pyright: ignore[reportArgumentType]


def hp(src: str = "*/tslpatchdata", option: int | None = None, allow_errors: int = 0) -> HoloPatcher:
    return HoloPatcher(src=src, option=option, allow_errors=allow_errors)


def sdel(src: str, names: list[str]) -> StageDelete:
    return StageDelete(src=src, names=tuple(names))


def odel(names: list[str]) -> Delete:
    return Delete(names=tuple(names))


def repair(name: str, *args: GameDir | OverrideDir | StageDir | ArchivePath | DataPath) -> Script:
    """A repair folder's make.py, with the whole folder (README included) as key material."""
    return Script(path=f"./repairs/{name}/make.py", args=args, reads=(f"./repairs/{name}",))


def recipe(game_dir: Path) -> Recipe:
    dirs = mod_folders(game_dir)
    entries: list[Entry] = []

    def mod(
        n: int | str, *steps: Step, skip: str | None = None, inputs: tuple[str, ...] | None = None
    ) -> None:
        name = dirs[n] if isinstance(n, int) else n
        if inputs is None:
            inputs = (name,) if isinstance(n, int) else ()
        entries.append(Entry(name, inputs, tuple(steps), skip))

    def mega(name: str, archive: str, *steps: Step) -> None:
        mod(f"mega:{name}", *steps, inputs=(f"mega/{archive}",))

    # the two names the patcher and some mods' installers need beside the game's own folders
    mod("aliases", Symlink(link="Modules", target="modules"), Symlink(link="override", target="Override"))
    mod(1, Tlk(src="*/PC Response Moderation version/dialog.tlk"))
    mod(2, hp("*/tslpatchdata"))
    mega(
        "character-startup-patch",
        "Character_Startup_Changes_Patch.zip",
        cp("Character_Startup_Changes_Patch/Override"),
    )
    mod(3, skip=KMRP)
    mod(4, cp("*/Straight Fixes"), cp("*/Resolution Fixes"), cp("*/Aesthetic Improvements"),
        cp("*/Things What Bother Me Fixes", exclude=("N_AdmrlSaulKar.*", "N_SithCom*")))  # fmt: skip
    mega(
        "ajunta-pall-patch",
        "Ajunta Pall Unique Appearance.zip",
        hp("Ajunta Pall Unique Appearance/tslpatchdata"),
    )
    mod(5, cp("*/Non-Transparent Skins", pattern="*.tga"))
    mod(6, hp("K1_Community_Patch*/tslpatchdata", allow_errors=1), hp("k1cp-sithtroop/tslpatchdata"), cp("K1CP_v1.10.1*"),
        inputs=(dirs[6], "./fixes/k1cp-sithtroop"))  # fmt: skip
    mega("k1cp-patch", "K1CP Patch.rar", cp("K1CP Patch/K1CP Patch"))
    mod(7, hp())
    mod(8, hp(option=0), hp(option=1))
    for n in (9, 10, 11, 12, 13, 14):
        mod(n, cp("*/*/Override"))
    mega("korriban-patch", "Korriban Patch.7z", cp("Korriban Patch"))
    mod(15, sdel("*/*/Override", ["LSI_win01.tpc", "LSI_box01.tpc"]), cp("*/*/Override"))
    mod(16, cp("Ultimate Character Overhaul*/*"))
    mod(17, sdel("*/*/Override", ["LUN_blst01.tpc", "LUN_blst02.tpc"]), cp("*/*/Override"))
    mod(18, cp("Door Mural*/Override"), cp("Sith Art*/Override"))
    mega("duncan-on-manaan", "Duncan on Manaan.7z", cp("Duncan on Manaan", exclude=("*.kmm",)))
    mod(20, cp("*/*/Override"))
    mod(21, cp("*"))
    mod(22, cp("*/*/Override"))
    for n in (23, 24, 25, 26):
        mod(n, cp("*"))
    mod(27, cp("*/UPSCALED/FOR OVERRIDE"))
    mod(28, cp("*"))
    mod(29, cp("*/Creatures"))
    mod(30, cp("*/Quanon_Gammoreans"))
    for n in (31, 32, 33, 34):
        mod(n, cp("*"))
    mega("sand-people-patch", "HD Realistic Sand People Patch.zip", cp("HD Realistic Sand People Patch"))
    mod(35, hp(option=0))
    mod(36, cp("*"))
    mod(37, cp("*/*/NPC Replacement"))
    mod(38, cp("*/Override"))
    mega("calo-nord", "Calo Nord Recolor.zip", cp("Calo Nord Recolor/CN_Recolor/*/Override"))
    mod(40, cp("*/Malak (Red Eyes)"))
    mod(41, cp(".", pattern="*.tga"))
    mod(42, StageCopyAs(src="*/N_DarthRevan01.tga", new="PMBJ01.tga"), cp("*"))
    mod(43, cp("*"))
    mod(44, cp("*"))
    mod(45, cp("*/*/Party Selection"), cp("*/*/Planet Icons"))
    mod(46, cp("*/*/Override"))
    mod(47, sdel("NPC clothing M", ["n_commm07.tga", "N_CommMD01.tga", "N_CommM08.tga"]),
        StageCopyAs(src="NPC clothing M/N_CommM0801.tga", new="N_CommM08.tga"), cp("NPC clothing M"))  # fmt: skip
    mod(48, hp(option=0))
    mega("jao-saber-patch", "JAO_Saber_Replacement.7z", hp("JAO_Saber_Replacement/*/tslpatchdata"))
    mod(49, skip=KMRP)
    mod(50, hp(option=1, allow_errors=1))
    mod(51, hp(option=4))
    mod(52, hp(option=0))
    mod(53, cp("*/Jedi Robes Override"))
    mod(54, cp("*/*"))
    mod(55, sdel("*/Quanons_HK47_Reskin", ["PO_phk47.tga"]), cp("*/Quanons_HK47_Reskin"))
    mod(56, cp("*"))
    mod(57, cp("Kiosk HD*"), cp("Kiosk Model Fix*/*/K1"))
    mod(58, cp("*"))
    mod(59, cp("*"))
    mod(60, cp("*"))
    mod(61, hp("*/*/tslpatchdata", option=1))
    mod(62, cp("*"))
    mod(63, skip=LINUX)
    for n in (64, 65, 66, 67, 68):
        mod(n, cp("*"))
    mod(69, sdel("*", ["N_CommF02.tga", "N_CommF02.txi"]), cp("*"))
    mod(70, cp("*"))
    mod(71, cp("*"))
    mod(72, sdel("*", ["po_pt3m33.tga"]), cp("*"))
    mod(73, cp("*"))
    mod(74, cp("*/*/Override"))
    mod(75, sdel("*", ["PO_pcarth3.tga"]), cp("*"))
    mod(76, cp("*"))
    mega("canderous-patch", "Canderous Patch.rar", cp("Canderous Patch"))
    mod(77, cpf("*/Quanon_CandOrdo_Reskin", ["P_CandH01.tga"]))
    mod(78, cp("*"))
    mod(79, cpf("*/*", ["P_joleeh01.tga", "P_joleeh01.txi"]))
    mod(80, sdel("*", ["po_pzaalbar3.tga"]), cp("*"))
    mod(81, hp(option=1))
    mod(82, cp("*/NPCs"))
    mod(83, cp("*/Star-Map*"))
    mod(84, cp("*"))
    mod(85, hp("*/*/tslpatchdata"))
    mod(86, skip="GameFront refuses the download")
    mod(87, cp("*/*/To Override"), cp("*/*/Animated Monitors"))
    mod(88, cp("*/*/Override"))
    mod(89, hp(option=0), hp(option=1), cp("*/HQ Cockpit Skybox Textures/1024x1024 (M)"),
        odel(["ebo_yab.tga", "ebo_yaf.tga", "ebo_yal.tga", "ebo_yar.tga", "ebo_yat.tga"]))  # fmt: skip
    mod(90, cp("*", pattern="*.tpc"))
    mod(91, cp("*/No Overlays"))
    taris = "*/Taris_Reskin/Taris_TexturePack/Taris_Tex_Part1"
    mod(92, sdel(taris, ["LTS_Bsky01.tga", "LTS_Bsky02.tga", "LTS_sky0001.tga", "LTS_sky0002.tga", "LTS_sky0003.tga",
                         "LTS_sky0004.tga", "LTS_sky0005.tga"]),
        cp(taris), cp("*/Taris_Reskin/Taris_TexturePack/Taris_Tex_Part2"))  # fmt: skip
    mega("taris-reskin-patch", "Taris Reskin Patch.7z", cp("Taris Reskin Patch/Taris Reskin Patch"))
    mod(93, skip=KMRP)
    mod(94, sdel("HQSkyboxesII_K1/Override", ["m36aa_01_lm0.tga", "m36aa_01_lm1.tga", "m36aa_01_lm2.tga"]),
        cp("HQSkyboxesII_K1/Override"), cp("High quality skyboxes model fixes/*/override"))  # fmt: skip
    mod(95, cp("*/Main Installation/Override"), cp("*/Compatibility Patches/Leviathan - K1CP Forcefield"),
        cp("*/Compatibility Patches/High Quality Skyboxes by Kexikus"),
        cp("*/Compatibility Patches/Yavin Station Hangar by WildKarrde"))  # fmt: skip
    for n in (96, 97, 98, 99):
        mod(n, cp("*"))
    mod(100, cp("*/To Override"))
    mod(101, cp("*"))
    mod(102, cp("*"))
    mod(103, cp("*/*/to_Override"))
    mod(104, cp("*/Override"))
    mod(105, hp("*/*/tslpatchdata", option=0))
    mod(106, hp())
    mod(107, cp("*/Override"))
    mod(108, cp("*"))
    mod(109, hp())
    mod(110, cp("*"))
    mod(111, hp("*/*/tslpatchdata", option=1))
    mod(112, hp("*/*/tslpatchdata", option=0), cp("*/*/Optional - Upscaled Textures", recursive=True),
        hp("*/*/tslpatchdata", option=2))  # fmt: skip
    mod(113, hp("*/*/tslpatchdata"))
    mod(114, cp("*/*/For Override", recursive=True))
    mod(115, hp("*/TSLPatchdata"))
    mod(116, cpf("*/*", ["dan13_dorak.dlg"]))
    mod(117, cp("*/*/Installation", recursive=True))
    mod(118, skip="build marks it Steam Deck-incompatible")
    mod(119, cp("*/*"))
    mod(120, cp("*/Override"))
    mod(121, cp("*/*"))
    mod(122, hp("*/*/tslpatchdata"))
    mod(
        123,
        sdel("*", ["ii_trapkit_001.tga", "ii_trapkit_002.tga", "ii_trapkit_003.tga", "ii_trapkit_004.tga"]),
        cp("*"),
    )
    mod(124, cp("*"))
    mod(125, skip=KMRP)
    mod(126, hp("*/*/tslpatchdata"))
    mod(127, hp())
    mod(128, hp(option=1))
    mod(129, skip=KMRP)
    mod(130, hp())
    mod(131, hp("*/*/tslpatchdata"))
    mod(132, hp("*/*/tslpatchdata", option=1))
    mod(133, hp("*/*/Tslpatchdata"))
    mod(134, hp("*/English/tslpatchdata"))
    mod(135, cp("*/*"))
    mod(136, hp(option=0))
    mod(137, sdel("*/*/tslpatchdata", ["keblastore.utm"]), hp("*/*/tslpatchdata", allow_errors=2),
        Rename(old="w_ionrfl_04.mdl", new="w_ionrfl_004.mdl"), Rename(old="w_ionrfl_04.mdx", new="w_ionrfl_004.mdx"),
        odel(["w_rptnblstr_004.mdl", "w_rptnblstr_004.mdx", "w_blstrpstl_006.mdl", "w_blstrpstl_006.mdx",
              "g1_w_rptnblstr01.uti"]))  # fmt: skip
    mod(
        138,
        hp("*/*/tslpatchdata", option=0),
        hp("*/*/tslpatchdata", option=1),
        hp("*/*/tslpatchdata", option=2),
    )
    for n in (139, 140, 141, 142):
        mod(n, hp("*/*/tslpatchdata"))
    mod(143, skip=KMRP)
    mod(144, hp("*/*/tslpatchdata"))
    mod(145, hp())
    mega("sherruk-patch", "SAWL Patch.rar", cp("SAWL Patch/*/Override"))
    mod(146, hp("*/*/tslpatchdata"))
    mod(147, hp())
    mod(148, hp("*/*/tslpatchdata", option=0))
    mod(149, hp("*/*/tslpatchdata"))
    mod(150, cp(".", pattern="*.dlg"))
    mod(151, hp("*/*/tslpatchdata"))
    mod(152, hp("*/*/tslpatchdata", option=0))
    mod(153, hp("*/*/tslpatchdata"))
    mod(154, hp("*/*/tslpatchdata", option=1))
    mod(155, hp())
    mega(
        "czerka-ithorian-patch",
        "Czerka Business Attire - Dark Hope Ithorian Compatch.7z",
        cp("Czerka Business Attire*"),
    )
    mod(156, hp(option=0))
    mod(157, hp("*/*/tslpatchdata"))
    mod(158, hp("*/*/tslpatchdata", option=0))
    mod(159, hp())
    mod(160, hp("*/*/tslpatchdata", option=1))
    mod(161, skip=LINUX)
    mod(162, hp("*/*/tslpatchdata"))
    mod(163, hp("*/*/tslpatchdata"))
    mod(164, skip=KMRP)
    mod(165, hp("*/*/tslpatchdata", option=0))
    mod(166, hp(option=0))
    mod(167, hp("*/*/tslpatchdata", option=2))
    mod(168, hp("*/tslpatchdata", option=0))
    mod(169, hp(option=2))
    mod(170, repair("09-blaster-adjustment-orphan-rows", StageDir()), hp(option=1))
    mod(171, hp("*/*/tslpatchdata"))
    mod(172, cp("*/*/For Override", recursive=True))
    mod(173, hp())
    mod(174, hp("*/*/tslpatchdata"))
    mod(175, hp())
    mod(176, hp("*/*/tslpatchdata"))
    mod(177, hp())
    mod(178, hp("*/*/tslpatchdata"))
    mod(179, hp("*/*/Main Install/tslpatchdata", option=1))
    mod(180, hp(option=0))
    mod(181, DedupeTpc())
    mod(182, sdel("JC's Minor Fixes*/*/Aesthetic Improvements",
                  ["N_CommM02.tga", "N_CommM03.tga", "N_CommM04.tga", "N_CommM05.tga", "N_CommM06.tga", "N_CommM08.tga"]),
        cp("JC's Minor Fixes*/*/Aesthetic Improvements"), cp("JC's Minor Fixes*/*/Resolution Fixes"),
        cp("JC's Minor Fixes*/*/Straight Fixes"),
        sdel("KOTOR 1 Community Patch*/*", ["PLC_SSldCrps.tpc", "N_CommM01.tpc", "N_CommM02.tpc", "N_CommM03.tpc",
                                            "N_CommM04.tpc", "N_CommM05.tpc", "N_CommM06.tpc", "N_CommM08.tpc"]),
        cp("KOTOR 1 Community Patch*/*"),
        cp("Miscellaneous*/*/Sherruk with Lightsabers - Patch"),
        cp("Miscellaneous*/*/Thigh-High Boots for Twi'lek - Patch/NPC Replacement"),
        cp("Miscellaneous*/*/Thigh-High Boots for Twi'lek - Patch/NPC Replacement/Optional"))  # fmt: skip
    mod(
        183,
        cp("*/Override"),
        cp("*/Player Clothing", pattern="pfbbl*"),
        cp("*/Player Clothing", pattern="pmbbl*"),
    )
    mod(184, hp("*/*/tslpatchdata", option=3), hp("*/*/tslpatchdata", option=5))
    # 185: the build's cleanlist, applied for every listed mod that is installed here (Juhani Cathar Head is not)
    rows = [
        line.split(",")
        for line in (game_dir / "build" / "cleanlist_k1.txt").read_text().splitlines()
        if line.strip()
    ]
    dele = [f for row in rows if "Juhani Real Cathar Head" not in row[0] for f in row[1:]]
    mod(185, sdel("*/Copy contents to KotOR's Override folder", dele), cp("*/Copy contents to KotOR's Override folder"),
        DedupeTpc())  # fmt: skip
    mod(186, skip=REPL)
    # after the build: the repairs, then the rescaled cutscenes over the game's movies
    mod("repair:08-wounded-republic-detonate-controller",
        repair("08-wounded-republic-detonate-controller", OverrideDir(),
               ArchivePath(rel=f"{dirs[157]}/[K1]_Diversified_Wounded_Republic_Soldiers_On_Taris_v1.4.7z")))  # fmt: skip
    mod("cutscenes", cp("*/1920x1080", pattern="*.bik", dest="movies"), inputs=("cutscenes",))
    # KMRP's installer in a Wine container with what its Advanced Settings would hold, then the controller
    # module built from source (../kmrp-build/README.md) replacing the one it shipped. First the game's
    # settings file, which a never-launched tree lacks and the installer needs: the one Steam's install
    # produced, kept with the other original files.
    mod(
        "ini",
        cpf(".", ["swkotor.ini"], dest=".", if_absent=True),
        inputs=("original-steam-files/swkotor.ini",),
    )
    mod("kmrp", Kmrp(installer="KMRP-Windows-1.5.1.exe",
                     settings={"driverCompatibility": True, "markerFixes": True, "controllerSupport": True, "highFpsFix": True}))  # fmt: skip
    mod("kmrp-controller", Script(path="./kmrp-build/install-controller.py",
                                  args=(GameDir(), DataPath(rel="kmrp-build/kmrp-controller.dll"),
                                        DataPath(rel="kmrp-build/kmrp-controller.hooks.toml"))))  # fmt: skip
    return Recipe(tuple(entries))
