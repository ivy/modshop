import struct

import pytest

from modshop.kotor.re import IMAGE_BASE, PAGE, DumpError, flat_pe, restore_hooks


def image_with_sections(*sections: tuple[int, int]) -> bytearray:
    """A mapped PE image: DOS stub pointer, PE header, an optional header of 0xE0 bytes, and a
    section table of (virtual address, virtual size), raw fields as a packed file would have them."""
    size = max(va + vsize for va, vsize in sections)
    size = (size + PAGE - 1) & ~(PAGE - 1)
    img = bytearray(size)
    pe = 0x80
    struct.pack_into("<I", img, 0x3C, pe)
    img[pe : pe + 4] = b"PE\0\0"
    struct.pack_into("<HH", img, pe + 4, 0x14C, len(sections))
    struct.pack_into("<H", img, pe + 20, 0xE0)
    optional = pe + 24
    struct.pack_into("<I", img, optional + 36, 0x200)  # FileAlignment, as on disk
    table = optional + 0xE0
    for i, (va, vsize) in enumerate(sections):
        s = table + 40 * i
        img[s : s + 8] = f".s{i}".encode().ljust(8, b"\0")
        struct.pack_into("<IIII", img, s + 8, vsize, va, 0x10, 0x400 + 0x10 * i)
    return img


def test_flat_pe_puts_sections_at_their_virtual_addresses() -> None:
    img = image_with_sections((0x1000, 0x1234), (0x3000, 0x800))
    out = flat_pe(bytes(img))
    pe = struct.unpack_from("<I", out, 0x3C)[0]
    assert struct.unpack_from("<I", out, pe + 24 + 36)[0] == PAGE
    table = pe + 24 + 0xE0
    assert struct.unpack_from("<II", out, table + 16) == (0x2000, 0x1000)
    assert struct.unpack_from("<II", out, table + 40 + 16) == (0x1000, 0x3000)
    assert len(out) == len(img)


def test_flat_pe_refuses_a_dump_without_a_header() -> None:
    img = image_with_sections((0x1000, 0x10))
    img[0x80:0x84] = b"\0\0\0\0"
    with pytest.raises(DumpError, match="no PE header"):
        flat_pe(bytes(img))


def test_restore_hooks_undoes_detours_and_in_place_patches() -> None:
    img = image_with_sections((0x1000, 0x2000))
    detour, patched, untouched = IMAGE_BASE + 0x1100, IMAGE_BASE + 0x1200, IMAGE_BASE + 0x1300
    img[0x1100:0x1106] = b"\xe9\x00\x00\x00\x00\x90"  # a jump to the handler, the rest NOPed
    img[0x1200:0x1202] = b"\xeb\x09"  # a byte patch: jz turned into jmp
    img[0x1300:0x1302] = b"\x74\x09"
    config: dict[str, object] = {
        "patches": [
            {"hooks": [{"address": detour, "type": "detour", "original_bytes": [0x8B, 0x81, 0x80, 0, 0, 0]}]},
            {
                "hooks": [
                    {"address": patched, "type": "simple", "original_bytes": [0x74, 0x09]},
                    {"address": untouched, "type": "simple", "original_bytes": [0x74, 0x09]},
                ]
            },
        ]
    }
    r = restore_hooks(img, config)
    assert (r.restored, r.unchanged) == (2, 1)
    assert r.in_place == (f"{patched:#010x} simple",)
    assert bytes(img[0x1100:0x1106]) == b"\x8b\x81\x80\x00\x00\x00"
    assert bytes(img[0x1200:0x1202]) == b"\x74\x09"


def test_restore_hooks_rejects_a_site_outside_the_image() -> None:
    img = image_with_sections((0x1000, 0x10))
    config: dict[str, object] = {
        "patches": [{"hooks": [{"address": IMAGE_BASE + 0x100000, "original_bytes": [1]}]}]
    }
    with pytest.raises(DumpError, match="outside the image"):
        restore_hooks(img, config)


def test_restore_from_disk_takes_every_section_but_the_code() -> None:
    from modshop.kotor.re import restore_from_disk

    img = image_with_sections((0x1000, 0x1000), (0x2000, 0x1000))
    disk = bytearray(img)
    pe = 0x80
    table = pe + 24 + 0xE0
    # .s0 stands for the code; rename it so the rule applies, and give the file raw data for .s1
    disk[table : table + 8] = b".text\0\0\0"
    img[table : table + 8] = b".text\0\0\0"
    struct.pack_into("<II", disk, table + 40 + 16, 0x10, 0x3000)  # .s1: 16 raw bytes at 0x3000
    disk += bytes(0x1000)
    disk[0x3000:0x3010] = b"vanilla-constant"
    img[0x1000:0x1004] = b"code"
    img[0x2000:0x2010] = b"runtime-pointers"
    img[0x2010:0x2014] = b"heap"
    assert restore_from_disk(img, bytes(disk)) == [".s1"]
    assert bytes(img[0x2000:0x2010]) == b"vanilla-constant"
    assert bytes(img[0x2010:0x2014]) == bytes(4)  # beyond the raw data: zero, as the loader maps it
    assert bytes(img[0x1000:0x1004]) == b"code"


def test_redirects_are_rel32_branches_into_mapped_memory_outside_the_image() -> None:
    from modshop.kotor.re import redirects

    img = image_with_sections((0x1000, 0x1000))
    pe = 0x80
    img[pe + 24 + 0xE0 : pe + 24 + 0xE0 + 8] = b".text\0\0\0"

    def branch(at: int, op: int, target: int) -> None:
        img[at] = op
        struct.pack_into("<i", img, at + 1, target - (IMAGE_BASE + at + 5))

    branch(0x1010, 0xE8, 0x10001000)  # into a module
    branch(0x1020, 0xE9, 0x20000000)  # into an anonymous cave
    branch(0x1030, 0xE8, IMAGE_BASE + 0x1800)  # inside the image: the game's own call
    branch(0x1040, 0xE8, 0x30000000)  # nowhere mapped: a byte that only looks like a call
    regions = [(0x10000000, 0x10100000, "/g/patches/kmrp.dll"), (0x20000000, 0x20001000, "")]
    found = redirects(bytes(img), regions)
    assert [(r.at - IMAGE_BASE, r.op, r.region) for r in found] == [
        (0x1010, "call", "/g/patches/kmrp.dll"),
        (0x1020, "jmp", "[anonymous]"),
    ]


def test_module_regions_are_game_folder_dlls_and_small_anonymous_allocations() -> None:
    from modshop.kotor.re import CAVE_LIMIT, module_regions

    regions = [
        (0x10000000, 0x10100000, "/g/swkotor/patches/kmrp.dll"),
        (0x20000000, 0x20002000, ""),
        (0x30000000, 0x30000000 + CAVE_LIMIT + 1, ""),
        (0x40000000, 0x40100000, "/usr/lib/libLLVM.so"),
        (0x50000000, 0x50100000, "/g/swkotor/binkw32.dll.so"),
    ]
    assert [r[0] for r in module_regions(regions, "/g/swkotor")] == [0x10000000, 0x20000000]
