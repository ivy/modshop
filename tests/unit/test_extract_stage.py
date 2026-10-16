import zipfile
from pathlib import Path

from modshop.core.extract import Extractor, fix_backslash_names
from modshop.core.recipe import Entry
from modshop.core.stage import stage_dir, staged
from tests.conftest import Synthetic


def test_fix_backslash_names(tmp_path: Path) -> None:
    (tmp_path / "a\\b\\c.tga").write_bytes(b"x")
    fix_backslash_names(tmp_path)
    assert (tmp_path / "a" / "b" / "c.tga").read_bytes() == b"x"


def test_extractor_places_archive_file_and_folder(tmp_path: Path) -> None:
    z = tmp_path / "Mod.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("Mod/Override/a.tga", b"a")
    loose = tmp_path / "loose.txt"
    loose.write_bytes(b"l")
    folder = tmp_path / "folder"
    (folder / "sub").mkdir(parents=True)
    (folder / "sub" / "f").write_bytes(b"f")
    out = tmp_path / "stage"
    out.mkdir()
    ex = Extractor()
    ex.place(z, out)
    ex.place(loose, out)
    ex.place(folder, out)
    assert (out / "Mod" / "Mod" / "Override" / "a.tga").read_bytes() == b"a"
    assert (out / "loose.txt").exists() and (out / "folder" / "sub" / "f").exists()
    assert ex.version().startswith("7-Zip")


def test_stage_holds_entry_inputs_only_and_is_removed(synthetic: Synthetic) -> None:
    synthetic.archive("001-mod", "Mod.zip", {"Override/a.tga": b"a"})
    (synthetic.paths.game_dir / "fixes" / "fix").mkdir(parents=True)
    (synthetic.paths.game_dir / "fixes" / "fix" / "changes.ini").write_text("x")
    entry = Entry("001-mod", ("001-mod", "./fixes/fix"))
    with staged(synthetic.paths.stage, synthetic.resolver, Extractor(), entry) as st:
        assert st.path == stage_dir(synthetic.paths.stage, entry)
        assert (st.path / "Mod" / "Override" / "a.tga").exists()
        assert (st.path / "fix" / "changes.ini").exists()
    assert not st.path.exists()
