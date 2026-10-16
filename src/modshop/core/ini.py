"""Single keys of an INI file, read and set with every other byte left as it was.

Sections and keys match without regard to case; a set keeps the file's line endings.
"""

from __future__ import annotations


def _split(data: bytes) -> list[str]:
    return data.decode("latin-1").splitlines(keepends=True)


def _section(line: str) -> str | None:
    s = line.strip()
    return s[1:-1].strip().casefold() if s.startswith("[") and s.endswith("]") else None


def _key(line: str) -> str | None:
    if "=" not in line or _section(line) is not None:
        return None
    return line.split("=", 1)[0].strip().casefold()


def get(data: bytes, section: str, key: str) -> str | None:
    current = None
    for line in _split(data):
        if (s := _section(line)) is not None:
            current = s
        elif current == section.casefold() and _key(line) == key.casefold():
            return line.split("=", 1)[1].rstrip("\r\n").strip()
    return None


def put(data: bytes, section: str, key: str, value: str) -> bytes:
    lines = _split(data)
    eol = "\r\n" if b"\r\n" in data else "\n"
    current = None
    last_in_section: int | None = None
    for i, line in enumerate(lines):
        if (s := _section(line)) is not None:
            current = s
            if s == section.casefold():
                last_in_section = i
        elif current == section.casefold():
            if _key(line) == key.casefold():
                ending = line[len(line.rstrip("\r\n")) :]
                lines[i] = f"{line.split('=', 1)[0]}={value}{ending}"
                return "".join(lines).encode("latin-1")
            if line.strip():
                last_in_section = i
    if last_in_section is None:
        if lines and not lines[-1].endswith(("\r", "\n")):
            lines[-1] += eol
        lines += [eol, f"[{section}]{eol}", f"{key}={value}{eol}"]
    else:
        if not lines[last_in_section].endswith(("\r", "\n")):
            lines[last_in_section] += eol
        lines.insert(last_in_section + 1, f"{key}={value}{eol}")
    return "".join(lines).encode("latin-1")
