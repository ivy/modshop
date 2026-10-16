"""An entry's inputs, extracted to a scratch folder for the duration of its steps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Stage:
    path: Path
