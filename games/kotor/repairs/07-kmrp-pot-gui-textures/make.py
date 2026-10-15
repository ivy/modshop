#!/usr/bin/env python3
"""Resample KMRP's three 768x768 GUI textures to 1024x1024 for the game's Override folder.

KMRP serves these from its asset bank at run time; a copy in Override takes
precedence. Needs Pillow (the patcher venv has it).

    make.py <bank dir with the originals> <Override dir>
"""
import pathlib
import struct
import sys

from PIL import Image

NAMES = ("lbl_custpnl.tga", "lbl_wupgradeb1.tga", "lbl_wupgradeb2.tga")
SIDE = 1024
HEADER = struct.Struct("<BBBHHBHHHHBB")


def resample(src: pathlib.Path, dst: pathlib.Path) -> None:
    data = src.read_bytes()
    idlen, cmap, kind, _, _, _, _, _, w, h, bpp, desc = HEADER.unpack(data[: HEADER.size])
    if kind != 2 or bpp != 32 or idlen or cmap:
        raise SystemExit(f"{src.name}: expected an uncompressed 32-bit TGA, got type {kind} {bpp}bpp")
    pixels = data[HEADER.size : HEADER.size + w * h * 4]
    trailer = data[HEADER.size + w * h * 4 :]
    # The channel order is irrelevant to resampling, so the raw BGRA rows go in as RGBA.
    image = Image.frombytes("RGBA", (w, h), pixels).resize((SIDE, SIDE), Image.LANCZOS)
    dst.write_bytes(HEADER.pack(0, 0, 2, 0, 0, 0, 0, 0, SIDE, SIDE, 32, desc) + image.tobytes() + trailer)
    print(f"{src.name}: {w}x{h} -> {SIDE}x{SIDE}")


def main() -> None:
    bank, override = (pathlib.Path(a) for a in sys.argv[1:3])
    for name in NAMES:
        resample(bank / name, override / name)


if __name__ == "__main__":
    main()
