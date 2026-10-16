"""Checkpoints and the store that holds them.

A checkpoint is an immutable tree with its manifest, change set and metadata, named by key,
under <ckpt>/<key>/{tree,manifest.txt,changed.txt,meta.json}. The vanilla game is the
checkpoint with key `vanilla` and no parent, under its own directory. Nothing ever writes inside
a checkpoint's tree: the work tree is a reflink copy, so its writes land on new inodes, which is
what makes the hardlinks between checkpoints safe.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from modshop.core.clone import Cloner
from modshop.core.key import VANILLA, Key
from modshop.core.recipe import Entry
from modshop.core.tree import Manifest, TreeHash, normalise_mtimes
from modshop.core.worktree import WorkTree

FIXED_MTIME_NS = 946684801 * 10**9  # 2000-01-01T00:00:01Z: every file in a checkpoint carries it


@dataclass(frozen=True, slots=True)
class Checkpoint:
    key: Key
    parent: Key | None
    mod: str
    tree: TreeHash
    files: int
    built_at: str
    changed: int | None = None
    seconds: float | None = None

    @classmethod
    def from_json(cls, text: str) -> Checkpoint:
        d = json.loads(text)
        return cls(
            key=Key(d["key"]),
            parent=Key(d["parent"]) if d.get("parent") else None,
            mod=d["mod"],
            tree=TreeHash(d["tree"]),
            files=int(d["files"]),
            built_at=d["built_at"],
            changed=d.get("changed"),
            seconds=d.get("seconds"),
        )

    def to_json(self) -> str:
        d = {k: v for k, v in asdict(self).items() if v is not None or k == "parent"}
        return json.dumps(d, indent=1) + "\n"


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


class Store:
    def __init__(self, ckpt: Path, vanilla: Path, cloner: Cloner, mtime_ns: int = FIXED_MTIME_NS) -> None:
        self.ckpt, self.vanilla, self.cloner, self.mtime_ns = ckpt, vanilla, cloner, mtime_ns

    def dir(self, key: Key) -> Path:
        return self.vanilla if key == VANILLA else self.ckpt / key

    def tree(self, key: Key) -> Path:
        return self.dir(key) / "tree"

    def manifest_path(self, key: Key) -> Path:
        return self.dir(key) / "manifest.txt"

    def get(self, key: Key) -> Checkpoint | None:
        meta = self.dir(key) / "meta.json"
        return Checkpoint.from_json(meta.read_text()) if meta.exists() else None

    def manifest(self, key: Key) -> Manifest:
        return Manifest.read(self.manifest_path(key))

    def stored_keys(self) -> list[Key]:
        if not self.ckpt.exists():
            return []
        return sorted(Key(d.name) for d in self.ckpt.iterdir() if d.is_dir() and (d / "meta.json").exists())

    def lineage(self, key: Key) -> list[Checkpoint]:
        """The checkpoint, its parent, and so on down to vanilla; oldest first."""
        out: list[Checkpoint] = []
        cur: Key | None = key
        while cur is not None:
            c = self.get(cur)
            if c is None:
                raise KeyError(f"checkpoint {cur} is missing from {self.ckpt}")
            out.append(c)
            cur = c.parent
        return list(reversed(out))

    def remove(self, key: Key) -> None:
        if key == VANILLA:
            raise ValueError("the vanilla checkpoint is not removable")
        shutil.rmtree(self.ckpt / key)

    def clear_partial(self) -> None:
        """Remove any `<key>.tmp` left by a commit that did not finish."""
        if self.ckpt.exists():
            for t in self.ckpt.glob("*.tmp"):
                shutil.rmtree(t)

    def index_vanilla(self) -> Checkpoint:
        """Normalise the vanilla tree's mtimes and write its manifest and meta.json."""
        tree = self.tree(VANILLA)
        normalise_mtimes(tree, self.mtime_ns)
        m = Manifest.of_tree(tree)
        h = m.write(self.manifest_path(VANILLA))
        c = Checkpoint(VANILLA, None, "vanilla", h, len(m), timestamp())
        (self.vanilla / "meta.json").write_text(c.to_json())
        return c

    def commit(self, work: WorkTree, key: Key, parent: Key, entry: Entry, since_ns: int) -> Checkpoint:
        """The finished work tree becomes checkpoint `key`: mtimes normalised, manifest written, the
        tree built in `<key>.tmp` and renamed into place; the work tree's record then names the key.

        The tree hardlinks the parent checkpoint's files and holds reflink clones of only the paths
        the entry changed. A reflink clone of a whole tree per checkpoint adds an extent-ownership
        record for every file to XFS's per-allocation-group reserved metadata, and a few hundred
        such clones exhausted it here with ENOSPC while `df` showed terabytes free."""
        t0 = time.time()
        normalise_mtimes(work.path, self.mtime_ns)
        prior = self.manifest(parent)
        m = Manifest.of_tree(work.path, prior=prior, since_ns=since_ns)
        changes = prior.diff(m)
        tmp = self.ckpt / f"{key}.tmp"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        tree_hash = m.write(tmp / "manifest.txt")
        (tmp / "changed.txt").write_text(changes.text())
        self.cloner.hardlink_tree(self.tree(parent), tmp / "tree")
        for rel in changes.paths():
            dst = tmp / "tree" / rel
            if dst.is_symlink() or dst.exists():
                dst.unlink()
            if rel in m:
                dst.parent.mkdir(parents=True, exist_ok=True)
                src = work.path / rel
                if src.is_symlink():
                    dst.symlink_to(src.readlink())
                else:
                    self.cloner.copy_file(src, dst)
        self._prune_empty_dirs(tmp / "tree", work.path)
        c = Checkpoint(
            key,
            parent,
            entry.name,
            tree_hash,
            len(m),
            timestamp(),
            changed=len(changes.paths()),
            seconds=round(time.time() - t0, 1),
        )
        (tmp / "meta.json").write_text(c.to_json())
        os.sync()
        tmp.rename(self.ckpt / key)
        work.set_key(key)
        return c

    @staticmethod
    def _prune_empty_dirs(tree: Path, like: Path) -> None:
        """Directories the entry emptied in the work tree go away in the checkpoint too."""
        dirs = sorted(
            (d for d in tree.rglob("*") if d.is_dir() and not d.is_symlink()), key=lambda d: -len(str(d))
        )
        for d in dirs:
            if not any(d.iterdir()) and not (like / d.relative_to(tree)).exists():
                d.rmdir()
