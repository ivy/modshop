"""Trees and their manifests.

A manifest lists every path under a tree: files by digest and size, symlinks by target, sorted
by the path's bytes. Its canonical text is one line per path, `F <digest> <size> <path>` or
`L <target> <path>`, and the SHA-256 of that text is the tree hash: two trees with the same
content have the same hash whatever their timestamps, inodes or location.
"""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import NewType

from modshop.core.hashing import sha256_file, sha256_text

TreeHash = NewType("TreeHash", str)


@dataclass(frozen=True, slots=True)
class File:
    digest: str
    size: int


@dataclass(frozen=True, slots=True)
class Symlink:
    target: str


Row = File | Symlink


@dataclass(frozen=True, slots=True)
class ChangeSet:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]

    def __bool__(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def paths(self) -> tuple[str, ...]:
        return tuple(sorted(self.added + self.removed + self.changed, key=str.encode))

    def text(self) -> str:
        """One line per path: `+` added, `-` removed, `~` changed."""
        marks = {
            **dict.fromkeys(self.added, "+"),
            **dict.fromkeys(self.removed, "-"),
            **dict.fromkeys(self.changed, "~"),
        }
        return "".join(f"{marks[p]} {p}\n" for p in self.paths())


def walk(root: Path) -> list[Path]:
    """Every file and symlink under root, sorted by relative path bytes; a symlinked directory
    is listed as the link it is, not descended."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        for n in list(dirnames):
            if (d / n).is_symlink():
                dirnames.remove(n)
                filenames.append(n)
        dirnames.sort()
        out.extend(d / n for n in filenames)
    return sorted(out, key=lambda p: str(p.relative_to(root)).encode())


class Manifest(Mapping[str, Row]):
    def __init__(self, rows: Mapping[str, Row]) -> None:
        self._rows: dict[str, Row] = dict(sorted(rows.items(), key=lambda kv: kv[0].encode()))

    def __getitem__(self, key: str) -> Row:
        return self._rows[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Manifest) and self._rows == other._rows

    def __hash__(self) -> int:
        return hash(self.tree_hash)

    @classmethod
    def of_tree(cls, root: Path, *, prior: Manifest | None = None, since_ns: int | None = None) -> Manifest:
        """Hash every path under root. With `prior` (the manifest of the tree this one was copied
        from) and `since_ns` (a clock reading taken after that copy), a file whose inode has not
        changed since (ctime older than since_ns, same size, same path in prior) keeps the prior
        digest: the kernel sets ctime on every write and no user can set it back."""
        rows: dict[str, Row] = {}
        for p in walk(root):
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                rows[rel] = Symlink(str(p.readlink()))
                continue
            st = p.stat()
            old = prior.get(rel) if prior is not None else None
            if (
                isinstance(old, File)
                and since_ns is not None
                and old.size == st.st_size
                and st.st_ctime_ns < since_ns
            ):
                rows[rel] = old
            else:
                rows[rel] = File(sha256_file(p), st.st_size)
        return cls(rows)

    @classmethod
    def read(cls, path: Path) -> Manifest:
        rows: dict[str, Row] = {}
        with path.open(encoding="utf-8") as f:
            for line in f:
                kind, rest = line.rstrip("\n").split(" ", 1)
                if kind == "F":
                    digest, size, rel = rest.split(" ", 2)
                    rows[rel] = File(digest, int(size))
                elif kind == "L":
                    target, rel = rest.split(" ", 1)
                    rows[rel] = Symlink(target)
                else:
                    raise ValueError(f"{path}: unknown manifest row kind {kind!r}")
        return cls(rows)

    def text(self) -> str:
        lines: list[str] = []
        for rel, row in self._rows.items():
            if isinstance(row, File):
                lines.append(f"F {row.digest} {row.size} {rel}\n")
            else:
                lines.append(f"L {row.target} {rel}\n")
        return "".join(lines)

    def write(self, path: Path) -> TreeHash:
        text = self.text()
        path.write_text(text, encoding="utf-8")
        return TreeHash(sha256_text(text))

    @property
    def tree_hash(self) -> TreeHash:
        return TreeHash(sha256_text(self.text()))

    def diff(self, other: Manifest) -> ChangeSet:
        """What `other` has that this one does not: paths added, removed and changed in other."""
        added = tuple(sorted((p for p in other if p not in self), key=str.encode))
        removed = tuple(sorted((p for p in self if p not in other), key=str.encode))
        changed = tuple(sorted((p for p in other if p in self and self[p] != other[p]), key=str.encode))
        return ChangeSet(added, removed, changed)


def normalise_mtimes(root: Path, mtime_ns: int) -> int:
    """Give every file under root the one fixed mtime, so no comparison that looks at
    timestamps (rsync's, a human's) depends on an archive's clock. Returns how many changed."""
    n = 0
    for p in walk(root):
        if p.is_symlink():
            continue
        if p.stat().st_mtime_ns != mtime_ns:
            os.utime(p, ns=(mtime_ns, mtime_ns))
            n += 1
    return n
