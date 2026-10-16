from pathlib import Path

import pytest

from modshop.core.config import Local, Paths
from modshop.core.errors import Preflight


def test_paths_resolve_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game = tmp_path / "repo" / "games" / "kotor"
    game.mkdir(parents=True)
    monkeypatch.delenv("KOTOR_DATA", raising=False)
    assert Paths.resolve(game).data == (game / "data").resolve()
    monkeypatch.setenv("KOTOR_DATA", str(tmp_path / "elsewhere"))
    assert Paths.resolve(game).data == (tmp_path / "elsewhere").resolve()
    assert Paths.resolve(game, tmp_path / "arg").data == (tmp_path / "arg").resolve()
    assert Paths.resolve(game).local_toml == (tmp_path / "repo" / "local.toml").resolve()


def test_local_loads_and_reads_dotted(tmp_path: Path) -> None:
    f = tmp_path / "local.toml"
    f.write_text('[handheld]\nssh="h"\nhome="/home/u"\ngame_dir="~/g"\ndisplay="1920x1080"\nextra="x"\n')
    local = Local.load(f)
    assert local.handheld.game_dir_absolute == "/home/u/g"
    assert local.value("handheld.display") == "1920x1080"
    assert local.value("handheld.extra") == "x"
    with pytest.raises(Preflight):
        Local.load(tmp_path / "missing.toml")
