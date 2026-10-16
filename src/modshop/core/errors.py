"""The failures the tool expects. Anything else is a bug and shows its traceback."""

from __future__ import annotations

from pathlib import Path


class ModshopError(Exception):
    """Base of every expected failure; the command line prints the message and exits 1."""


class Preflight(ModshopError):
    """The data directory, the base, the patcher or the environment is not ready."""


class RecipeError(ModshopError):
    def __init__(self, entry: str, message: str) -> None:
        super().__init__(f"{entry}: {message}")
        self.entry = entry


class InputMissing(ModshopError):
    def __init__(self, entry: str, spec: str, looked_at: Path | str) -> None:
        super().__init__(f"{entry}: input {spec} ({looked_at}) does not exist")
        self.entry, self.spec = entry, spec


class StepFailed(ModshopError):
    def __init__(self, entry: str, index: int, step: str, cause: str, log: Path | None = None) -> None:
        where = f" (log: {log})" if log else ""
        super().__init__(f"{entry}: step {index} ({step}) failed: {cause}{where}")
        self.entry, self.index, self.step, self.log = entry, index, step, log


class NotReproducible(ModshopError):
    def __init__(self, entry: str, key: str, paths: tuple[str, ...]) -> None:
        super().__init__(f"{entry} ({key}): {len(paths)} paths differ between the two builds")
        self.entry, self.key, self.paths = entry, key, paths


class Locked(ModshopError):
    """Another build holds the lock."""
