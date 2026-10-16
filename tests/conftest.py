"""Fixtures: a synthetic game, archives made as zips, a fake patcher, and the plain-copy cloner."""

from __future__ import annotations

import logging
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from modshop.core.checkpoint import Store
from modshop.core.clone import Cloner
from modshop.core.config import Paths
from modshop.core.extract import Extractor
from modshop.core.inputs import HashCache, InputResolver
from modshop.core.key import Keyer
from modshop.core.stage import stage_factory
from modshop.core.worktree import WorkTree
from modshop.kotor.patcher import PatchReport


@dataclass
class FakePatcher:
    """Writes the files it is told to and reports what it is told to report."""

    writes: dict[str, bytes] = field(default_factory=lambda: {"Override/patched.2da": b"patched"})
    errors: int = 0
    calls: list[tuple[Path, Path, int | None]] = field(default_factory=list[tuple[Path, Path, int | None]])

    def install(
        self, game: Path, tslpatchdata: Path, *, option: int | None, log_to: Path, timeout: int
    ) -> PatchReport:
        self.calls.append((game, tslpatchdata, option))
        for rel, data in self.writes.items():
            p = game / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        log_to.parent.mkdir(parents=True, exist_ok=True)
        log_to.write_text(f"fake run on {tslpatchdata}\nInstall completed: {self.errors} errors\n")
        return PatchReport(self.errors, log_to, (f"Install completed: {self.errors} errors",))


@dataclass
class Synthetic:
    paths: Paths
    store: Store
    work: WorkTree
    cloner: Cloner
    resolver: InputResolver
    cache: HashCache
    patcher: FakePatcher
    log: logging.Logger

    def keyer(self, code: str = "code", env: str = "env") -> Keyer:
        return Keyer(self.resolver, self.cache, code, env)

    def stages(self):
        return stage_factory(self.paths.stage, self.resolver, Extractor())

    def archive(self, folder: str, name: str, files: dict[str, bytes]) -> Path:
        """A zip under data/archives/<folder>/<name> holding `files`."""
        d = self.paths.archives / folder
        d.mkdir(parents=True, exist_ok=True)
        z = d / name
        with zipfile.ZipFile(z, "w") as zf:
            for rel, data in files.items():
                zf.writestr(rel, data)
        return z


@pytest.fixture
def synthetic(tmp_path: Path) -> Synthetic:
    repo = tmp_path / "repo"
    game_dir = repo / "games" / "kotor"
    (game_dir / "build").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("")
    paths = Paths(tmp_path / "data", game_dir)
    vanilla_tree = paths.vanilla / "tree"
    (vanilla_tree / "Override").mkdir(parents=True)
    (vanilla_tree / "modules").mkdir()
    (vanilla_tree / "movies").mkdir()
    (vanilla_tree / "Override" / "base.tga").write_bytes(b"base")
    (vanilla_tree / "Override" / "old.tpc").write_bytes(b"tpc")
    (vanilla_tree / "Override" / "Old.tga").write_bytes(b"tga")
    (vanilla_tree / "modules" / "tar_m03ad.mod").write_bytes(b"module")
    (vanilla_tree / "dialog.tlk").write_bytes(b"vanilla tlk")
    (vanilla_tree / "swkotor.exe").write_bytes(b"exe")
    for d in (paths.archives, paths.stage, paths.logs, paths.ckpt, paths.tags):
        d.mkdir(parents=True, exist_ok=True)
    cloner = Cloner(reflink=False)
    store = Store(paths.ckpt, paths.vanilla, cloner)
    store.index_vanilla()
    work = WorkTree(paths.work, paths.work_record)
    resolver = InputResolver(paths)
    cache = HashCache(paths.hashcache, paths.archives)
    return Synthetic(paths, store, work, cloner, resolver, cache, FakePatcher(), logging.getLogger("modshop"))
