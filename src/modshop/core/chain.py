"""The recipe resolved against a store, and the builder that fills in what is missing.

A build walks the entries in order, keys each against its parent, and does nothing for an entry
whose checkpoint exists; the first missing one is rebuilt from its parent's checkpoint and so is
every entry after it, since every later key contains this one.
"""

from __future__ import annotations

import logging
import signal
from collections.abc import Collection
from contextlib import AbstractContextManager
from dataclasses import dataclass
from types import FrameType

from modshop.core.checkpoint import Checkpoint, Store
from modshop.core.clone import Cloner
from modshop.core.errors import NotReproducible, Preflight
from modshop.core.key import VANILLA, Key, Keyer
from modshop.core.recipe import Entry, Recipe, Runner
from modshop.core.stage import StageFactory
from modshop.core.tree import TreeHash
from modshop.core.worktree import WorkTree

log = logging.getLogger("modshop")


@dataclass(frozen=True, slots=True)
class Link:
    entry: Entry
    key: Key
    checkpoint: Checkpoint | None


@dataclass(frozen=True, slots=True)
class BuildResult:
    links: tuple[Link, ...]
    rebuilt: int

    @property
    def end(self) -> Link:
        return self.links[-1]


@dataclass(frozen=True, slots=True)
class ProveResult:
    entries: int
    first_difference: Link | None
    differing_paths: tuple[str, ...]

    @property
    def reproducible(self) -> bool:
        return self.first_difference is None


def vanilla_tree(store: Store) -> TreeHash:
    c = store.get(VANILLA)
    if c is None:
        raise Preflight(f"no vanilla manifest under {store.vanilla}; run `base fetch` then `base index`")
    return c.tree


def resolve(recipe: Recipe, store: Store, keyer: Keyer) -> list[Link]:
    """Each entry's key and checkpoint, up to and including the first entry without one; keys
    after that cannot be computed, since each needs its parent's tree hash."""
    parent, tree = VANILLA, vanilla_tree(store)
    links: list[Link] = []
    for entry in recipe.active():
        key = keyer.key_of(parent, tree, entry)
        ck = store.get(key)
        links.append(Link(entry, key, ck))
        if ck is None:
            break
        parent, tree = key, ck.tree
    return links


class Interrupted(BaseException):
    """SIGTERM or SIGINT arrived; handled like a failing step."""


class Builder:
    def __init__(
        self,
        recipe: Recipe,
        store: Store,
        work: WorkTree,
        keyer: Keyer,
        stages: StageFactory,
        run: Runner,
        cloner: Cloner,
    ) -> None:
        self.recipe, self.store, self.work, self.keyer = recipe, store, work, keyer
        self.stages, self.run, self.cloner = stages, run, cloner

    def build(self, until: Collection[str] = ()) -> BuildResult:
        parent, tree = VANILLA, vanilla_tree(self.store)
        links: list[Link] = []
        rebuilt = 0
        with _interruptible():
            for entry in self.recipe.active():
                key = self.keyer.key_of(parent, tree, entry)
                ck = self.store.get(key)
                if ck is None:
                    ck = self._build_one(entry, key, parent)
                    rebuilt += 1
                links.append(Link(entry, key, ck))
                parent, tree = key, ck.tree
                if entry.name in until:
                    break
        return BuildResult(tuple(links), rebuilt)

    def _build_one(self, entry: Entry, key: Key, parent: Key) -> Checkpoint:
        log.info("== %s  [%s]", entry.name, key)
        since = self.work.restore(self.store.tree(parent), parent, self.cloner)
        self.work.set_dirty()
        try:
            with self.stages(entry) as stage:
                self.run(entry, self.work, stage)
            ck = self.store.commit(self.work, key, parent, entry, since)
        except BaseException:
            log.error(
                "!! %s failed; the working tree is discarded and the next run restores %s", entry.name, parent
            )
            self.work.discard()
            raise
        log.info(
            "   checkpoint %s: %s paths changed, tree %s, %ss", key, ck.changed, ck.tree[:12], ck.seconds
        )
        return ck

    def prove(self, scratch: Store, scratch_work: WorkTree) -> ProveResult:
        """The chain built again from vanilla into `scratch`, no checkpoint reused, must reach the
        same tree hash at every entry as this builder's store holds. Names the first entry that does
        not, with the paths that differ."""
        cached = resolve(self.recipe, self.store, self.keyer)
        if not cached or cached[-1].checkpoint is None or len(cached) != len(self.recipe.active()):
            raise Preflight("the cached chain is incomplete; run a build first")
        other = Builder(self.recipe, scratch, scratch_work, self.keyer, self.stages, self.run, self.cloner)
        parent = VANILLA
        vanilla_tree(scratch)
        with _interruptible():
            for link in cached:
                assert link.checkpoint is not None
                ck = other._build_one(link.entry, link.key, parent)  # pyright: ignore[reportPrivateUsage]
                if ck.tree != link.checkpoint.tree:
                    diff = self.store.manifest(link.key).diff(scratch.manifest(link.key))
                    return ProveResult(len(cached), link, diff.paths())
                parent = link.key
        scratch_work.discard()
        return ProveResult(len(cached), None, ())


class _interruptible(AbstractContextManager[None]):
    """SIGTERM raises like SIGINT does, so a stopped build discards its work tree the same way."""

    def __enter__(self) -> None:
        def raise_it(signum: int, frame: FrameType | None) -> None:
            raise Interrupted(signal.Signals(signum).name)

        self._old = signal.signal(signal.SIGTERM, raise_it)

    def __exit__(self, *exc: object) -> None:
        signal.signal(signal.SIGTERM, self._old)


def not_reproducible(result: ProveResult) -> NotReproducible:
    assert result.first_difference is not None
    return NotReproducible(
        result.first_difference.entry.name, result.first_difference.key, result.differing_paths
    )
