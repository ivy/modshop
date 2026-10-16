"""The one mutable tree: a reflink copy of a checkpoint, with a record of which."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WorkTree:
    path: Path
    record: Path
