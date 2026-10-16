"""The running game's executable, as a file a disassembler can read.

Steam's swkotor.exe is SteamStub-wrapped: `.text` is encrypted on disk and decrypted in memory at
start-up, so the code has to come out of the running process. `dump` reads the image over ssh
from the Wine process that maps the PE at its image base (the pressure-vessel wrappers carry
`swkotor.exe` in their arguments too, so the command line alone picks the wrong process). Every
section but `.text` is then taken from the executable on disk, which holds them unencrypted and
unresolved: vanilla bytes, imports a disassembler can name. In `.text`, KPM's hook sites go back
to the bytes `patch_config.toml` records; a call or jump whose target lies outside the image in
memory the process has mapped is a redirect some module made without an entry there, and is
listed rather than restored, since nothing records what it replaced. The result is written as a
PE whose file layout is its memory layout. Nothing on the handheld is written.
"""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from modshop.core.config import Handheld
from modshop.core.errors import ModshopError

IMAGE_BASE = 0x400000
PAGE = 0x1000
CODE = ".text"
# KPM's code caves and the modules' trampolines are small anonymous allocations; Wine and the
# graphics stack map executable memory too, most of it far larger, which is where a stray E8 or E9
# byte lands. Measured on one session: every redirect two sessions disagreed on was inside this.
CAVE_LIMIT = 1 << 20


class DumpError(ModshopError):
    pass


# Runs on the handheld with its own python3, fed on stdin: writes the image to stdout and one JSON
# line to stderr, with the process's other executable mappings. SizeOfImage comes from the mapped
# header.
REMOTE = r"""
import json, os, struct, sys
BASE, PAGE = 0x400000, 0x1000
def wine_pid():
    for p in os.listdir('/proc'):
        if not p.isdigit():
            continue
        try:
            with open(f'/proc/{p}/maps') as maps:
                for line in maps:
                    if line.startswith('00400000-') and line.rstrip().lower().endswith('swkotor.exe'):
                        return int(p)
        except OSError:
            continue
    return None
pid = wine_pid()
if pid is None:
    sys.exit('no process maps swkotor.exe at 0x400000; is the game running?')
out, missing = bytearray(), 0
with open(f'/proc/{pid}/mem', 'rb', buffering=0) as mem:
    mem.seek(BASE)
    head = mem.read(PAGE)
    pe = struct.unpack_from('<I', head, 0x3C)[0]
    size = struct.unpack_from('<I', head, pe + 24 + 56)[0]
    for a in range(BASE, BASE + size, PAGE):
        try:
            mem.seek(a)
            out += mem.read(PAGE)
        except OSError:
            out += bytes(PAGE)
            missing += 1
regions, exe = [], ''
with open(f'/proc/{pid}/maps') as maps:
    for line in maps:
        f = line.split(maxsplit=5)
        lo, hi = (int(x, 16) for x in f[0].split('-'))
        path = f[5].strip() if len(f) > 5 else ''
        if lo == BASE:
            exe = path
        elif hi <= 1 << 32 and 'x' in f[1] and not BASE <= lo < BASE + size:
            regions.append([lo, hi, path])
sys.stderr.write(json.dumps({'size': size, 'missing_pages': missing, 'regions': regions, 'exe': exe}) + '\n')
sys.stdout.buffer.write(out)
"""


@dataclass(frozen=True, slots=True)
class Section:
    name: str
    va: int
    vsize: int
    raw_at: int
    raw_size: int


@dataclass(frozen=True, slots=True)
class HookRestore:
    restored: int
    unchanged: int
    # in-place byte patches, which are not jumps: restored like the rest, listed for the record
    in_place: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Redirect:
    at: int
    op: str
    target: int
    region: str


@dataclass(frozen=True, slots=True)
class Dump:
    exe: Path
    record: Path
    hooks: HookRestore
    redirects: tuple[Redirect, ...]
    missing_pages: int


