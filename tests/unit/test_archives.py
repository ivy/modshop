import json
from pathlib import Path

import pytest

from modshop.kotor.archives import folder_name, mega_link, slug

GAME_DIR = Path(__file__).resolve().parents[2] / "games" / "kotor"


def test_slug_and_folder_name() -> None:
    assert slug("JC's Minor Fixes") == "jc-s-minor-fixes"
    assert folder_name(6, "KOTOR Community Patch") == "006-kotor-community-patch"


def test_folder_names_reproduce_the_download_layout() -> None:
    mods = json.loads((GAME_DIR / "build" / "k1full.json").read_text())
    titles = [m["title"] for m in mods if m["section"] == "Mod List"]
    assert len(titles) == 186
    assert folder_name(1, titles[0]) == "001-kotor-dialogue-fixes"
    assert folder_name(170, titles[169]) == "170-blaster-adjustment"


def test_mega_link_forms() -> None:
    assert mega_link("https://mega.nz/file/abc123#KEYKEY") == ("abc123", "KEYKEY")
    assert mega_link("https://mega.nz/#!old!KEY2") == ("old", "KEY2")
    with pytest.raises(ValueError):
        mega_link("https://example.com/x")
