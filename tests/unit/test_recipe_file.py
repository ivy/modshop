"""The real recipe loads from the repository's data files alone, and recipe.json is in sync."""

from pathlib import Path

from modshop.cli.kotor import recipe_json
from modshop.core.key import code_closure
from modshop.kotor.recipe import recipe

GAME_DIR = Path(__file__).resolve().parents[2] / "games" / "kotor"


def test_recipe_loads_without_data_and_matches_recipe_json() -> None:
    r = recipe(GAME_DIR)
    assert len(r.entries) == 202 and len(r.active()) == 190
    assert r.get("170-blaster-adjustment").steps[0].do == "script"
    text = recipe_json(r)
    committed = GAME_DIR / "build" / "recipe.json"
    assert committed.exists(), "run `modshop kotor recipe write`"
    assert committed.read_text() == text, "recipe.json is out of date; run `modshop kotor recipe write`"


def test_code_closure_is_the_pinned_list() -> None:
    assert code_closure("modshop.kotor.runner") == [
        "modshop.core.clone",
        "modshop.core.config",
        "modshop.core.errors",
        "modshop.core.extract",
        "modshop.core.hashing",
        "modshop.core.inputs",
        "modshop.core.recipe",
        "modshop.core.stage",
        "modshop.core.tree",
        "modshop.core.worktree",
        "modshop.kotor",
        "modshop.kotor.context",
        "modshop.kotor.kmrp",
        "modshop.kotor.patcher",
        "modshop.kotor.paths",
        "modshop.kotor.runner",
        "modshop.kotor.steps",
    ]  # pinned: a module entering or leaving the keyed closure is a visible change in review


def test_package_inits_are_empty() -> None:
    src = Path(__file__).resolve().parents[2] / "src" / "modshop"
    for init in src.rglob("__init__.py"):
        if init.parent.name != "cli":
            assert init.read_text().strip() == "", init
