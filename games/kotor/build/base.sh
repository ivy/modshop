#!/usr/bin/env bash
# The vanilla game, downloaded from Steam by depot manifest id into data/game/vanilla/tree with
# DepotDownloader (SteamRE's open-source Steam client, installed by mise from the repository's
# mise.toml). The ids are in base.json: the app, its Windows depot and the exact manifest, so
# the base is a definition and not a copy of some install.
#
# First run: Steam asks for the account's password and a Steam Guard code on the terminal, so
# run it from an interactive shell. With -remember-password the login state is kept under
# ~/.config/DepotDownloader, outside the repository and data/; nothing else reads it.
#
#   build/base.sh <steam account>     then     build/build.py base
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
data="${KOTOR_DATA:-$here/../data}"
account="${1:?usage: base.sh <steam account>}"
read -r app depot manifest < <(python3 -c 'import json,sys; b=json.load(open(sys.argv[1])); print(b["app"], b["depot"], b["manifest"])' "$here/base.json")
out="$data/game/vanilla"
rm -rf "$out/tree.partial"
mkdir -p "$out/tree.partial"
DepotDownloader -app "$app" -depot "$depot" -manifest "$manifest" -os windows -osarch 32 \
	-username "$account" -remember-password -dir "$out/tree.partial" -validate
# DepotDownloader keeps its own bookkeeping beside the files; the tree is the game alone
rm -rf "$out/tree.partial/.DepotDownloader"
rm -rf "$out/tree"
mv "$out/tree.partial" "$out/tree"
printf '{"app": %s, "depot": %s, "manifest": "%s"}\n' "$app" "$depot" "$manifest" > "$out/source.json"
echo "vanilla tree at $out/tree ($(find "$out/tree" -type f | wc -l) files); now: build/build.py base"
