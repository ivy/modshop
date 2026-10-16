from modshop.core import ini

TEXT = b"[A]\r\nx=1\r\n\r\n[Graphics Options]\r\nWidth=800\r\n\r\n[C]\r\ny=2"


def test_get_matches_section_and_key_without_case() -> None:
    assert ini.get(TEXT, "graphics options", "WIDTH") == "800"
    assert ini.get(TEXT, "A", "Width") is None
    assert ini.get(TEXT, "Missing", "x") is None


def test_put_replaces_in_place_and_keeps_line_endings() -> None:
    out = ini.put(TEXT, "Graphics Options", "Width", "1920")
    assert out == TEXT.replace(b"Width=800", b"Width=1920")


def test_put_adds_a_missing_key_to_its_section() -> None:
    out = ini.put(TEXT, "Graphics Options", "FullScreen", "1")
    assert out == TEXT.replace(b"Width=800\r\n", b"Width=800\r\nFullScreen=1\r\n")


def test_put_adds_a_missing_section_at_the_end() -> None:
    out = ini.put(TEXT, "New", "k", "v")
    assert out == TEXT + b"\r\n\r\n[New]\r\nk=v\r\n"
    assert ini.get(out, "New", "k") == "v"
