import logging
import zipfile
from pathlib import Path

import pytest

from modshop.core.config import Paths
from modshop.core.errors import StepFailed
from modshop.core.stage import Stage
from modshop.kotor import nwnnsscomp
from modshop.kotor.context import StepContext
from modshop.kotor.paths import GameTree
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
    Setting,
    StageCopyAs,
    StageDelete,
    StageDir,
    Symlink,
    Tlk,
    Word,
)
from tests.conftest import FakePatcher


def ctx_for(tmp_path: Path, patcher: FakePatcher | None = None) -> StepContext:
    game = tmp_path / "game"
    (game / "Override").mkdir(parents=True)
    (game / "modules").mkdir()
    (game / "Override" / "keep.tga").write_bytes(b"k")
    stage = tmp_path / "stage"
    (stage / "Mod" / "Override").mkdir(parents=True)
    (stage / "Mod" / "Override" / "new.tga").write_bytes(b"n")
    (stage / "Mod" / "Override" / "readme.txt").write_bytes(b"r")
    (stage / "Mod" / "tslpatchdata").mkdir()
    (stage / "Mod" / "dialog.tlk").write_bytes(b"new tlk")
    paths = Paths(tmp_path / "data", tmp_path / "repo" / "games" / "kotor")
    paths.archives.mkdir(parents=True)
    paths.game_dir.mkdir(parents=True)
    return StepContext(
        game=GameTree(game), stage=Stage(stage), paths=paths, handheld=None, patcher=patcher or FakePatcher(),
        log=logging.getLogger("test"), entry="e", index=0,
    )  # fmt: skip


