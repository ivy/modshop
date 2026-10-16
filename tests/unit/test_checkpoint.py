from pathlib import Path

from modshop.core.checkpoint import FIXED_MTIME_NS, Store
from modshop.core.clone import Cloner
from modshop.core.key import VANILLA, Key
from modshop.core.recipe import Entry
from modshop.core.tree import Manifest, Symlink
from modshop.core.worktree import WorkTree


def make_store(tmp_path: Path) -> tuple[Store, WorkTree]:
    vanilla = tmp_path / "vanilla"
    (vanilla / "tree" / "Override").mkdir(parents=True)
    (vanilla / "tree" / "Override" / "a.tga").write_bytes(b"a")
    (vanilla / "tree" / "Override" / "gone.tga").write_bytes(b"g")
    (vanilla / "tree" / "dialog.tlk").write_bytes(b"tlk")
    store = Store(tmp_path / "ckpt", vanilla, Cloner(reflink=False))
    store.index_vanilla()
    return store, WorkTree(tmp_path / "work", tmp_path / "work.json")


def test_index_vanilla_writes_manifest_and_meta(tmp_path: Path) -> None:
    store, _ = make_store(tmp_path)
    c = store.get(VANILLA)
    assert c is not None and c.parent is None and c.mod == "vanilla" and c.files == 3
    assert c.tree == store.manifest(VANILLA).tree_hash
    assert (store.tree(VANILLA) / "dialog.tlk").stat().st_mtime_ns == FIXED_MTIME_NS


def test_commit_hardlinks_unchanged_and_clones_changed(tmp_path: Path) -> None:
    store, work = make_store(tmp_path)
    since = work.restore(store.tree(VANILLA), VANILLA, Cloner(reflink=False))
    (work.path / "Override" / "a.tga").write_bytes(b"A")
    (work.path / "Override" / "gone.tga").unlink()
    (work.path / "Override" / "new.tpc").write_bytes(b"n")
    (work.path / "override").symlink_to("Override")
    c = store.commit(work, Key("k1"), VANILLA, Entry("one", ("one",)), since)
    assert c.parent == VANILLA and c.mod == "one" and c.changed == 4
    tree = store.tree(Key("k1"))
    assert (tree / "dialog.tlk").stat().st_ino == (store.tree(VANILLA) / "dialog.tlk").stat().st_ino
    assert (tree / "Override" / "a.tga").stat().st_ino != (
        store.tree(VANILLA) / "Override" / "a.tga"
    ).stat().st_ino
    assert (store.tree(VANILLA) / "Override" / "a.tga").read_bytes() == b"a"
    assert not (tree / "Override" / "gone.tga").exists()
    assert store.manifest(Key("k1"))["override"] == Symlink("Override")
    assert store.manifest(Key("k1")) == Manifest.of_tree(tree)
    assert (
        store.ckpt / "k1" / "changed.txt"
    ).read_text() == "~ Override/a.tga\n- Override/gone.tga\n+ Override/new.tpc\n+ override\n"
    assert work.key() == Key("k1")
    assert [x.key for x in store.lineage(Key("k1"))] == [VANILLA, Key("k1")]
    assert store.keys() == [Key("k1")]


def test_dirty_record_forces_restore(tmp_path: Path) -> None:
    store, work = make_store(tmp_path)
    work.restore(store.tree(VANILLA), VANILLA, Cloner(reflink=False))
    work.set_dirty()
    (work.path / "dialog.tlk").write_bytes(b"half written")
    assert work.key() is None
    work.restore(store.tree(VANILLA), VANILLA, Cloner(reflink=False))
    assert (work.path / "dialog.tlk").read_bytes() == b"tlk"


def test_clear_partial(tmp_path: Path) -> None:
    store, _ = make_store(tmp_path)
    (store.ckpt / "abc.tmp").mkdir(parents=True)
    store.clear_partial()
    assert not (store.ckpt / "abc.tmp").exists()
