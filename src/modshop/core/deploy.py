"""Putting a tree on the target by content, into a copy that is swapped in by rename.

The target's live folder is snapshotted to `<game_dir>.next`; rsync writes into that copy
comparing checksums and never timestamps, so a rebuilt file with identical content moves nothing
and a file the game rewrote with the same bytes is not drift;
then a dry run must find nothing left to do, the old folder becomes `<game_dir>.prev` (the
rollback) and the copy becomes live. The target's exclusions are the one list of paths the
deploy never touches and the drift check never reports, with one refinement: a managed settings
file is excluded as a whole, because the game rewrites it as it is played, but the keys the target
names in it are set to the tree's values on deploy and reported when they differ.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import Protocol

from modshop.core import ini
from modshop.core.errors import ModshopError


class DeployError(ModshopError):
    pass


class Transport(Protocol):
    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]: ...

    def rsync_dest(self, path: str) -> str: ...

    def snapshot(self, src: str, dst: str) -> None:
        """dst becomes a copy of the directory src on the target (a reflink copy where possible)."""
        ...

    def read(self, path: str) -> bytes | None:
        """The file's bytes, or None when it is absent."""
        ...

    def write(self, path: str, data: bytes) -> None: ...


@dataclass(frozen=True, slots=True)
class SshTransport:
    host: str

    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]:
        return subprocess.run(["ssh", self.host, cmd], check=check, text=True, capture_output=True)

    def rsync_dest(self, path: str) -> str:
        return f"{self.host}:{path}"

    def snapshot(self, src: str, dst: str) -> None:
        self.run(f"rm -rf {shlex.quote(dst)} && cp -a --reflink=always {shlex.quote(src)} {shlex.quote(dst)}")

    def read(self, path: str) -> bytes | None:
        q = shlex.quote(path)
        r = subprocess.run(["ssh", self.host, f"test -e {q} || exit 3; cat {q}"], capture_output=True)
        if r.returncode == 3:
            return None
        if r.returncode != 0:
            raise DeployError(f"reading {path} failed:\n{r.stderr.decode(errors='replace')}")
        return r.stdout

    def write(self, path: str, data: bytes) -> None:
        subprocess.run(
            ["ssh", self.host, f"cat > {shlex.quote(path)}"], input=data, check=True, capture_output=True
        )


@dataclass(frozen=True, slots=True)
class LocalTransport:
    """The target is a directory on this machine; the tests use it."""

    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]:
        return subprocess.run(["sh", "-c", cmd], check=check, text=True, capture_output=True)

    def rsync_dest(self, path: str) -> str:
        return path

    def snapshot(self, src: str, dst: str) -> None:
        if Path(dst).exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, symlinks=True)

    def read(self, path: str) -> bytes | None:
        p = Path(path)
        return p.read_bytes() if p.exists() else None

    def write(self, path: str, data: bytes) -> None:
        Path(path).write_bytes(data)


@dataclass(frozen=True, slots=True)
class ManagedIni:
    """A settings file the game rewrites, in which the build owns some keys."""

    path: str  # relative to the game folder; it must also be excluded from the sync
    keys: tuple[tuple[str, str], ...]  # (section, key) pairs set to the tree's values


@dataclass(frozen=True, slots=True)
class Target:
    transport: Transport
    game_dir: str  # as the target's shell expands it (`~` allowed)
    exclude: tuple[str, ...]  # rsync exclude patterns: never written, never reported
    process: str  # the game's process name; a deploy refuses while it runs
    managed: tuple[ManagedIni, ...] = ()


@dataclass(frozen=True, slots=True)
class Drift:
    lines: tuple[str, ...]  # rsync's itemized lines, directories left out

    def __bool__(self) -> bool:
        return bool(self.lines)


@dataclass(frozen=True, slots=True)
class DeployResult:
    updated: int
    previous: str | None  # the rollback folder, when a swap happened


class Deployer:
    def __init__(self, target: Target) -> None:
        self.target = target

    def live_dir(self) -> str:
        return self.target.transport.run(f"echo {self.target.game_dir}").stdout.strip()

    def game_running(self) -> bool:
        return (
            self.target.transport.run(f"pgrep -x {shlex.quote(self.target.process)}", check=False).returncode
            == 0
        )

    def _rsync(self, src: Path, dest: str, *, dry: bool) -> list[str]:
        # content only: --checksum decides what moves, and without --times a file or symlink that
        # differs only in its timestamp is neither drift nor something to send
        cmd = [
            "rsync",
            "--recursive",
            "--links",
            "--perms",
            "--checksum",
            "--delete",
            "--itemize-changes",
        ]
        if dry:
            cmd.append("--dry-run")
        for e in self.target.exclude:
            cmd += ["--exclude", e]
        cmd += [f"{src}/", f"{self.target.transport.rsync_dest(dest)}/"]
        r = subprocess.run(cmd, text=True, capture_output=True)
        if r.returncode != 0:
            raise DeployError(f"rsync failed:\n{r.stderr}")
        return [line for line in r.stdout.splitlines() if line and not line.startswith(".d")]

    def _managed_drift(self, tree: Path, folder: str) -> list[str]:
        lines: list[str] = []
        for m in self.target.managed:
            have = self.target.transport.read(f"{folder}/{m.path}")
            if have is None:
                lines.append(f"*missing {m.path}")
                continue
            want = (tree / m.path).read_bytes()
            for section, key in m.keys:
                value = ini.get(want, section, key)
                if value is not None and ini.get(have, section, key) != value:
                    lines.append(
                        f"~setting {m.path} [{section}] {key}={ini.get(have, section, key)} (build: {value})"
                    )
        return lines

    def _set_managed(self, tree: Path, folder: str) -> None:
        for m in self.target.managed:
            path = f"{folder}/{m.path}"
            have = self.target.transport.read(path)
            want = (tree / m.path).read_bytes()
            if have is None:
                self.target.transport.write(path, want)
                continue
            new = have
            for section, key in m.keys:
                value = ini.get(want, section, key)
                if value is not None:
                    new = ini.put(new, section, key, value)
            if new != have:
                self.target.transport.write(path, new)

    def drift(self, tree: Path) -> Drift:
        """What differs between the tree and the live folder, by path, and the managed keys that differ."""
        live = self.live_dir()
        return Drift(tuple(self._rsync(tree, live, dry=True) + self._managed_drift(tree, live)))

    def deploy(self, tree: Path) -> DeployResult:
        if self.game_running():
            raise DeployError(f"{self.target.process} is running on the target")
        live = self.live_dir()
        drift = self.drift(tree)
        if not drift:
            return DeployResult(0, None)
        nxt = f"{live}.next"
        self.target.transport.snapshot(live, nxt)
        self._rsync(tree, nxt, dry=False)
        self._set_managed(tree, nxt)
        left = self._rsync(tree, nxt, dry=True) + self._managed_drift(tree, nxt)
        if left:
            raise DeployError(
                f"{len(left)} paths still differ after the sync; {nxt} is left for inspection, the live folder untouched:\n"
                + "\n".join(left)
            )
        q = shlex.quote
        self.target.transport.run(
            f"rm -rf {q(live + '.prev')} && mv {q(live)} {q(live + '.prev')} && mv {q(nxt)} {q(live)}"
        )
        return DeployResult(len(drift.lines), f"{live}.prev")
