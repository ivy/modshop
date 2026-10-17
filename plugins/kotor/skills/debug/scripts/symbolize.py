#!/usr/bin/env python3
"""Turn raw addresses from a 32-bit Wine process into library + function.

    symbolize.py MAPS LIBDIR ADDR...          (or addresses on stdin, one per line)

MAPS is a copy of /proc/<pid>/maps taken while the process ran; LIBDIR holds copies of its
libraries under their absolute paths (copied through /proc/<pid>/root before it exited). Each
address becomes `library +file_offset function+delta`, the function from the library's .symtab,
else its embedded .gnu_debugdata mini symbol table (xz-compressed ELF), else its .dynsym.
Needs readelf, objcopy and xz.
"""

import bisect
import functools
import lzma
import subprocess
import sys
import tempfile
from pathlib import Path


def mappings(path):
    out = []
    for line in Path(path).read_text().splitlines():
        f = line.split(maxsplit=5)
        lo, hi = (int(x, 16) for x in f[0].split("-"))
        out.append((lo, hi, int(f[2], 16), f[5].strip() if len(f) > 5 else ""))
    return out


def readelf(*args):
    return subprocess.run(["readelf", *args], capture_output=True, text=True).stdout


@functools.cache
def symbols(lib):
    """(sorted starts, [(start, size, name)]) for a library's functions, and its PT_LOADs."""
    loads = [
        (int(f[1], 16), int(f[2], 16), int(f[4], 16))
        for f in (row.split() for row in readelf("-lW", lib).splitlines())
        if f and f[0] == "LOAD"
    ]
    sources = [lib]
    with tempfile.TemporaryDirectory() as tmp:
        dd = Path(tmp) / "dd"
        if (
            subprocess.run(
                ["objcopy", "--dump-section", f".gnu_debugdata={dd}", lib, f"{tmp}/out"], capture_output=True
            ).returncode
            == 0
            and dd.exists()
        ):
            (Path(tmp) / "dd.elf").write_bytes(lzma.decompress(dd.read_bytes()))
            sources.append(str(Path(tmp) / "dd.elf"))
        funcs = []
        for src in sources:
            for f in (row.split() for row in readelf("-sW", src).splitlines()):
                if len(f) >= 8 and f[3] == "FUNC" and int(f[1], 16):
                    funcs.append((int(f[1], 16), int(f[2], 0), f[7]))
    funcs = sorted(set(funcs))
    return [a for a, _, _ in funcs], funcs, loads


def main():
    maps, libdir, *addrs = sys.argv[1:]
    addrs = addrs or [arg.strip() for arg in sys.stdin if arg.strip()]
    table = mappings(maps)
    for text in addrs:
        a = int(text, 16)
        hit = next(((lo, off, p) for lo, hi, off, p in table if lo <= a < hi), None)
        if not hit or not hit[2].startswith("/"):
            print(f"{a:#010x}  {hit[2] if hit else '?'}")
            continue
        off = a - hit[0] + hit[1]
        lib = Path(libdir + hit[2])
        name = Path(hit[2]).name
        if not lib.exists():
            print(f"{a:#010x}  {name} +{off:#x}  (no copy in LIBDIR)")
            continue
        starts, funcs, loads = symbols(str(lib))
        seg = next(((po, pv) for po, pv, sz in loads if po <= off < po + sz), None)
        va = off - seg[0] + seg[1] if seg else off
        i = bisect.bisect_right(starts, va) - 1
        fn = (
            f"{funcs[i][2]}+{va - funcs[i][0]:#x}"
            if i >= 0 and va < funcs[i][0] + max(funcs[i][1], 1)
            else ""
        )
        print(f"{a:#010x}  {name} +{off:#x}  {fn}")


if __name__ == "__main__":
    main()