def sections(pe_bytes: bytes) -> list[Section]:
    pe = struct.unpack_from("<I", pe_bytes, 0x3C)[0]
    if pe_bytes[pe : pe + 4] != b"PE\0\0":
        raise DumpError("no PE header")
    count = struct.unpack_from("<H", pe_bytes, pe + 6)[0]
    table = pe + 24 + struct.unpack_from("<H", pe_bytes, pe + 20)[0]
    out: list[Section] = []
    for i in range(count):
        s = table + 40 * i
        name = pe_bytes[s : s + 8].rstrip(b"\0").decode(errors="replace")
        vsize, va, raw_size, raw_at = struct.unpack_from("<IIII", pe_bytes, s + 8)
        out.append(Section(name, va, vsize, raw_at, raw_size))
    return out


def restore_from_disk(image: bytearray, disk: bytes) -> list[str]:
    """Every section but `.text` back to the file's bytes, the rest of its span zero as loaded."""
    restored: list[str] = []
    for s in sections(disk):
        if s.name == CODE:
            continue
        span = (s.vsize + PAGE - 1) & ~(PAGE - 1)
        if s.va + span > len(image):
            raise DumpError(f"{s.name} of the file on disk does not fit the image; a different executable?")
        data = disk[s.raw_at : s.raw_at + min(s.raw_size, s.vsize)]
        image[s.va : s.va + span] = data + bytes(span - len(data))
        restored.append(s.name)
    return restored


def hook_sites(config: dict[str, Any]) -> list[tuple[int, bytes, str]]:
    """(address, original bytes, type) for every hook in a parsed patch_config.toml."""
    out: list[tuple[int, bytes, str]] = []
    for patch in cast(list[dict[str, Any]], config.get("patches", [])):
        for hook in cast(list[dict[str, Any]], patch.get("hooks", [])):
            out.append((int(hook["address"]), bytes(hook["original_bytes"]), str(hook.get("type", "?"))))
    return out


def restore_hooks(image: bytearray, config: dict[str, Any]) -> HookRestore:
    """Put every hook site back to its `original_bytes`."""
    restored = unchanged = 0
    in_place: list[str] = []
    for address, original, kind in hook_sites(config):
        at = address - IMAGE_BASE
        if not 0 <= at <= len(image) - len(original):
            raise DumpError(f"hook {address:#x} lies outside the image")
        current = bytes(image[at : at + len(original)])
        if current == original:
            unchanged += 1
            continue
        if current[0] not in (0xE8, 0xE9):
            in_place.append(f"{address:#010x} {kind}")
        image[at : at + len(original)] = original
        restored += 1
    return HookRestore(restored, unchanged, tuple(in_place))


def module_regions(regions: list[tuple[int, int, str]], game_folder: str) -> list[tuple[int, int, str]]:
    """The executable mappings a redirect can point into: the DLLs in the game's folder, and the
    anonymous allocations no larger than a cave."""
    return [
        (lo, hi, path)
        for lo, hi, path in regions
        if (path.startswith(game_folder + "/") and path.lower().endswith(".dll"))
        or (not path and hi - lo <= CAVE_LIMIT)
    ]


def redirects(image: bytes, regions: list[tuple[int, int, str]]) -> list[Redirect]:
    """`call rel32` and `jmp rel32` in `.text` whose target is outside the image and inside one of
    the regions. The game's own code reaches other modules only through its import table, so each
    is a candidate for a module's redirect. A scan, not a disassembly: an E8 or E9 byte inside
    another instruction can match too, so these are candidates for the disassembler to confirm."""
    code = next((s for s in sections(image) if s.name == CODE), None)
    if code is None:
        raise DumpError("the image has no .text")
    found: list[Redirect] = []
    end = code.va + code.vsize - 5
    for op, name in ((0xE8, "call"), (0xE9, "jmp")):
        at = image.find(op, code.va, end)
        while at != -1:
            target = (IMAGE_BASE + at + 5 + struct.unpack_from("<i", image, at + 1)[0]) & 0xFFFFFFFF
            if not IMAGE_BASE <= target < IMAGE_BASE + len(image):
                region = next((r for lo, hi, r in regions if lo <= target < hi), None)
                if region is not None:
                    found.append(Redirect(IMAGE_BASE + at, name, target, region or "[anonymous]"))
            at = image.find(op, at + 1, end)
    return sorted(found, key=lambda r: r.at)


