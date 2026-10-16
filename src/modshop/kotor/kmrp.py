"""KMRP's installer, run on the build host under Wine in a container, and made deterministic.

The container has no network and nothing mounted but the tree, the installer and a settings
file; the tree is mounted at the path it will have on the handheld, because the installer
records the executable's path for its Restore. Afterwards the two timestamps its state file
carries are fixed and the manifest row for that file recomputed, so the output depends on
nothing but the inputs.
"""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
from pathlib import Path

from modshop.core.config import Handheld
from modshop.core.hashing import sha256_file

STAMP = "2000-01-01T00:00:01"
CONTAINER = "modshop-kmrp"  # one fixed name, so a container a killed build left behind can be removed


def remove_stale_container() -> None:
    subprocess.run(["podman", "rm", "-f", "--ignore", CONTAINER], capture_output=True)


def install(
    *,
    game: Path,
    installer: Path,
    settings: dict[str, bool],
    image: str,
    handheld: Handheld,
    scratch: Path,
    timeout: int,
    log: logging.Logger,
) -> None:
    target = handheld.game_dir_absolute
    exe_win = "Z:" + target.replace("/", "\\") + "\\swkotor.exe"
    remove_stale_container()
    with tempfile.TemporaryDirectory(dir=scratch) as cfg:
        body = (
            "{\r\n"
            + ",\r\n".join(f'  "{k}": {"true" if v else "false"}' for k, v in settings.items())
            + "\r\n}\r\n"
        )
        (Path(cfg) / "settings.json").write_bytes(body.encode())
        cmd = [
            "podman", "run", "--rm", "--name", CONTAINER, "--network", "none", "--security-opt", "label=disable",
            "-v", f"{game}:{target}",
            "-v", f"{installer}:/in/{installer.name}:ro",
            "-v", f"{cfg}:/wine/drive_c/users/root/AppData/Local/KMRP",
            "-e", "WINEDEBUG=-all",
            image, "bash", "-c",
            f'xvfb-run -a wine "/in/{installer.name}" --in-place "{exe_win}" {handheld.display}; rc=$?; wineserver --wait; exit $rc',
        ]  # fmt: skip
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    for line in [x for x in (r.stdout + r.stderr).splitlines() if "X connection" not in x][-6:]:
        log.info("    %s", line[:200])
    if r.returncode != 0:
        raise RuntimeError(f"KMRP installer exited {r.returncode}")
    normalise_state(game)
    log.info("    KMRP installed at %s for %s", handheld.display, target)


def normalise_state(game: Path) -> None:
    state = game / "kpm_install_state.json"
    text = re.sub(r'"(CreatedAt|UpdatedAt)": "[^"]*"', rf'"\1": "{STAMP}"', state.read_text())
    state.write_text(text)
    digest = sha256_file(state).upper().encode()
    manifest = game / "KMRP_KPM.manifest"
    lines = manifest.read_bytes().split(b"\n")
    for i, line in enumerate(lines):
        if line.startswith(b"file\tkpm_install_state.json\t"):
            lines[i] = b"file\tkpm_install_state.json\t" + digest + (b"\r" if line.endswith(b"\r") else b"")
    manifest.write_bytes(b"\n".join(lines))
