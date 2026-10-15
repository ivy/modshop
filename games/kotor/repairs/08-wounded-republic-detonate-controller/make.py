#!/usr/bin/env python3
"""Drop the detonate controller from the clinic room's bubble emitters.

The Diversified Wounded Republic Soldiers mod rebuilds Upper City South's clinic
room (m02ac_02h) with seven kolto-tank bubble emitters. Each carries a `detonate`
controller (type 502), which none of the game's own bubble emitters has, and
under Proton the room ended the game on its first frame in view, in the emitter
render path. The controller is the last key of each node's controller array, so
the node's two controller counts go from 50 to 49 and nothing else moves.

    make.py <Override dir> [<mod archive>]

The input is extracted from the mod's own archive (the one download.py left
under data/archives/157-diversified-republic-soldiers/, or the path given),
never kept in this repository.
"""
import os
import pathlib
import re
import struct
import subprocess
import sys
import tempfile

ARCHIVE_DIR = "157-diversified-republic-soldiers"
MEMBER = "[K1]_Diversified_Wounded_Republic_Soldiers_On_Taris_v1.4/tslpatchdata/m02ac_02h.mdl"


def extract_input() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve().parent
    data = pathlib.Path(os.environ.get("KOTOR_DATA", here.parent.parent / "data"))
    if len(sys.argv) > 2:
        archive = pathlib.Path(sys.argv[2])
    else:
        archives = sorted((data / "archives" / ARCHIVE_DIR).glob("*.7z"))
        if not archives:
            raise SystemExit(f"no archive under {data / 'archives' / ARCHIVE_DIR}; pass it as the second argument")
        archive = archives[0]
    out = pathlib.Path(tempfile.mkdtemp(prefix="wounded-republic-"))
    subprocess.run(["7zz", "e", "-y", f"-o{out}", str(archive), MEMBER], check=True, capture_output=True)
    return out / "m02ac_02h.mdl"

DETONATE = 502
NODE_HEADER = 0x50          # the node header precedes the emitter header
EMITTER_TEXTURE = 0x80      # offset of the texture name inside the emitter header
CONTROLLER_COUNTS = 60      # offset of the controller key array's two counts in the node header


def main() -> None:
    override = pathlib.Path(sys.argv[1])
    src = extract_input()
    data = bytearray(src.read_bytes())
    patched = 0
    for m in re.finditer(rb"fx_bubble", data):
        node = m.start() - EMITTER_TEXTURE - NODE_HEADER
        key_offset, count, allocated = struct.unpack_from("<III", data, node + 56)
        last_type = struct.unpack_from("<I", data, 12 + key_offset + 16 * (count - 1))[0]
        if last_type != DETONATE:
            if DETONATE in (struct.unpack_from("<I", data, 12 + key_offset + 16 * i)[0] for i in range(count)):
                raise SystemExit(f"detonate is not the last controller of the node at {node:#x}")
            continue
        struct.pack_into("<II", data, node + CONTROLLER_COUNTS, count - 1, count - 1)
        patched += 1
    (override / "m02ac_02h.mdl").write_bytes(bytes(data))
    print(f"m02ac_02h.mdl: detonate controller dropped from {patched} emitters")


if __name__ == "__main__":
    main()
