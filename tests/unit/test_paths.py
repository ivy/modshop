from pathlib import Path

from modshop.kotor.paths import ci_find, ci_path, collapse_case, files_in, put


def tree(tmp_path: Path) -> Path:
    (tmp_path / "Mod_v1" / "Mod" / "override").mkdir(parents=True)
    (tmp_path / "Mod_v1" / "Mod" / "override" / "A.tga").write_bytes(b"a")
    (tmp_path / "Mod_v1" / "Mod" / "override" / "readme.txt").write_bytes(b"r")
    (tmp_path / "Mod_v1" / "__MACOSX").mkdir()
    (tmp_path / "Mod_v1" / "Mod" / "TSLPatchdata").mkdir()
    return tmp_path


def test_ci_find_prefers_exact_spelling(tmp_path: Path) -> None:
    (tmp_path / "a.tga").write_bytes(b"")
    (tmp_path / "A.tga").write_bytes(b"")
    assert ci_find(tmp_path, "A.tga") is not None and ci_find(tmp_path, "A.tga").name == "A.tga"  # pyright: ignore[reportOptionalMemberAccess]
    assert ci_find(tmp_path, "a.TGA") is not None
    assert ci_find(tmp_path, "nope") is None
    assert ci_find(tmp_path / "missing", "x") is None


def test_ci_path_wildcards_case_and_wrapper_levels(tmp_path: Path) -> None:
    root = tree(tmp_path)
    assert ci_path(root, "*/Mod/Override") == root / "Mod_v1" / "Mod" / "override"
    assert (
        ci_path(root, "*/tslpatchdata") == root / "Mod_v1" / "Mod" / "TSLPatchdata"
    )  # one extra level tried
    assert ci_path(root, "Mod_v1\\Mod\\override\\a.tga") == root / "Mod_v1" / "Mod" / "override" / "A.tga"
    assert ci_path(root, "nothing/here") == root / "nothing" / "here"  # returned as given
    assert ci_path(root, ".") == root


def test_files_in_skips_docs_and_macosx(tmp_path: Path) -> None:
    root = tree(tmp_path)
    names = [p.name for p in files_in(root / "Mod_v1", recursive=True)]
    assert names == ["A.tga"]


def test_put_replaces_case_variant(tmp_path: Path) -> None:
    dest = tmp_path / "Override"
    dest.mkdir()
    (dest / "a.tga").write_bytes(b"old")
    src = tmp_path / "A.tga"
    src.write_bytes(b"new")
    put(src, dest)
    assert sorted(p.name for p in dest.iterdir()) == ["A.tga"]
    assert (dest / "A.tga").read_bytes() == b"new"


def test_collapse_case_keeps_newest(tmp_path: Path) -> None:
    (tmp_path / "x.tga").write_bytes(b"first")
    import time

    time.sleep(0.01)
    (tmp_path / "X.TGA").write_bytes(b"second")
    result = collapse_case(tmp_path)
    assert [p.name for p in tmp_path.iterdir()] == ["X.TGA"]
    assert result[0][0].name == "X.TGA" and [p.name for p in result[0][1]] == ["x.tga"]