def test_copy_descends_wrapper_and_skips_docs(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    Copy(src="*/Override").apply(ctx)
    assert sorted(p.name for p in ctx.game.override.iterdir()) == ["keep.tga", "new.tga"]
    (ctx.stage.path / "Wrap" / "Inner").mkdir(parents=True)
    (ctx.stage.path / "Wrap" / "Inner" / "deep.tga").write_bytes(b"d")
    Copy(src="Wrap").apply(ctx)  # Wrap/ holds nothing but Inner/: the wrapper descent finds the files
    assert (ctx.game.override / "deep.tga").exists()
    with pytest.raises(RuntimeError, match="copied nothing"):
        Copy(src="*", pattern="*.mdl").apply(ctx)


def test_copy_files_if_absent_and_dest(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    CopyFiles(src="Mod", names=("dialog.tlk",), dest=".", if_absent=True).apply(ctx)
    assert (ctx.game.root / "dialog.tlk").read_bytes() == b"new tlk"
    (ctx.game.root / "dialog.tlk").write_bytes(b"mine")
    CopyFiles(src="Mod", names=("dialog.tlk",), dest=".", if_absent=True).apply(ctx)
    assert (ctx.game.root / "dialog.tlk").read_bytes() == b"mine"


def test_delete_rename_tlk_symlink(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    Delete(names=("KEEP.TGA", "absent.tga")).apply(ctx)
    assert not list(ctx.game.override.iterdir())
    Copy(src="Mod/Override").apply(ctx)
    Rename(old="NEW.tga", new="renamed.tga").apply(ctx)
    assert [p.name for p in ctx.game.override.iterdir()] == ["renamed.tga"]
    Tlk(src="Mod/dialog.tlk").apply(ctx)
    assert (ctx.game.root / "dialog.tlk").read_bytes() == b"new tlk"
    Symlink(link="Modules", target="modules").apply(ctx)
    Symlink(link="Modules", target="modules").apply(ctx)  # idempotent
    assert (ctx.game.root / "Modules").readlink().name == "modules"
    with pytest.raises(FileExistsError):
        Symlink(link="Override", target="modules").apply(ctx)


def test_stage_delete_and_copy_as(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    StageCopyAs(src="Mod/Override/new.tga", new="twin.tga").apply(ctx)
    StageDelete(src="Mod/Override", names=("new.tga", "missing")).apply(ctx)
    assert sorted(p.name for p in (ctx.stage.path / "Mod" / "Override").iterdir()) == [
        "readme.txt",
        "twin.tga",
    ]


def test_dedupe_tpc(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    (ctx.game.override / "a.tpc").write_bytes(b"")
    (ctx.game.override / "A.tga").write_bytes(b"")
    (ctx.game.override / "b.tpc").write_bytes(b"")
    DedupeTpc().apply(ctx)
    assert sorted(p.name for p in ctx.game.override.iterdir()) == ["A.tga", "b.tpc", "keep.tga"]


def test_holopatcher_step_collapses_case_and_checks_errors(tmp_path: Path) -> None:
    patcher = FakePatcher(writes={"Override/KEEP.tga": b"patched"})
    ctx = ctx_for(tmp_path, patcher)
    HoloPatcher(src="Mod/tslpatchdata", option=2).apply(ctx)
    assert patcher.calls == [(ctx.game.root, ctx.stage.path / "Mod" / "tslpatchdata", 2)]
    assert [p.name for p in ctx.game.override.iterdir()] == ["KEEP.tga"]  # newest spelling wins
    assert (ctx.paths.logs / "holopatcher" / "e-00.log").exists()
    patcher.errors = 2
    with pytest.raises(StepFailed, match="2 errors"):
        HoloPatcher(src="Mod/tslpatchdata").apply(ctx)
    HoloPatcher(src="Mod/tslpatchdata", allow_errors=2).apply(ctx)


def test_holopatcher_compile_runs_the_nws_shim_and_fails_on_pykotors_compiler(tmp_path: Path) -> None:
    patcher = FakePatcher(compiled=("a.nss",))
    ctx = ctx_for(tmp_path, patcher)
    with pytest.raises(StepFailed, match=r"compiled a\.nss without compile=True"):
        HoloPatcher(src="Mod/tslpatchdata").apply(ctx)
    assert patcher.launchers == [None]
    step = HoloPatcher(src="Mod/tslpatchdata", compile=True)
    step.apply(ctx)
    launcher = patcher.launchers[-1]
    assert launcher == [str(ctx.paths.data / "tools/nws/nwnnsscomp")]
    assert nwnnsscomp.SHIM in step.inputs()
    patcher.builtin = (
        "[Note] Patching from a unix operating system, compiling 'a.nss' using the built-in compilers...",
    )
    with pytest.raises(StepFailed, match="pykotor's compiler built"):
        step.apply(ctx)


def test_nwnnsscomp_supply_takes_tslpatchers_compiler_from_another_archive(tmp_path: Path) -> None:
    td = tmp_path / "tslpatchdata"
    td.mkdir()
    archive = tmp_path / "other.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("tslpatchdata/nwnnsscomp.exe", b"not tslpatcher's")
        z.writestr("tslpatchdata/nwscript.nss", b"// nwscript")
    with pytest.raises(ValueError, match="is not TSLPatcher's"):
        nwnnsscomp.supply(td, archive)
    assert not nwnnsscomp.supply(td, archive)  # it has one now: nothing to supply


def test_script_args_render_and_declare_inputs(tmp_path: Path) -> None:
    ctx = ctx_for(tmp_path)
    (ctx.paths.game_dir / "repairs" / "r").mkdir(parents=True)
    script = ctx.paths.game_dir / "repairs" / "r" / "make.py"
    script.write_text(
        "import sys, pathlib; pathlib.Path(sys.argv[1], 'Override', 'made').write_text(' '.join(sys.argv[2:]))"
    )
    step = Script(
        path="./repairs/r/make.py",
        args=(
            GameDir(),
            OverrideDir(),
            StageDir(),
            ArchivePath(rel="157-x/a.7z"),
            DataPath(rel="k/b.dll"),
            Word(text="w"),
        ),
        reads=("./repairs/r",),
    )
    assert step.inputs() == ("./repairs/r/make.py", "./repairs/r", "157-x/a.7z", "data/k/b.dll")
    step.apply(ctx)
    made = (ctx.game.override / "made").read_text().split()
    assert made == [
        str(ctx.game.override),
        str(ctx.stage.path),
        str(ctx.paths.archives / "157-x/a.7z"),
        str(ctx.paths.data / "k/b.dll"),
        "w",
    ]
    script.write_text("import sys; sys.exit(3)")
    with pytest.raises(RuntimeError, match="exited 3"):
        step.apply(ctx)


def test_script_arg_kinds_never_dump_alike() -> None:
    dumps = {
        type(a).__name__: a.model_dump(mode="json")
        for a in (GameDir(), OverrideDir(), StageDir(), Word(text="x"))
    }
    assert len({str(d) for d in dumps.values()}) == len(dumps)


def test_kmrp_declares_its_inputs_and_needs_local() -> None:
    k = Kmrp(installer="KMRP.exe", settings={"a": True})
    assert k.inputs() == (
        "KMRP.exe",
        "./kmrp-build/wine/Containerfile",
        "image:modshop-wine",
        "local:handheld.home",
        "local:handheld.game_dir",
        "local:handheld.display",
    )


def test_setting_renders_local_value_or_default(tmp_path: Path) -> None:
    from dataclasses import replace

    from modshop.core.config import Local

    ctx = ctx_for(tmp_path)
    arg = Setting(key="kmrp.debug_logs", default="0")
    assert arg.spec == "local?:kmrp.debug_logs"
    assert arg.render(ctx) == "0"
    handheld = {"ssh": "h", "home": "/h", "game_dir": "~/g", "display": "1x1"}
    without = Local.model_validate({"handheld": handheld})
    assert arg.render(replace(ctx, local=without)) == "0"
    with_level = Local.model_validate({"handheld": handheld, "kmrp": {"debug_logs": 2}})
    assert arg.render(replace(ctx, local=with_level)) == "2"
