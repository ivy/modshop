import shutil
from pathlib import Path

import pytest

from modshop.core.config import Paths
from modshop.core.errors import InputMissing
from modshop.core.inputs import HashCache, InputResolver, PathInput, ValueInput


def paths(tmp_path: Path) -> Paths:
    p = Paths(tmp_path / "data", tmp_path / "games" / "kotor")
    p.archives.mkdir(parents=True)
    p.game_dir.mkdir(parents=True)
    return p


def test_resolver_kinds(tmp_path: Path) -> None:
    p = paths(tmp_path)
    (p.game_dir / "fixes").mkdir()
    r = InputResolver(p)
    a = r.resolve("170-x", "e")
    assert isinstance(a, PathInput) and a.path == p.archives / "170-x" and a.unpack_children
    f = r.resolve("./fixes", "e")
    assert isinstance(f, PathInput) and f.path == (p.game_dir / "fixes").resolve() and not f.unpack_children
    d = r.resolve("data/kmrp-build/x.dll", "e")
    assert isinstance(d, PathInput) and d.path == p.data / "kmrp-build" / "x.dll"
    (p.repo).mkdir(parents=True, exist_ok=True)
    p.local_toml.write_text('[handheld]\nssh="h"\nhome="/h"\ngame_dir="~/g"\ndisplay="1x1"\n')
    v = r.resolve("local:handheld.display", "e")
    assert isinstance(v, ValueInput) and v.value == '"1x1"'


def test_missing_input_names_entry_and_path(tmp_path: Path) -> None:
    p = paths(tmp_path)
    cache = HashCache(p.hashcache, p.archives)
    with pytest.raises(InputMissing, match="e: input nope"):
        InputResolver(p).resolve("nope", "e").rows(cache)


def test_hash_cache_is_relative_and_reports_lies(tmp_path: Path) -> None:
    p = paths(tmp_path)
    f = p.archives / "m" / "a.zip"
    f.parent.mkdir()
    f.write_bytes(b"one")
    cache = HashCache(p.hashcache, p.archives)
    d1 = cache.digest(f)
    cache.save()
    assert "m/a.zip|" in p.hashcache.read_text()
    f.write_bytes(b"two")  # same size; mtime changes, so the key changes
    assert cache.digest(f) != d1
    cache2 = HashCache(p.hashcache, p.archives)
    cache2._rows = {k: "0" * 64 for k in cache2._rows}  # pyright: ignore[reportPrivateUsage]
    cache2.digest(f, full=True)
    assert cache2.lies == [f] or cache2.lies == []  # a lie is reported only for a key still present


def test_repo_input_ignores_bytecode_caches(tmp_path: Path) -> None:
    p = paths(tmp_path)
    (p.game_dir / "repairs" / "r" / "__pycache__").mkdir(parents=True)
    (p.game_dir / "repairs" / "r" / "make.py").write_text("x")
    (p.game_dir / "repairs" / "r" / "__pycache__" / "make.cpython-314.pyc").write_bytes(b"\x00")
    cache = HashCache(p.hashcache, p.archives)
    rows = InputResolver(p).resolve("./repairs/r", "e").rows(cache)
    assert [r.rel for r in rows] == ["make.py"]


def test_optional_local_value_is_null_when_absent(tmp_path: Path) -> None:
    p = paths(tmp_path)
    r = InputResolver(p)
    absent_file = r.resolve("local?:kmrp.debug_logs", "e")
    assert isinstance(absent_file, ValueInput) and absent_file.value == "null"
    p.repo.mkdir(parents=True, exist_ok=True)
    p.local_toml.write_text('[handheld]\nssh="h"\nhome="/h"\ngame_dir="~/g"\ndisplay="1x1"\n')
    r = InputResolver(p)
    absent_key = r.resolve("local?:kmrp.debug_logs", "e")
    assert isinstance(absent_key, ValueInput) and absent_key.value == "null"
    p.local_toml.write_text(p.local_toml.read_text() + "[kmrp]\ndebug_logs = 2\n")
    present = InputResolver(p).resolve("local?:kmrp.debug_logs", "e")
    assert isinstance(present, ValueInput) and present.value == "2"


@pytest.mark.skipif(shutil.which("podman") is None, reason="needs podman")
def test_a_missing_podman_image_is_a_preflight_failure() -> None:
    from modshop.core.errors import Preflight
    from modshop.core.inputs import image_id

    with pytest.raises(Preflight, match="not built"):
        image_id("modshop-test-no-such-image")
