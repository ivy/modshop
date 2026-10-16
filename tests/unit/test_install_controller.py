import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[2] / "games" / "kotor" / "kmrp-build" / "install-controller.py"


def script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("install_controller", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_set_debug_logs_replaces_the_line_and_keeps_crlf(tmp_path: Path) -> None:
    ini = tmp_path / "configs" / "kmrp-controller.ini"
    ini.parent.mkdir()
    ini.write_bytes(b"[Patch Options]\r\ndebug-logs=0\r\n")
    script().set_debug_logs(ini, 2)
    assert ini.read_bytes() == b"[Patch Options]\r\ndebug-logs=2\r\n"


def test_set_debug_logs_writes_the_section_when_absent(tmp_path: Path) -> None:
    ini = tmp_path / "configs" / "kmrp-controller.ini"
    script().set_debug_logs(ini, 1)
    assert ini.read_bytes() == b"[Patch Options]\r\ndebug-logs=1\r\n"
