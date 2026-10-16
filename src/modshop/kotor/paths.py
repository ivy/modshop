"""The game's path rules: lookup is case-insensitive, as the game's own file system was.

Mod archives name files loosely (`Override` and `override`, `tslpatchdata` and `TSLPatchdata`),
and under Wine two names differing only in case are one file. Every lookup here matches names
case-insensitively, the exact spelling first when both exist; `put` replaces any case-variant of
the file it writes; `collapse_case` keeps one file per case-insensitive name.
"""

from __future__ import annotations

import fnmatch
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

SKIP_SUFFIXES = (
    ".jpg", ".png", ".txt", ".rtf", ".pdf", ".md", ".ds_store", ".url", ".htm", ".html", ".docx", ".exe", ".bat", ".ini",
)  # fmt: skip
MACOSX = "__macosx"


def ci_find(directory: Path, name: str) -> Path | None:
    """The path of `name` inside `directory`, matched case-insensitively, the exact spelling first."""
    if not directory.is_dir():
        return None
    low = name.lower()
    hits = sorted(
        (p for p in directory.iterdir() if p.name.lower() == low), key=lambda p: (p.name != name, p.name)
    )
    return hits[0] if hits else None


def _resolve(cur: Path, parts: list[str]) -> list[Path]:
    if not parts:
        return [cur]
    if not cur.is_dir():
        return []
    part, rest = parts[0], parts[1:]
    if "*" in part:
        kids = sorted(
            p
            for p in cur.iterdir()
            if fnmatch.fnmatch(p.name.lower(), part.lower()) and MACOSX not in p.name.lower()
        )
    else:
        k = ci_find(cur, part)
        kids = [k] if k else []
    out: list[Path] = []
    for k in kids:
        out += _resolve(k, rest)
    return out


def ci_path(root: Path, rel: str) -> Path:
    """Resolve a slash path under root case-insensitively; a segment may hold `*` wildcards.
    Archives unpack as `<stem>/<their own folders>`, so if nothing matches, one or two extra
    wildcard levels are tried after the first segment before giving up. A path that does not
    exist is returned as given, since callers that create files rely on that."""
    parts = list(PurePosixPath(rel.replace("\\", "/")).parts)
    if not parts or parts == ["."]:
        return root
    for extra in (0, 1, 2):
        trial = [*parts[:1], *["*"] * extra, *parts[1:]] if parts[0] != "." else [*["*"] * extra, *parts[1:]]
        hits = _resolve(root, trial)
        if hits:
            return hits[0]
    return root.joinpath(*parts)


def files_in(root: Path, pattern: str = "*", recursive: bool = False) -> list[Path]:
    it = root.rglob("*") if recursive else root.iterdir()
    return sorted(
        p
        for p in it
        if p.is_file()
        and fnmatch.fnmatch(p.name.lower(), pattern.lower())
        and not p.name.lower().endswith(SKIP_SUFFIXES)
        and MACOSX not in str(p).lower()
    )


def subdirs(root: Path) -> list[Path]:
    return [d for d in root.iterdir() if d.is_dir() and MACOSX not in d.name.lower()]


def put(src: Path, dest_dir: Path) -> None:
    """Copy a file into dest_dir, replacing any case-variant of it."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    old = ci_find(dest_dir, src.name)
    if old and old.name != src.name:
        old.unlink()
    shutil.copy2(src, dest_dir / src.name)


def collapse_case(directory: Path) -> list[tuple[Path, list[Path]]]:
    """Keep one file per case-insensitive name, the most recently written; return what was kept
    and what went. HoloPatcher writes a file by the exact name its ini spells beside an existing one
    of another spelling, where Windows would overwrite."""
    groups: dict[str, list[Path]] = {}
    for p in directory.iterdir():
        if p.is_file():
            groups.setdefault(p.name.lower(), []).append(p)
    out: list[tuple[Path, list[Path]]] = []
    for ps in groups.values():
        if len(ps) > 1:
            ps.sort(key=lambda p: p.stat().st_ctime_ns, reverse=True)
            for p in ps[1:]:
                p.unlink()
            out.append((ps[0], ps[1:]))
    return out


@dataclass(frozen=True, slots=True)
class GameTree:
    """A game folder with the rules above."""

    root: Path

    @property
    def override(self) -> Path:
        return self.root / "Override"

    @property
    def modules(self) -> Path:
        return self.root / "modules"

    def dest(self, sub: str | None) -> Path:
        return self.root / sub if sub else self.override

    def find(self, name: str, directory: Path | None = None) -> Path | None:
        return ci_find(directory or self.override, name)
