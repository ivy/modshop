"""Copies that share storage: reflink clones of files and trees, hardlinked trees.

The data directory must be on a filesystem with reflinks (XFS with reflink=1, btrfs). A Cloner
made with `reflink=False` copies bytes instead; the tests use it, since tmpfs has no reflinks,
and nothing else does.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from modshop.core.errors import Preflight


@dataclass(frozen=True, slots=True)
class Cloner:
    reflink: bool = True

    def copy_tree(self, src: Path, dst: Path) -> None:
        """dst becomes a copy of the directory src, attributes kept."""
        if self.reflink:
            subprocess.run(["cp", "-a", "--reflink=always", str(src), str(dst)], check=True)
        else:
            shutil.copytree(src, dst, symlinks=True)

    def copy_file(self, src: Path, dst: Path) -> None:
        if self.reflink:
            subprocess.run(["cp", "-a", "--reflink=always", str(src), str(dst)], check=True)
        else:
            shutil.copy2(src, dst, follow_symlinks=False)

    def hardlink_tree(self, src: Path, dst: Path) -> None:
        """dst becomes a tree of hardlinks to src's files (new directories, shared inodes)."""
        subprocess.run(["cp", "-al", str(src), str(dst)], check=True)

    def probe(self, directory: Path) -> None:
        """Raise Preflight unless `directory` is on a filesystem where reflinks work."""
        if not self.reflink:
            return
        scratch = directory / ".reflink-probe"
        try:
            if scratch.exists():
                shutil.rmtree(scratch)
            scratch.mkdir(parents=True)
            (scratch / "a").write_text("x")
            subprocess.run(
                ["cp", "--reflink=always", str(scratch / "a"), str(scratch / "b")],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise Preflight(f"{directory} is not on a reflink-capable filesystem") from e
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
