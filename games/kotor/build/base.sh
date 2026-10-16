#!/usr/bin/env bash
# The vanilla game, downloaded from Steam by depot manifest id into data/game/vanilla/tree,
# with steamcmd running in a container. The ids are in base.json: the app, its Windows depot
# and the exact manifest, so the base is a definition and not a copy of some install.
#
# First run: steamcmd asks for the account's password and a Steam Guard code on the terminal,
# so run it from an interactive shell. Its login state persists in the podman volume named
# below, outside the repository and data/; nothing else in the pipeline touches that volume.
#
#   build/base.sh <steam account>     then     build/build.py base
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
data="${KOTOR_DATA:-$here/../data}"
account="${1:?usage: base.sh <steam account>}"
image="docker.io/steamcmd/steamcmd:latest"
volume="modshop-steamcmd"
read -r app depot manifest < <(python3 -c 'import json,sys; b=json.load(open(sys.argv[1])); print(b["app"], b["depot"], b["manifest"])' "$here/base.json")
out="$data/game/vanilla"
mkdir -p "$out"
# download_depot writes under the container's Steam directory; the volume holds it between runs
podman run --rm -it --volume "$volume:/root/Steam" "$image" \
	+@sSteamCmdForcePlatformType windows \
	+login "$account" \
	+download_depot "$app" "$depot" "$manifest" \
	+quit
# copy the depot out of the volume into vanilla/tree, then drop it from the volume
podman run --rm --volume "$volume:/root/Steam" --volume "$out:/out" "$image" \
	bash -c "set -e; src=/root/Steam/steamapps/content/app_$app/depot_$depot; test -d \"\$src\"; rm -rf /out/tree; cp -a \"\$src\" /out/tree; rm -rf \"\$src\"" >/dev/null
printf '{"app": %s, "depot": %s, "manifest": "%s"}\n' "$app" "$depot" "$manifest" > "$out/source.json"
echo "vanilla tree at $out/tree ($(find "$out/tree" -type f | wc -l) files); now: build/build.py base"
