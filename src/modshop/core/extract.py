"""Putting an input into a stage: archives unpacked with 7-Zip, loose files and folders copied."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

ARCHIVE_SUFFIXES = (".zip", ".rar", ".7z")


@dataclass(frozen=True, slots=True)
class Extractor:
    sevenzip: str = "7zz"

    def place(self, item: Path, into: Path) -> None:
        """An archive unpacks into `<into>/<stem>/`; a file is copied; a folder is copied whole."""
        if item.is_file() and item.suffix.lower() in ARCHIVE_SUFFIXES:
            sub = into / item.stem
            sub.mkdir(exist_ok=True)
            r = subprocess.run(
                [self.sevenzip, "x", "-y", "-bd", "-bso0", f"-o{sub}", str(item)],
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"{self.sevenzip} failed on {item}: {r.stderr[-500:]}")
            fix_backslash_names(sub)
        elif item.is_file():
            shutil.copy2(item, into / item.name)
        elif item.is_dir():
            shutil.copytree(item, into / item.name, symlinks=True)
        else:
            raise FileNotFoundError(item)

    def version(self) -> str:
        """7-Zip's version line, for the environment fingerprint."""
        out = subprocess.run([self.sevenzip], capture_output=True, text=True).stdout.splitlines()
        return out[1] if len(out) > 1 else out[0] if out else ""


def fix_backslash_names(root: Path) -> None:
    """Windows zips with backslash paths unpack as single files named `a\\b\\c`; make them folders."""
    for f in list(root.iterdir()):
        if "\\" in f.name:
            t = root / f.name.replace("\\", "/")
            t.parent.mkdir(parents=True, exist_ok=True)
            f.rename(t)
