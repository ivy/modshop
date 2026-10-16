from pathlib import Path

import pytest

from modshop.core.deploy import Deployer, DeployError, LocalTransport, Target


def make(tmp_path: Path) -> tuple[Path, Path, Deployer]:
    tree = tmp_path / "tree"
    (tree / "Override").mkdir(parents=True)
    (tree / "Override" / "a.tga").write_bytes(b"a")
    (tree / "swkotor.ini").write_bytes(b"ini from build")
    (tree / "saves").mkdir()
    live = tmp_path / "swkotor"
    (live / "Override").mkdir(parents=True)
    (live / "Override" / "a.tga").write_bytes(b"old")
    (live / "Override" / "stray.tga").write_bytes(b"s")
    (live / "Saves").mkdir()
    (live / "Saves" / "game1.sav").write_bytes(b"save")
    (live / "kmrp-kpm.log").write_bytes(b"log")
    target = Target(
        LocalTransport(),
        str(live),
        ("/Saves/", "/saves/", "*.log", "/swkotor.ini"),
        ("swkotor.ini",),
        "no-such-process",
    )
    return tree, live, Deployer(target)


def test_drift_then_deploy_then_clean(tmp_path: Path) -> None:
    tree, live, d = make(tmp_path)
    drift = d.drift(tree)
    assert drift and sorted(line.split()[-1] for line in drift.lines) == [
        "Override/a.tga",
        "Override/stray.tga",
    ]
    result = d.deploy(tree)
    assert result.updated == 2 and result.previous == f"{live}.prev"
    assert (live / "Override" / "a.tga").read_bytes() == b"a"
    assert not (live / "Override" / "stray.tga").exists()
    assert (live / "Saves" / "game1.sav").read_bytes() == b"save"  # outside the comparison
    assert (live / "kmrp-kpm.log").exists()
    assert (live / "swkotor.ini").read_bytes() == b"ini from build"  # the target had none: sent once
    assert not (live / "saves").exists()
    assert (Path(f"{live}.prev") / "Override" / "stray.tga").exists()  # the rollback
    assert not d.drift(tree)
    assert d.deploy(tree).updated == 0
    (live / "swkotor.ini").write_bytes(b"edited by the game")
    (live / "Override" / "a.tga").write_bytes(b"drifted")
    assert [line.split()[-1] for line in d.drift(tree).lines] == ["Override/a.tga"]


def test_deploy_refuses_while_game_runs(tmp_path: Path) -> None:
    tree, live, d = make(tmp_path)
    d.target = Target(LocalTransport(), str(live), (), (), "sh")  # a shell is always running somewhere
    with pytest.raises(DeployError, match="running"):
        d.deploy(tree)
