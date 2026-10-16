"""What a step is given."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from modshop.core.config import Handheld, Paths
from modshop.core.stage import Stage
from modshop.kotor.patcher import Patcher
from modshop.kotor.paths import GameTree


@dataclass(frozen=True, slots=True)
class StepContext:
    game: GameTree
    stage: Stage
    paths: Paths
    handheld: Handheld | None  # the three local.toml values the KMRP step needs; None when the file is absent
    patcher: Patcher
    log: logging.Logger
    entry: str
    index: int
    timeout: int = 1800

    @property
    def label(self) -> str:
        """`<entry>-<step index>`, for log file names."""
        return f"{self.entry}-{self.index:02d}"
