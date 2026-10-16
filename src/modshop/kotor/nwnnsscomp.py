"""TSLPatcher's nwnnsscomp.exe, run under Wine in a container: the compiler a mod's author
expects for its [CompileList], where HoloPatcher would otherwise use pykotor's own.

HoloPatcher runs `<launcher> <nwnnsscomp.exe> -c <source> -o <output>` with host paths; this
file is that launcher. It mounts the folders those paths are in at the same paths, with no
network, and hands Wine the `Z:` spelling of each, since nwnnsscomp is a Windows program.
Standard library only: HoloPatcher runs it with `python -I`, outside this package.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

LAUNCHER_ENV = "PYKOTOR_NWNNSSCOMP_LAUNCHER"
TIMEOUT_ENV = "PYKOTOR_NWNNSSCOMP_TIMEOUT"
TIMEOUT = 120  # a container and a Wine start take about 4 s; pykotor's default is 5
CONTAINER = "modshop-nwnnsscomp"  # one fixed name, so one a killed build left behind can be removed

# pykotor's KnownExternalCompilers.TSLPATCHER: tk102's v0.03b, the one TSLPatcher mods ship
TSLPATCHER_SHA256 = "539eb689d2e0d3751aeed273385865278bef6696c46bc0cab116b40c3b2fe820"


def launcher(image: str) -> list[str]:
    return [sys.executable, "-I", __file__, image]


def supply(tslpatchdata: Path, archive: Path) -> bool:
    """Put TSLPatcher's nwnnsscomp.exe and the nwscript.nss beside it into a tslpatchdata that
    has none, from another mod's archive; False when it already has one."""
    if any(p.name.lower() == "nwnnsscomp.exe" for p in tslpatchdata.iterdir()):
        return False
    with zipfile.ZipFile(archive) as z:
        members = [n for n in z.namelist() if not n.startswith("__MACOSX/")]
        for want in ("nwnnsscomp.exe", "nwscript.nss"):
            name = next((n for n in members if PurePosixPath(n).name.lower() == want), None)
            if name is None:
                raise FileNotFoundError(f"{archive.name} holds no {want}")
            (tslpatchdata / want).write_bytes(z.read(name))
    got = hashlib.sha256((tslpatchdata / "nwnnsscomp.exe").read_bytes()).hexdigest()
    if got != TSLPATCHER_SHA256:
        raise ValueError(f"{archive.name}'s nwnnsscomp.exe is not TSLPatcher's (sha256 {got})")
    return True


def windows(path: str) -> str:
    return "Z:" + path.replace("/", "\\")


def main(argv: list[str]) -> int:
    image, exe, *args = argv
    paths = [a for a in args if a.startswith("/")]
    dirs = sorted({str(Path(p).parent) for p in [exe, *paths]})
    subprocess.run(["podman", "rm", "-f", "--ignore", CONTAINER], capture_output=True)
    cmd = [
        "podman",
        "run",
        "--rm",
        "--name",
        CONTAINER,
        "--network",
        "none",
        "--security-opt",
        "label=disable",
    ]
    for d in dirs:
        cmd += ["-v", f"{d}:{d}"]
    wine_args = " ".join(f"'{windows(a) if a.startswith('/') else a}'" for a in [exe, *args])
    cmd += [
        "-e",
        "WINEDEBUG=-all",
        image,
        "bash",
        "-c",
        f"wine {wine_args}; rc=$?; wineserver --wait; exit $rc",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    noise = ("XDG_RUNTIME_DIR", "X connection")
    sys.stdout.write("".join(line + "\n" for line in r.stdout.splitlines() if not line.startswith(noise)))
    sys.stderr.write(
        "".join(line + "\n" for line in r.stderr.splitlines() if not any(n in line for n in noise))
    )
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
