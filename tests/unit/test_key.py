import json
from pathlib import Path

from modshop.core.inputs import HashCache, InputResolver, InputRow
from modshop.core.key import Key, Keyer, KeyMaterial, canonical_entry, code_closure, code_fingerprint
from modshop.core.recipe import Entry
from modshop.core.tree import TreeHash
from modshop.kotor.steps import Copy


def test_canonical_entry_carries_do_and_defaults() -> None:
    e = Entry("m", ("m",), (Copy(src="*"),))
    d = json.loads(canonical_entry(e))
    assert d["steps"][0] == {
        "do": "copy",
        "src": "*",
        "pattern": "*",
        "exclude": [],
        "recursive": False,
        "dest": None,
    }


def test_key_golden() -> None:
    km = KeyMaterial(
        Key("vanilla"), TreeHash("t" * 64), '{"mod":"x"}', (InputRow("x", "a", "d" * 64),), "c", "e"
    )
    assert km.key() == "af6a3a741f991e5d"  # pinned: a change to the key function rebuilds every chain
    assert (
        km.key()
        == KeyMaterial(
            Key("vanilla"), TreeHash("t" * 64), '{"mod":"x"}', (InputRow("x", "a", "d" * 64),), "c", "e"
        ).key()
    )
    assert (
        km.key()
        != KeyMaterial(
            Key("vanilla"), TreeHash("u" * 64), '{"mod":"x"}', (InputRow("x", "a", "d" * 64),), "c", "e"
        ).key()
    )


def test_code_fingerprint_ignores_comments_and_docstrings(tmp_path: Path, monkeypatch: object) -> None:
    import modshop.kotor.steps as steps

    before = code_fingerprint("modshop.kotor.steps")
    src = Path(steps.__file__)
    original = src.read_text()
    try:
        src.write_text(
            original.replace(
                '"""The step kinds, one frozen model each."""', '"""Edited docstring."""  # and a comment'
            )
        )
        assert code_fingerprint("modshop.kotor.steps") == before
        src.write_text(original.replace('pattern: str = "*"', 'pattern: str = "**"'))
        assert code_fingerprint("modshop.kotor.steps") != before
    finally:
        src.write_text(original)


def test_code_closure_excludes_type_checking_imports_and_orchestration() -> None:
    closure = code_closure("modshop.kotor.steps")
    assert "modshop.kotor.steps" in closure
    assert "modshop.core.chain" not in closure
    assert "modshop.core.checkpoint" not in closure
    assert "modshop.cli" not in closure


def test_keyer_unions_entry_and_step_inputs(tmp_path: Path) -> None:
    from modshop.core.config import Paths

    paths = Paths(tmp_path / "data", tmp_path / "games" / "kotor")
    (paths.archives / "m").mkdir(parents=True)
    (paths.archives / "m" / "a.zip").write_bytes(b"zip")
    cache = HashCache(paths.hashcache, paths.archives)
    keyer = Keyer(InputResolver(paths), cache, "code", "env")
    rows = keyer.input_rows(Entry("m", ("m",), ()))
    assert [(r.spec, r.rel) for r in rows] == [("m", "a.zip")]
    k1 = keyer.key_of(Key("vanilla"), TreeHash("t"), Entry("m", ("m",), ()))
    (paths.archives / "m" / "a.zip").write_bytes(b"zip2")
    k2 = keyer.key_of(Key("vanilla"), TreeHash("t"), Entry("m", ("m",), ()))
    assert k1 != k2
