"""Putting a tree on the target by content, into a copy that is swapped in by rename.

The target's live folder is snapshotted to `<game_dir>.next`; rsync writes into that copy
comparing checksums, not timestamps, so a rebuilt file with identical content moves nothing;
then a dry run must find nothing left to do, the old folder becomes `<game_dir>.prev` (the
rollback) and the copy becomes live. The target's exclusions are the one list of paths the
deploy never touches and the drift check never reports.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import Protocol

from modshop.core.errors import ModshopError


class DeployError(ModshopError):
    pass


class Transport(Protocol):
    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]: ...

    def rsync_dest(self, path: str) -> str: ...

    def snapshot(self, src: str, dst: str) -> None:
        """dst becomes a copy of the directory src on the target (a reflink copy where possible)."""
        ...


@dataclass(frozen=True, slots=True)
class SshTransport:
    host: str

    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]:
        return subprocess.run(["ssh", self.host, cmd], check=check, text=True, capture_output=True)

    def rsync_dest(self, path: str) -> str:
        return f"{self.host}:{path}"

    def snapshot(self, src: str, dst: str) -> None:
        self.run(f"rm -rf {shlex.quote(dst)} && cp -a --reflink=always {shlex.quote(src)} {shlex.quote(dst)}")


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


@dataclass(frozen=True, slots=True)
class Target:
    transport: Transport
    game_dir: str  # as the target's shell expands it (`~` allowed)
    exclude: tuple[str, ...]  # rsync exclude patterns: never written, never reported
    first_time: tuple[str, ...]  # sent only when the target has none
    process: str  # the game's process name; a deploy refuses while it runs


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
        cmd = [
            "rsync",
            "--recursive",
            "--links",
            "--perms",
            "--times",
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

    def drift(self, tree: Path) -> Drift:
        """What differs between the tree and the live folder, by path; the exclusions aside."""
        return Drift(tuple(self._rsync(tree, self.live_dir(), dry=True)))

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
        for name in self.target.first_time:
            if (
                self.target.transport.run(f"test -e {shlex.quote(f'{live}/{name}')}", check=False).returncode
                != 0
            ):
                subprocess.run(
                    ["rsync", "--times", str(tree / name), self.target.transport.rsync_dest(f"{nxt}/{name}")],
                    check=True,
                )
        left = self._rsync(tree, nxt, dry=True)
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
