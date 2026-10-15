#!/usr/bin/env bash
# The patcher the build runs with: HoloPatcher 1.5.3 on pykotor 2.3.12, plus the
# fixes in ../patches/pykotor/, in a venv at $1 (default: data/venv). Needs a
# Python with tkinter (HoloPatcher imports it even headless); Bazzite's has none,
# which is why the build runs on another machine.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
data="${KOTOR_DATA:-$here/../data}"
venv="${1:-$data/venv}"
python3 -m venv "$venv"
"$venv/bin/pip" install --quiet holopatcher==1.5.3
# The series is on OpenKotOR/PyKotor master (base ca61ce8d5), with paths
# Libraries/PyKotor/src/pykotor/...: four leading components to the package.
for p in "$here"/../patches/pykotor/*.patch; do
    patch --directory "$venv"/lib/python3.*/site-packages --strip 4 --forward --silent < "$p"
done
"$venv/bin/python" -c 'import pykotor.tslpatcher.reader as r, pykotor.resource.formats.twoda.io_twoda as t; print("patched pykotor ready")'
