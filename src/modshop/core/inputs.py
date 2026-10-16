"""What an entry reads, named by a spec string, and how each kind is hashed and staged.

Spec forms:
  `<name>`           a folder or a file under data/archives (`170-jc-s-blaster-adjustment`, `mega/X.zip`)
  `./<path>`         a file or folder in the game's directory in the repository
  `data/<path>`      a file or folder under the data root
  `local:<dotted>`   a value from local.toml; key material only, nothing staged
  `local?:<dotted>`  the same for a value local.toml may leave out (its absence is key material too)
  `image:<name>`     a podman image's id; key material only
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from modshop.core.config import Local, Paths
from modshop.core.errors import InputMissing
from modshop.core.hashing import sha256_file, sha256_text
from modshop.core.tree import walk


@dataclass(frozen=True, slots=True)
class InputRow:
    spec: str
    rel: str  # path inside the input, or "" for a value
    digest: str


class HashCache:
    """sha256 of archive files, keyed by path relative to the archives root, size and mtime.
    The archives are immutable downloads and tens of gigabytes; `verify --inputs` rehashes them
    all and reports any entry that lies. This is the one place the pipeline trusts a timestamp."""

    def __init__(self, path: Path, archives: Path) -> None:
        self.path, self.archives = path, archives
        self._rows: dict[str, str] = json.loads(path.read_text()) if path.exists() else {}
        self.lies: list[Path] = []

    def _key(self, p: Path) -> str:
        st = p.stat()
        rel = p.relative_to(self.archives).as_posix() if p.is_relative_to(self.archives) else str(p)
        return f"{rel}|{st.st_size}|{st.st_mtime_ns}"

    def digest(self, p: Path, *, full: bool = False) -> str:
        k = self._key(p)
        if full or k not in self._rows:
            d = sha256_file(p)
            if full and k in self._rows and self._rows[k] != d:
                self.lies.append(p)
            self._rows[k] = d
        return self._rows[k]

    def save(self) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._rows))
        tmp.replace(self.path)


class Input(Protocol):
    @property
    def spec(self) -> str: ...

    def rows(self, cache: HashCache, *, full: bool = False) -> list[InputRow]: ...

    def staged(self) -> list[Path]:
        """Paths to put in the stage: the children of an archive folder, or the path itself.
        Empty for a value."""
        ...


@dataclass(frozen=True, slots=True)
class PathInput:
    spec_: str
    path: Path
    entry: str
    unpack_children: bool  # an archive folder stages its children; a repo or data path is one item

    @property
    def spec(self) -> str:
        return self.spec_

    def rows(self, cache: HashCache, *, full: bool = False) -> list[InputRow]:
        if not self.path.exists():
            raise InputMissing(self.entry, self.spec, self.path)
        files = walk(self.path) if self.path.is_dir() else [self.path]
        out: list[InputRow] = []
        for p in files:
            if p.is_symlink() or "__pycache__" in p.parts:
                continue  # bytecode caches appear when a script is imported; they are not the script
            rel = p.relative_to(self.path).as_posix() if self.path.is_dir() else p.name
            out.append(InputRow(self.spec, rel, cache.digest(p, full=full)))
        return out

    def staged(self) -> list[Path]:
        if not self.path.exists():
            raise InputMissing(self.entry, self.spec, self.path)
        if self.unpack_children and self.path.is_dir():
            return sorted(self.path.iterdir())
        return [self.path]


@dataclass(frozen=True, slots=True)
class ValueInput:
    spec_: str
    value: str

    @property
    def spec(self) -> str:
        return self.spec_

    def rows(self, cache: HashCache, *, full: bool = False) -> list[InputRow]:
        return [InputRow(self.spec, "", sha256_text(self.value))]

    def staged(self) -> list[Path]:
        return []


def image_id(name: str) -> str:
    r = subprocess.run(
        ["podman", "image", "inspect", "--format", "{{.Id}}", name], capture_output=True, text=True
    )
    if r.returncode != 0:
        raise FileNotFoundError(f"podman image {name} is not built")
    return r.stdout.strip()


class InputResolver:
    """Turns spec strings into Inputs. local.toml is read on the first `local:` spec."""

    def __init__(self, paths: Paths, local: Local | None = None) -> None:
        self.paths = paths
        self._local = local

    def local(self) -> Local:
        if self._local is None:
            self._local = Local.load(self.paths.local_toml)
        return self._local

    def resolve(self, spec: str, entry: str) -> Input:
        if spec.startswith("local:"):
            return ValueInput(spec, json.dumps(self.local().value(spec[6:])))
        if spec.startswith("local?:"):
            present = self._local is not None or self.paths.local_toml.exists()
            return ValueInput(spec, json.dumps(self.local().get(spec[7:]) if present else None))
        if spec.startswith("image:"):
            return ValueInput(spec, image_id(spec[6:]))
        if spec.startswith("./"):
            return PathInput(spec, (self.paths.game_dir / spec[2:]).resolve(), entry, unpack_children=False)
        if spec.startswith("data/"):
            return PathInput(spec, self.paths.data / spec[5:], entry, unpack_children=False)
        return PathInput(spec, self.paths.archives / spec, entry, unpack_children=True)
