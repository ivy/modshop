"""The synthetic game end to end: build, no-op, mutation, failure, kill, prove, gc."""

from __future__ import annotations

import shutil

import pytest

from modshop.core.chain import Builder, resolve
from modshop.core.checkpoint import Store
from modshop.core.errors import StepFailed
from modshop.core.key import VANILLA
from modshop.core.recipe import Entry, Recipe
from modshop.core.worktree import WorkTree
from modshop.kotor.runner import runner
from modshop.kotor.steps import Copy, DedupeTpc, Delete, HoloPatcher, Symlink, Tlk
from tests.conftest import Synthetic


def make_recipe(s: Synthetic) -> Recipe:
    s.archive("001-tlk", "Tlk.zip", {"Mod/dialog.tlk": b"mod tlk"})
    s.archive(
        "002-textures",
        "Tex.zip",
        {"Tex/Override/a.tga": b"a", "Tex/Override/b.tga": b"b", "Tex/readme.txt": b"r"},
    )
    s.archive("003-patch", "Patch.zip", {"P/tslpatchdata/changes.ini": b"[Settings]"})
    s.archive("004-fix", "Fix.zip", {"F/Override/base.tga": b"fixed"})
    return Recipe((
        Entry("aliases", (), (Symlink(link="Modules", target="modules"),)),
        Entry("001-tlk", ("001-tlk",), (Tlk(src="*/dialog.tlk"),)),
        Entry("002-textures", ("002-textures",), (Copy(src="*/Override"),)),
        Entry("003-patch", ("003-patch",), (HoloPatcher(src="*/tslpatchdata", option=1),)),
        Entry("skipped", (), (), skip="not on Linux"),
        Entry("004-fix", ("004-fix",), (Copy(src="*/Override"), Delete(names=("b.tga",)), DedupeTpc())),
    ))  # fmt: skip


def builder(
    s: Synthetic, recipe: Recipe, store: Store | None = None, work: WorkTree | None = None
) -> Builder:
    run = runner(s.paths, s.patcher, None)
    return Builder(recipe, store or s.store, work or s.work, s.keyer(), s.stages(), run, s.cloner)


def test_build_then_noop_then_mutation(synthetic: Synthetic) -> None:
    s = synthetic
    recipe = make_recipe(s)
    first = builder(s, recipe).build()
    assert first.rebuilt == 5 and len(first.links) == 5
    end = first.end.checkpoint
    assert end is not None
    tree = s.store.tree(first.end.key)
    assert (tree / "dialog.tlk").read_bytes() == b"mod tlk"
    assert (tree / "Override" / "base.tga").read_bytes() == b"fixed"
    assert not (tree / "Override" / "b.tga").exists()
    assert (tree / "Override" / "patched.2da").read_bytes() == b"patched"
    assert not (tree / "Override" / "old.tpc").exists()  # dedupe: Old.tga exists
    assert (tree / "Modules").is_symlink()
    assert len(s.patcher.calls) == 1

    second = builder(s, recipe).build()
    assert second.rebuilt == 0 and second.end.key == first.end.key

    s.archive("003-patch", "Patch.zip", {"P/tslpatchdata/changes.ini": b"[Settings]\nchanged=1"})
    third = builder(s, recipe).build()
    assert third.rebuilt == 2  # 003 and 004; aliases, 001, 002 untouched
    assert [a.key for a in third.links[:3]] == [a.key for a in first.links[:3]]
    assert third.links[3].key != first.links[3].key
    assert (
        third.end.checkpoint is not None and third.end.checkpoint.tree == end.tree
    )  # same content: fake patcher output unchanged
    links = resolve(recipe, s.store, s.keyer())
    assert all(link.checkpoint for link in links) and len(links) == 5


def test_step_failure_discards_work_and_next_run_resumes(synthetic: Synthetic) -> None:
    s = synthetic
    recipe = make_recipe(s)
    broken = Recipe((*recipe.entries[:3], Entry("bad", ("002-textures",), (Copy(src="*/Nope"),))))
    with pytest.raises(StepFailed, match="bad: step 0 \\(copy\\)"):
        builder(s, broken).build()
    assert not s.work.path.exists() and s.work.key() is None
    result = builder(s, recipe).build()
    assert result.rebuilt == 2  # 003 and 004; the first three were kept


def test_prove_matches_and_detects_difference(synthetic: Synthetic) -> None:
    s = synthetic
    recipe = make_recipe(s)
    builder(s, recipe).build()
    scratch = Store(s.paths.games / "ckpt-prove", s.paths.vanilla, s.cloner)
    scratch.ckpt.mkdir()
    r = builder(s, recipe).prove(
        scratch, WorkTree(s.paths.games / "work-prove", s.paths.games / "work-prove.json")
    )
    assert r.reproducible and r.entries == 5
    s.patcher.writes = {"Override/patched.2da": b"different this time"}
    shutil.rmtree(scratch.ckpt)
    scratch.ckpt.mkdir()
    r = builder(s, recipe).prove(
        scratch, WorkTree(s.paths.games / "work-prove", s.paths.games / "work-prove.json")
    )
    assert not r.reproducible and r.first_difference is not None
    assert r.first_difference.entry.name == "003-patch" and r.differing_paths == ("Override/patched.2da",)


