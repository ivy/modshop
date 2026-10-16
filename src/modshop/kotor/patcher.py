"""The patcher as a step sees it: HoloPatcher's command line, run as a subprocess."""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from modshop.kotor.paths import ci_find

log = logging.getLogger("modshop")


@dataclass(frozen=True, slots=True)
class PatchReport:
    errors: int | None  # None when the run never reported completing
    log: Path
    tail: tuple[str, ...]  # the lines worth showing: errors, warnings, the completion line


class Patcher(Protocol):
    def install(
        self, game: Path, tslpatchdata: Path, *, option: int | None, log_to: Path, timeout: int
    ) -> PatchReport: ...


def case_aliases(tslpatchdata: Path, modules: Path) -> list[tuple[Path, Path]]:
    """pykotor opens module files by exact name: for every `modules\\<name>` a mod's ini files
    mention whose case differs from the file on disk, link that spelling to the real file."""
    created: list[tuple[Path, Path]] = []
    for ini in sorted(tslpatchdata.rglob("*.ini")):
        text = ini.read_text(encoding="utf-8", errors="replace")
        names = set(re.findall(r"(?i)modules\\([^\\\r\n;=]+?\.(?:mod|rim|erf))\s*$", text, re.M))
        for name in sorted(n.strip() for n in names):
            real = ci_find(modules, name)
            if real and real.name != name and not (modules / name).exists():
                (modules / name).symlink_to(real.name)
                created.append((modules / name, real))
                log.info("   alias %s -> %s", name, real.name)
    return created


def drop_aliases(created: list[tuple[Path, Path]]) -> None:
    for link, real in created:
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            # the patcher replaced the link with a real file: keep it under the canonical name
            link.replace(real)
            log.info("   alias %s became the file; moved to %s", link.name, real.name)


@dataclass(frozen=True, slots=True)
class HoloPatcherCli:
    executable: Path

    def install(
        self, game: Path, tslpatchdata: Path, *, option: int | None, log_to: Path, timeout: int
    ) -> PatchReport:
        cmd = [
            str(self.executable),
            "--game-dir",
            str(game),
            "--tslpatchdata",
            str(tslpatchdata),
            "--install",
            "--console",
        ]
        if option is not None:
            cmd += ["--namespace-option-index", str(option)]
        aliases = case_aliases(tslpatchdata, game / "modules")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        finally:
            drop_aliases(aliases)
        log_to.parent.mkdir(parents=True, exist_ok=True)
        log_to.write_text(r.stdout + "\n--- stderr ---\n" + r.stderr)
        tail = [
            line
            for line in r.stdout.splitlines()
            if line.startswith("[Error]") or line.startswith("[Warning]") or "Install completed" in line
        ]
        done = [m for m in (re.search(r"Install completed: (\d+) errors", line) for line in tail) if m]
        errors = int(done[-1].group(1)) if done else None
        return PatchReport(errors, log_to, tuple(tail[-6:]))
