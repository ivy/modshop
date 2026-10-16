"""The handheld as a deploy target."""

from __future__ import annotations

from modshop.core.config import Handheld
from modshop.core.deploy import SshTransport, Target, Transport

# The player's saves (the depot ships an empty lower-case `saves/` beside the game's `Saves/`);
# the logs the game and KMRP write; swkotor.ini, which the build produces but the game rewrites
# as it is played ([Movies Shown], settings), so it is sent only to a handheld that has none;
# and K1DriverCompat.ini, the settings template KMRP's driver-compatibility patch writes at
# launch when the folder has none.
EXCLUDE = ("/Saves/", "/saves/", "*.log", "/swkotor.ini", "/K1DriverCompat.ini")
FIRST_TIME = ("swkotor.ini",)
PROCESS = "swkotor.exe"


def handheld_target(handheld: Handheld, transport: Transport | None = None) -> Target:
    return Target(transport or SshTransport(handheld.ssh), handheld.game_dir, EXCLUDE, FIRST_TIME, PROCESS)
