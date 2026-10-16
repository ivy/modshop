"""KMRP's controller module, built from a clone into the files the `kmrp-controller` entry installs.

The procedure and its reasons are games/kotor/kmrp-build/README.md. This runs it: the clone's
Linux build script, the checks that README names, KMRP's own packager, and the hand-over into
`data/kmrp-build/`, where the outputs of the build before are kept under `previous-<commit>/`
and `COMMIT` names the clone's commit. The build's Python packages come in as a uv overlay on
the project's environment, pinned here, so uv.lock (and with it every checkpoint key) is not
touched by them.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from modshop.core.errors import ModshopError, Preflight

UPSTREAM = "origin/master"
CONTAINER = "docker.io/mstorsjo/llvm-mingw:latest"
OVERLAY = ("pillow==12.3.0", "numpy==2.5.4", "fonttools==4.67.0", "capstone==5.0.7")
# The module links the CRT statically (/MT); anything else imported is a build that went wrong.
IMPORTS = frozenset({"KERNEL32.dll", "USER32.dll", "GDI32.dll", "bcrypt.dll"})
PACKAGE = "KOTOR 1 Native Controller Mod + Xbox HUD.kpatch"
OUTPUTS = (
    "kmrp-controller.dll",
    "kmrp-controller.map",
    "kmrp-controller.hooks.toml",
    "kmrp-controller.verification.json",
    PACKAGE,
)


class BuildError(ModshopError):
    pass


@dataclass(frozen=True, slots=True)
class Built:
    commit: str
    label: str
    hooks: int
    previous: Path | None  # where the outputs this replaced were moved


def git(clone: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=clone, capture_output=True, text=True, check=True
    ).stdout.strip()


def label(clone: Path) -> str:
    """`<upstream base>+linux<commits on top>`: what the module is, relative to what upstream ships."""
    base = git(clone, "merge-base", "HEAD", UPSTREAM)
    ahead = git(clone, "rev-list", "--count", f"{base}..HEAD")
    return f"{base[:7]}+linux{ahead}"


def hook_count(hooks_toml: str) -> int:
    return len(re.findall(r"^\[\[(?:patches\.)?hooks\]\]\s*$", hooks_toml, flags=re.MULTILINE))


def hand_over(staged: Path, out: Path, commit: str) -> Path | None:
    """Move the five outputs from staged/ into out/, the previous ones to previous-<commit>/."""
    out.mkdir(parents=True, exist_ok=True)
    record = out / "COMMIT"
    previous: Path | None = None
    old = record.read_text().strip() if record.exists() else ""
    if old and old != commit and all((out / name).exists() for name in OUTPUTS):
        previous = out / f"previous-{old[:7]}"
        if previous.exists():
            shutil.rmtree(previous)
        previous.mkdir()
        for name in OUTPUTS:
            (out / name).rename(previous / name)
    for name in OUTPUTS:
        shutil.copy2(staged / name, out / name)
    record.write_text(commit + "\n")
    return previous


def build(clone: Path, out: Path, repo: Path, xwin: Path) -> Built:
    if not (clone / "src" / "controller-native" / "build_controller_standalone_linux.sh").exists():
        raise Preflight(f"{clone} is not a KMRP clone with the Linux build patches applied")
    if git(clone, "status", "--porcelain", "--untracked-files=no"):
        raise Preflight(f"{clone} has uncommitted changes; COMMIT could not name what was built")
    if not (xwin / "crt").is_dir():
        raise Preflight(f"no xwin splat at {xwin}; kmrp-build/README.md has the command")
    uv = shutil.which("uv")
    if uv is None:
        raise Preflight("uv is not on PATH")
    commit = git(clone, "rev-parse", "HEAD")
    tag = label(clone)
    overlay = [uv, "run", "--project", str(repo), *(f"--with={p}" for p in OVERLAY), "--"]
    env = {**os.environ, "XWIN": str(xwin), "PYTHON": "python"}

    def run(*cmd: str) -> str:
        r = subprocess.run([*overlay, *cmd], cwd=clone, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise BuildError(f"{' '.join(cmd)} exited {r.returncode}:\n{(r.stdout + r.stderr)[-3000:]}")
        return r.stdout

    run("bash", "src/controller-native/build_controller_standalone_linux.sh")
    run("python", "tools/check_hook_stolen_bytes.py", "src/controller-native/kotor1.hooks.toml")
    built = clone / "build" / "controller-standalone"
    check_binary(built)

    with tempfile.TemporaryDirectory(prefix="kmrp-package-") as tmp:
        staged = Path(tmp)
        run(
            "python", "tools/build_controller_kpatch.py", "--module", str(built / "kmrp-controller.dll"),
            "--out", str(staged), "--version", tag, "--config-dir", str(staged / "config"),
        )  # fmt: skip
        shutil.move(staged / "config" / "kmrp-controller.hooks.toml", staged / "kmrp-controller.hooks.toml")
        for name in ("kmrp-controller.dll", "kmrp-controller.map"):
            shutil.copy2(built / name, staged / name)
        hooks = hook_count((staged / "kmrp-controller.hooks.toml").read_text())
        previous = hand_over(staged, out, commit)
    return Built(commit, tag, hooks, previous)


def readobj(built: Path, flag: str) -> str:
    r = subprocess.run(
        ["podman", "run", "--rm", "-v", f"{built}:/m:ro,z", CONTAINER, "llvm-readobj", flag, "/m/kmrp-controller.dll"],
        capture_output=True, text=True,
    )  # fmt: skip
    if r.returncode != 0:
        raise BuildError(f"llvm-readobj {flag} failed:\n{r.stderr}")
    return r.stdout


def check_binary(built: Path) -> None:
    """The two checks the README names: the imports are the four system DLLs, and every function
    the export list names is exported."""
    imports = set(
        re.findall(r"^\s*Name: (\S+\.dll)\s*$", readobj(built, "--coff-imports"), re.MULTILINE | re.I)
    )
    if not imports <= IMPORTS:
        raise BuildError(f"unexpected imports: {sorted(imports - IMPORTS)}")
    exported = set(re.findall(r"^\s*Name: (\S+)\s*$", readobj(built, "--coff-exports"), re.MULTILINE))
    wanted = {
        line.split()[0]
        for line in (built / "controller-exports.def").read_text().splitlines()[1:]
        if line.strip() and not line.strip().upper().startswith(("EXPORTS", "LIBRARY", ";"))
    }
    if missing := wanted - exported:
        raise BuildError(f"not exported: {sorted(missing)}")
