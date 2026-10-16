"""Entries and the steps they are made of, as the chain sees them.

The chain keys an entry, which needs each step's kind, inputs and canonical form, and hands the
entry to a `Runner` the game supplies; nothing here runs a step.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from modshop.core.stage import Stage
    from modshop.core.worktree import WorkTree


class Step(Protocol):
    @property
    def do(self) -> str: ...

    def inputs(self) -> tuple[str, ...]: ...

    def canonical(self) -> dict[str, object]: ...


@dataclass(frozen=True, slots=True)
class Entry:
    name: str
    inputs: tuple[str, ...]
    steps: tuple[Step, ...] = ()
    skip: str | None = None

    def all_inputs(self) -> tuple[str, ...]:
        """The entry's own inputs and every step's, in order, each once."""
        seen: dict[str, None] = dict.fromkeys(self.inputs)
        for step in self.steps:
            seen.update(dict.fromkeys(step.inputs()))
        return tuple(seen)


type Runner = Callable[[Entry, WorkTree, Stage], None]


@dataclass(frozen=True, slots=True)
class Recipe:
    entries: tuple[Entry, ...]

    def active(self) -> tuple[Entry, ...]:
        return tuple(e for e in self.entries if not e.skip)

    def get(self, name: str) -> Entry:
        for e in self.entries:
            if e.name == name:
                return e
        raise KeyError(name)
