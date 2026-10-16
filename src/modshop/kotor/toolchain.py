"""The tools a build runs with, and the two fingerprints they contribute to every key."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from modshop.core.config import Paths
from modshop.core.errors import Preflight
from modshop.core.extract import Extractor
from modshop.core.key import code_fingerprint, env_fingerprint, override_env_fingerprint
from modshop.kotor.patcher import HoloPatcherCli

CODE_ROOT = "modshop.kotor.runner"
PATCHER_ENV = "MODSHOP_PATCHER"


@dataclass(frozen=True, slots=True)
class Toolchain:
    patcher: HoloPatcherCli
    extractor: Extractor
    code: str
    env: str

    @classmethod
    def resolve(cls, paths: Paths) -> Toolchain:
        extractor = Extractor()
        sevenzip = extractor.version()
        if not sevenzip:
            raise Preflight("7zz (7-Zip) is not installed")
        override = os.environ.get(PATCHER_ENV)
        if override:
            exe = Path(override)
            env = override_env_fingerprint(package_dirs(exe), interpreter_version(exe), sevenzip)
        else:
            exe = Path(sys.executable).parent / "holopatcher"
            env = env_fingerprint(paths.repo / "uv.lock", sevenzip)
        if not exe.exists():
            raise Preflight(f"no patcher at {exe}; run `uv sync`")
        return cls(HoloPatcherCli(exe), extractor, code_fingerprint(CODE_ROOT), env)


def interpreter_version(patcher: Path) -> str:
    return subprocess.run(
        [str(patcher.parent / "python"), "-c", "import sys; print(sys.version)"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def package_dirs(patcher: Path) -> list[Path]:
    """Where that environment's interpreter finds pykotor and holopatcher."""
    code = "import pykotor, holopatcher; print(pykotor.__path__[0]); print(holopatcher.__path__[0])"
    out = subprocess.run(
        [str(patcher.parent / "python"), "-c", code], capture_output=True, text=True, check=True
    ).stdout
    return [Path(line) for line in out.splitlines() if line]
