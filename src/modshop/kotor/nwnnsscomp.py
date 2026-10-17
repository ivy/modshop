"""The compiler for a mod's [CompileList]: nws's nwnnsscomp shim, built from a pinned commit of
github.com/ivy/nwscript by `mise run nws:build`, where HoloPatcher would otherwise use pykotor's
own compiler.

HoloPatcher runs `<launcher> <nwnnsscomp.exe> -c <source> -o <output>`; the shim is the launcher,
skips the .exe it is handed, and compiles in nws's nwnnsscomp-compatible mode. pykotor uses a
launcher only when the tslpatchdata holds an nwnnsscomp.exe, so `supply` puts TSLPatcher's there
for a mod that ships none, with the nwscript.nss beside it.
"""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path, PurePosixPath

LAUNCHER_ENV = "PYKOTOR_NWNNSSCOMP_LAUNCHER"
TIMEOUT_ENV = "PYKOTOR_NWNNSSCOMP_TIMEOUT"
TIMEOUT = 120  # pykotor's default of 5 s is tight for a cold start

# pykotor's KnownExternalCompilers.TSLPATCHER: tk102's v0.03b, the one TSLPatcher mods ship
TSLPATCHER_SHA256 = "539eb689d2e0d3751aeed273385865278bef6696c46bc0cab116b40c3b2fe820"


SHIM = "data/tools/nws/nwnnsscomp"  # the spec of the shim as a step input; `mise run nws:build` makes it


def launcher(data: Path) -> list[str]:
    return [str(data / SHIM.removeprefix("data/"))]


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
