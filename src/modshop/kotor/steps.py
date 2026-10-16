"""The step kinds, one frozen model each, and the typed arguments a script can take.

Path specs follow `modshop.core.inputs`: `./x` is under the game's directory in the repository,
`data/x` under the data root, anything else under the archives.
"""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from modshop.core.errors import Preflight, StepFailed
from modshop.kotor import kmrp
from modshop.kotor.context import StepContext
from modshop.kotor.paths import ci_find, ci_path, collapse_case, files_in, put, subdirs


class StepModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    def inputs(self) -> tuple[str, ...]:
        return ()

    def canonical(self) -> dict[str, object]:
        return self.model_dump(mode="json")

    def apply(self, ctx: StepContext) -> None:
        raise NotImplementedError


# ---- script arguments ----------------------------------------------------------------------------


class GameDir(BaseModel, frozen=True):
    kind: Literal["game"] = "game"
    spec: None = None

    def render(self, ctx: StepContext) -> str:
        return str(ctx.game.root)


class OverrideDir(BaseModel, frozen=True):
    kind: Literal["override"] = "override"
    spec: None = None

    def render(self, ctx: StepContext) -> str:
        return str(ctx.game.override)


class StageDir(BaseModel, frozen=True):
    kind: Literal["stage"] = "stage"
    spec: None = None

    def render(self, ctx: StepContext) -> str:
        return str(ctx.stage.path)


class ArchivePath(BaseModel, frozen=True):
    """A file or folder under the archives; its spec is the path itself, so it is key material."""

    kind: Literal["archive"] = "archive"
    rel: str

    @property
    def spec(self) -> str:
        return self.rel

    def render(self, ctx: StepContext) -> str:
        return str(ctx.paths.archives / self.rel)


class DataPath(BaseModel, frozen=True):
    kind: Literal["data"] = "data"
    rel: str

    @property
    def spec(self) -> str:
        return f"data/{self.rel}"

    def render(self, ctx: StepContext) -> str:
        return str(ctx.paths.data / self.rel)


class Word(BaseModel, frozen=True):
    kind: Literal["word"] = "word"
    text: str
    spec: None = None

    def render(self, ctx: StepContext) -> str:
        return self.text


class Setting(BaseModel, frozen=True):
    """A value from local.toml by dotted key, `default` where the file leaves it out. The value
    is key material, so changing it rebuilds the entry."""

    kind: Literal["setting"] = "setting"
    key: str
    default: str

    @property
    def spec(self) -> str:
        return f"local?:{self.key}"

    def render(self, ctx: StepContext) -> str:
        value = ctx.setting(self.key)
        return self.default if value is None else str(value)


ScriptArg = GameDir | OverrideDir | StageDir | ArchivePath | DataPath | Word | Setting


def input_path(ctx: StepContext, spec: str) -> Path:
    if spec.startswith("./"):
        return ctx.paths.game_dir / spec[2:]
    if spec.startswith("data/"):
        return ctx.paths.data / spec[5:]
    return ctx.paths.archives / spec


# ---- the kinds -----------------------------------------------------------------------------------


class Copy(StepModel):
    """Files from a staged folder into Override (or `dest` under the game folder)."""

    do: Literal["copy"] = "copy"
    src: str = "."
    pattern: str = "*"
    exclude: tuple[str, ...] = ()
    recursive: bool = False
    dest: str | None = None

    def apply(self, ctx: StepContext) -> None:
        root = ci_path(ctx.stage.path, self.src)
        if not root.exists():
            raise FileNotFoundError(f"copy: {root}")
        # a wrapper folder holding nothing but one folder is not the mod's content yet
        while not self.recursive and not files_in(root, self.pattern) and len(subdirs(root)) == 1:
            root = subdirs(root)[0]
        excluded = [e.lower() for e in self.exclude]
        n = 0
        for f in files_in(root, self.pattern, self.recursive):
            if any(fnmatch.fnmatch(f.name.lower(), e) for e in excluded):
                continue
            put(f, ctx.game.dest(self.dest))
            n += 1
        ctx.log.info("   copied %d from %s", n, root.relative_to(ctx.stage.path.parent))
        if n == 0:
            raise RuntimeError("copied nothing")


class CopyFiles(StepModel):
    """Named files from the stage into Override (or `dest`); with `if_absent`, only the ones the
    tree does not already have."""

    do: Literal["copy_files"] = "copy_files"
    src: str
    names: tuple[str, ...]
    dest: str | None = None
    if_absent: bool = False

    def apply(self, ctx: StepContext) -> None:
        n = 0
        for name in self.names:
            d = ctx.game.dest(self.dest)
            if self.if_absent and ci_find(d, name):
                continue
            put(ci_path(ctx.stage.path, f"{self.src}/{name}"), d)
            n += 1
        ctx.log.info("   copied %d named files from %s", n, self.src)


class Delete(StepModel):
    """Files out of Override; a missing one is reported, not fatal."""

    do: Literal["delete"] = "delete"
    names: tuple[str, ...]

    def apply(self, ctx: StepContext) -> None:
        for n in self.names:
            p = ci_find(ctx.game.override, n)
            if p:
                p.unlink()
                ctx.log.info("   deleted %s", n)
            else:
                ctx.log.info("   (absent) %s", n)


class Rename(StepModel):
    do: Literal["rename"] = "rename"
    old: str
    new: str

    def apply(self, ctx: StepContext) -> None:
        p = ci_find(ctx.game.override, self.old)
        if not p:
            raise FileNotFoundError(self.old)
        q = ci_find(ctx.game.override, self.new)
        if q:
            q.unlink()
        p.rename(ctx.game.override / self.new)
        ctx.log.info("   renamed %s -> %s", self.old, self.new)


