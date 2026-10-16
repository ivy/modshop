import os
import time
from pathlib import Path

from modshop.core.tree import File, Manifest, Symlink, normalise_mtimes, walk


def make_tree(root: Path) -> None:
    (root / "Override").mkdir(parents=True)
    (root / "Override" / "a.tga").write_bytes(b"aaa")
    (root / "Override" / "with space.txt").write_bytes(b"s")
    (root / "modules").mkdir()
    (root / "modules" / "m.mod").write_bytes(b"mmm")
    (root / "dialog.tlk").write_bytes(b"tlk")
    (root / "Modules").symlink_to("modules")


def test_walk_lists_symlinked_dirs_as_entries_and_sorts_by_bytes(tmp_path: Path) -> None:
    make_tree(tmp_path)
    rels = [p.relative_to(tmp_path).as_posix() for p in walk(tmp_path)]
    assert rels == ["Modules", "Override/a.tga", "Override/with space.txt", "dialog.tlk", "modules/m.mod"]


def test_manifest_round_trip_and_hash_is_content_only(tmp_path: Path) -> None:
    make_tree(tmp_path / "x")
    m = Manifest.of_tree(tmp_path / "x")
    assert m["Modules"] == Symlink("modules")
    assert isinstance(m["Override/with space.txt"], File)
    h = m.write(tmp_path / "manifest.txt")
    assert Manifest.read(tmp_path / "manifest.txt") == m
    assert h == m.tree_hash
    make_tree(tmp_path / "y")
    os.utime(tmp_path / "y" / "dialog.tlk", ns=(1, 1))
    assert Manifest.of_tree(tmp_path / "y").tree_hash == h


def test_of_tree_keeps_prior_digest_only_for_untouched_inodes(tmp_path: Path) -> None:
    make_tree(tmp_path)
    prior = Manifest.of_tree(tmp_path)
    fake = Manifest({**prior, "dialog.tlk": File("0" * 64, 3), "Override/a.tga": File("1" * 64, 3)})
    os.sync()
    since = time.time_ns()
    time.sleep(0.01)
    (tmp_path / "Override" / "a.tga").write_bytes(b"bbb")  # same size, new ctime
    m = Manifest.of_tree(tmp_path, prior=fake, since_ns=since)
    assert m["dialog.tlk"] == File("0" * 64, 3)  # untouched: the prior digest is trusted
    assert m["Override/a.tga"] == File("3e744b9dc39389baf0c5a0660589b8402f3dbb49b89b3e75f2c9355852a3c677", 3)


def test_diff_names_added_removed_changed(tmp_path: Path) -> None:
    make_tree(tmp_path)
    before = Manifest.of_tree(tmp_path)
    (tmp_path / "Override" / "a.tga").write_bytes(b"changed")
    (tmp_path / "dialog.tlk").unlink()
    (tmp_path / "Override" / "new.tpc").write_bytes(b"n")
    after = Manifest.of_tree(tmp_path)
    c = before.diff(after)
    assert c.added == ("Override/new.tpc",)
    assert c.removed == ("dialog.tlk",)
    assert c.changed == ("Override/a.tga",)
    assert c.text() == "~ Override/a.tga\n+ Override/new.tpc\n- dialog.tlk\n"
    assert not before.diff(before)


def test_normalise_mtimes(tmp_path: Path) -> None:
    make_tree(tmp_path)
    n = normalise_mtimes(tmp_path, 946684801 * 10**9)
    assert n == 4
    assert normalise_mtimes(tmp_path, 946684801 * 10**9) == 0
    assert (tmp_path / "dialog.tlk").stat().st_mtime_ns == 946684801 * 10**9
