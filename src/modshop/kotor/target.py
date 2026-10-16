"""The handheld as a deploy target."""

from __future__ import annotations

from modshop.core.config import Handheld
from modshop.core.deploy import ManagedIni, SshTransport, Target, Transport

# The player's saves (the depot ships an empty lower-case `saves/` beside the game's `Saves/`);
# the logs the game and KMRP write; swkotor.ini, which the game rewrites as it is played
# ([Movies Shown], [Keymapping], the options menu), so it is managed rather than synced; and
# K1DriverCompat.ini, the settings template KMRP's driver-compatibility patch writes at launch
# when the folder has none.
EXCLUDE = ("/Saves/", "/saves/", "*.log", "/swkotor.ini", "/K1DriverCompat.ini")
# The display keys the build decides: the panel's size (KMRP's installer writes it from local.toml),
# fullscreen as Steam's install has it, and KMRP's high-refresh permission. RefreshRate is left to
# the handheld: the build's file says 60 and the handheld's has said 120.
MANAGED = (
    ManagedIni(
        "swkotor.ini",
        (
            ("Graphics Options", "Width"),
            ("Graphics Options", "Height"),
            ("Graphics Options", "FullScreen"),
            ("Graphics Options", "AllowHighMonitorFrequency"),
        ),
    ),
)
PROCESS = "swkotor.exe"


def handheld_target(handheld: Handheld, transport: Transport | None = None) -> Target:
    return Target(transport or SshTransport(handheld.ssh), handheld.game_dir, EXCLUDE, PROCESS, MANAGED)