class StageDelete(StepModel):
    """Files removed from the stage before a later step reads it."""

    do: Literal["stage_delete"] = "stage_delete"
    src: str
    names: tuple[str, ...]

    def apply(self, ctx: StepContext) -> None:
        for n in self.names:
            p = ci_path(ctx.stage.path, f"{self.src}/{n}")
            if p.exists():
                p.unlink()


class StageCopyAs(StepModel):
    do: Literal["stage_copy_as"] = "stage_copy_as"
    src: str
    new: str

    def apply(self, ctx: StepContext) -> None:
        p = ci_path(ctx.stage.path, self.src)
        shutil.copy2(p, p.parent / self.new)


class Tlk(StepModel):
    do: Literal["tlk"] = "tlk"
    src: str

    def apply(self, ctx: StepContext) -> None:
        shutil.copy2(ci_path(ctx.stage.path, self.src), ctx.game.root / "dialog.tlk")
        ctx.log.info("   dialog.tlk <- %s", self.src)


class Symlink(StepModel):
    """A name in the game folder pointing at another: `Modules` for the patcher, which opens
    module paths by exact name, and `override` for mods whose installer spells the folder in
    lower case."""

    do: Literal["symlink"] = "symlink"
    link: str
    target: str

    def apply(self, ctx: StepContext) -> None:
        p = ctx.game.root / self.link
        if p.is_symlink() and str(p.readlink()) == self.target:
            return
        if p.exists() or p.is_symlink():
            raise FileExistsError(p)
        p.symlink_to(self.target)
        ctx.log.info("   %s -> %s", self.link, self.target)


class Script(StepModel):
    """One of our scripts, run with the tool's interpreter in isolated mode. `reads` names
    further inputs the script depends on (a repair's whole folder, README included)."""

    do: Literal["script"] = "script"
    path: str
    args: tuple[ScriptArg, ...] = ()
    reads: tuple[str, ...] = ()

    def inputs(self) -> tuple[str, ...]:
        return (self.path, *self.reads, *(a.spec for a in self.args if a.spec))

    def apply(self, ctx: StepContext) -> None:
        script = input_path(ctx, self.path)
        argv = [sys.executable, "-I", str(script), *(a.render(ctx) for a in self.args)]
        r = subprocess.run(argv, capture_output=True, text=True, timeout=ctx.timeout)
        for line in (r.stdout + r.stderr).splitlines()[-6:]:
            ctx.log.info("    %s", line[:200])
        if r.returncode != 0:
            raise RuntimeError(f"{script.name} exited {r.returncode}")


class Kmrp(StepModel):
    """KMRP's Windows installer, in place on the working tree, under Wine in a container."""

    do: Literal["kmrp"] = "kmrp"
    installer: str
    settings: dict[str, bool]
    image: str = "modshop-wine"

    def inputs(self) -> tuple[str, ...]:
        return (
            self.installer,
            "./kmrp-build/wine/Containerfile",
            f"image:{self.image}",
            "local:handheld.home",
            "local:handheld.game_dir",
            "local:handheld.display",
        )

    def apply(self, ctx: StepContext) -> None:
        if ctx.handheld is None:
            raise Preflight("the kmrp step needs local.toml's [handheld] table")
        kmrp.install(
            game=ctx.game.root,
            installer=ctx.paths.archives / self.installer,
            settings=self.settings,
            image=self.image,
            handheld=ctx.handheld,
            scratch=ctx.stage.path,
            timeout=ctx.timeout,
            log=ctx.log,
        )


class HoloPatcher(StepModel):
    """HoloPatcher on a staged tslpatchdata (or its parent); `option` is the namespace index."""

    do: Literal["holopatcher"] = "holopatcher"
    src: str = "*/tslpatchdata"
    option: int | None = None
    allow_errors: int = 0

    def apply(self, ctx: StepContext) -> None:
        td = ci_path(ctx.stage.path, self.src)
        log_to = ctx.paths.logs / "holopatcher" / f"{ctx.label}.log"
        report = ctx.patcher.install(
            ctx.game.root, td, option=self.option, log_to=log_to, timeout=ctx.timeout
        )
        for line in report.tail:
            ctx.log.info("   %s", line[:200])
        if report.errors is None or report.errors > self.allow_errors:
            raise StepFailed(ctx.entry, ctx.index, self.do, f"{report.errors} errors on {td}", log_to)
        for kept, gone in collapse_case(ctx.game.override):
            ctx.log.info("   case collapse: kept %s, removed %s", kept.name, ", ".join(p.name for p in gone))


class DedupeTpc(StepModel):
    """Every Override .tpc that has a same-named .tga or .dds goes; the game crashes when both exist."""

    do: Literal["dedupe_tpc"] = "dedupe_tpc"

    def apply(self, ctx: StepContext) -> None:
        names = {p.name.lower(): p for p in ctx.game.override.iterdir()}
        n = 0
        for low, p in list(names.items()):
            if low.endswith(".tpc") and (low[:-4] + ".tga" in names or low[:-4] + ".dds" in names):
                p.unlink()
                n += 1
        ctx.log.info("   removed %d duplicate tpc files", n)


KINDS: tuple[type[StepModel], ...] = (
    Copy, CopyFiles, Delete, Rename, StageDelete, StageCopyAs, Tlk, Symlink, Script, Kmrp, HoloPatcher, DedupeTpc,
)  # fmt: skip