def flat_pe(image: bytes) -> bytes:
    """The image as a PE file whose sections sit at their virtual addresses."""
    out = bytearray(image)
    pe = struct.unpack_from("<I", out, 0x3C)[0]
    if bytes(out[pe : pe + 4]) != b"PE\0\0":
        raise DumpError("the image has no PE header at its base")
    optional = pe + 24
    struct.pack_into("<I", out, optional + 36, PAGE)  # FileAlignment = SectionAlignment
    table = optional + struct.unpack_from("<H", out, pe + 20)[0]
    for i, s in enumerate(sections(bytes(out))):
        size = min((s.vsize + PAGE - 1) & ~(PAGE - 1), len(out) - s.va)
        struct.pack_into("<II", out, table + 40 * i + 16, size, s.va)  # SizeOfRawData, PointerToRawData
    return bytes(out)


def ssh(handheld: Handheld, cmd: str) -> bytes:
    r = subprocess.run(["ssh", handheld.ssh, cmd], capture_output=True)
    if r.returncode != 0:
        raise DumpError(f"{cmd}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def dump(handheld: Handheld, dest: Path) -> Dump:
    """Read the running game's image from the handheld into dest/: the flat PE, the inputs it was
    made from (the raw image, the file on disk, patch_config.toml) and a record of what was done."""
    r = subprocess.run(["ssh", handheld.ssh, "python3", "-"], input=REMOTE.encode(), capture_output=True)
    if r.returncode != 0:
        raise DumpError(r.stderr.decode(errors="replace").strip() or f"ssh exited {r.returncode}")
    status = json.loads(r.stderr.decode().strip().splitlines()[-1])
    image = bytearray(r.stdout)
    if len(image) != status["size"]:
        raise DumpError(f"read {len(image)} bytes of a {status['size']}-byte image")
    game = handheld.game_dir  # expanded by the handheld's shell, as the deploy does
    disk = ssh(handheld, f"cat {game}/swkotor.exe")
    config_text = ssh(handheld, f"cat {game}/patch_config.toml").decode()

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "swkotor.image.bin").write_bytes(image)
    (dest / "swkotor.disk.exe").write_bytes(disk)
    (dest / "patch_config.toml").write_text(config_text)
    hooks = restore_hooks(image, tomllib.loads(config_text))
    from_disk = restore_from_disk(image, disk)
    folder = str(status["exe"]).rsplit("/", 1)[0]
    found = redirects(bytes(image), module_regions([(lo, hi, p) for lo, hi, p in status["regions"]], folder))
    exe = dest / "swkotor.unpacked.exe"
    exe.write_bytes(flat_pe(bytes(image)))
    record = dest / "dump.json"
    record.write_text(
        json.dumps(
            {
                "when": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "swkotor.exe on disk": hashlib.sha256(disk).hexdigest(),
                "unpacked": hashlib.sha256(exe.read_bytes()).hexdigest(),
                "missing pages": status["missing_pages"],
                "sections from disk": from_disk,
                "hooks restored": hooks.restored,
                "hooks already original": hooks.unchanged,
                "in-place patches restored": list(hooks.in_place),
                "redirect candidates, not restored": [
                    f"{x.at:#010x} {x.op} {x.target:#010x} {Path(x.region).name}" for x in found
                ],
            },
            indent=1,
        )
        + "\n"
    )
    return Dump(exe, record, hooks, tuple(found), status["missing_pages"])
