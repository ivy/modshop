"""One build at a time."""

from __future__ import annotations

import fcntl
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from modshop.core.errors import Locked


@contextmanager
def held(path: Path) -> Generator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            raise Locked(f"another build holds {path}") from e
        yield