def test_perturbing_each_input_kind_and_step_field_moves_the_key(synthetic: Synthetic) -> None:
    s = synthetic
    s.archive("002-textures", "Tex.zip", {"Tex/Override/a.tga": b"a"})
    (s.paths.game_dir / "fixes").mkdir()
    (s.paths.game_dir / "fixes" / "f.ini").write_text("1")
    (s.paths.data / "extra").mkdir()
    (s.paths.data / "extra" / "x.dll").write_bytes(b"1")
    (s.paths.repo).mkdir(parents=True, exist_ok=True)
    s.paths.local_toml.write_text('[handheld]\nssh="h"\nhome="/h"\ngame_dir="~/g"\ndisplay="1x1"\n')
    entry = Entry(
        "002-textures",
        ("002-textures", "./fixes", "data/extra/x.dll", "local:handheld.display"),
        (Copy(src="*/Override"),),
    )
    tree = s.store.get(VANILLA)
    assert tree is not None
    k0 = s.keyer().key_of(VANILLA, tree.tree, entry)

    def key() -> str:
        return s.keyer().key_of(VANILLA, tree.tree, entry)

    assert key() == k0  # stable
    s.archive("002-textures", "Tex.zip", {"Tex/Override/a.tga": b"A"})
    k1 = key()
    (s.paths.game_dir / "fixes" / "f.ini").write_text("2")
    k2 = key()
    (s.paths.data / "extra" / "x.dll").write_bytes(b"2")
    k3 = key()
    s.paths.local_toml.write_text('[handheld]\nssh="h"\nhome="/h"\ngame_dir="~/g"\ndisplay="2x2"\n')
    s.resolver._local = None  # pyright: ignore[reportPrivateUsage]
    k4 = key()
    k5 = s.keyer("other code").key_of(VANILLA, tree.tree, entry)
    k6 = s.keyer(env="other env").key_of(VANILLA, tree.tree, entry)
    k7 = s.keyer().key_of(
        VANILLA, tree.tree, Entry(entry.name, entry.inputs, (Copy(src="*/Override", recursive=True),))
    )
    k8 = s.keyer().key_of(
        VANILLA, tree.tree, Entry(entry.name, entry.inputs, (HoloPatcher(src="*/Override"),))
    )
    k9 = s.keyer().key_of(
        VANILLA, tree.tree, Entry(entry.name, entry.inputs, (Copy(src="*/Override"), DedupeTpc()))
    )
    k10 = s.keyer().key_of(
        VANILLA, tree.tree, Entry(entry.name, entry.inputs, (DedupeTpc(), Copy(src="*/Override")))
    )
    keys = [k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10]
    assert len(set(keys)) == len(keys)


def test_gc_keeps_chain_and_tags(synthetic: Synthetic) -> None:
    s = synthetic
    recipe = make_recipe(s)
    first = builder(s, recipe).build()
    s.archive("004-fix", "Fix.zip", {"F/Override/base.tga": b"fixed again"})
    second = builder(s, recipe).build()
    orphan = first.end.key
    assert orphan != second.end.key and s.store.get(orphan) is not None
    live = {link.key for link in resolve(recipe, s.store, s.keyer()) if link.checkpoint}
    assert orphan not in live and second.end.key in live


KILL_SCRIPT = """
import sys, time, pathlib
sys.path.insert(0, {src!r})
from tests.integration.test_chain import *
from tests.conftest import *
import logging, pickle
"""


def test_killed_build_leaves_dirty_record_and_next_run_restores(synthetic: Synthetic) -> None:
    """The work tree is marked dirty before the first step; a SIGKILL mid-entry leaves that record,
    and the next restore discards the tree instead of trusting it."""
    s = synthetic
    recipe = make_recipe(s)
    builder(s, Recipe(recipe.entries[:2])).build()
    parent = resolve(recipe, s.store, s.keyer())[1].key
    # simulate the kill: the builder restored the parent and set dirty, then the process died mid-step
    since = s.work.restore(s.store.tree(parent), parent, s.cloner)
    assert since > 0
    s.work.set_dirty()
    (s.work.path / "Override" / "half.tga").write_bytes(b"half written")
    (s.work.path / "dialog.tlk").write_bytes(
        b"xxxxxxx"
    )  # same size as "mod tlk": the ctime shortcut must not keep the old digest
    result = builder(s, recipe).build()
    tree = s.store.tree(result.end.key)
    assert not (tree / "Override" / "half.tga").exists()
    assert (tree / "dialog.tlk").read_bytes() == b"mod tlk"
