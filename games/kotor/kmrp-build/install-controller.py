#!/usr/bin/env python3
"""Install a built kmrp-controller.dll into a KPM-edition KMRP game folder.

    install-controller.py <game dir> <kmrp-controller.dll> <kmrp-controller.hooks.toml>

Replaces patches/kmrp-controller.dll, the hooks of the `kmrp-controller` block in
patch_config.toml (the block's own `id` and `dll` lines stay), and the SHA-256 in
KMRP_KPM.manifest's row for the DLL, so KMRP's Restore Original still knows the
file. The previous DLL, config and manifest are kept beside the live ones with a
`.prev` suffix. The game must not be running. Runs on the device with its own
python3 (tomllib only).
"""
import hashlib
import pathlib
import shutil
import sys
import tomllib


def main() -> None:
    game, dll, hooks = (pathlib.Path(a) for a in sys.argv[1:4])
    target = game / "patches" / "kmrp-controller.dll"
    config = game / "patch_config.toml"
    manifest = game / "KMRP_KPM.manifest"
    for p in (target, config, manifest, dll, hooks):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    # patch_config.toml: swap the controller block's hooks for the generated list.
    text = config.read_text()
    blocks = text.split("[[patches]]")
    for i, block in enumerate(blocks):
        if 'id = "kmrp-controller"' not in block:
            continue
        head = []
        for line in block.splitlines():
            head.append(line)
            if line.startswith("dll = "):
                break
        blocks[i] = "\n".join(head) + "\n\n" + hooks.read_text().strip() + "\n\n"
        break
    else:
        raise SystemExit("no kmrp-controller block in patch_config.toml")
    new_text = "[[patches]]".join(blocks)
    parsed = tomllib.loads(new_text)
    controller = [p for p in parsed["patches"] if p.get("id") == "kmrp-controller"]
    print(f"patch_config.toml: {len(parsed['patches'])} patches, controller hooks {len(controller[0].get('hooks', []))}")

    # KMRP_KPM.manifest: the hash column of the DLL's row (tab-separated).
    digest = hashlib.sha256(dll.read_bytes()).hexdigest().upper()
    rows = manifest.read_text().splitlines(keepends=True)
    hit = 0
    for i, row in enumerate(rows):
        cols = row.rstrip("\r\n").split("\t")
        if any(c.lower() == "patches\\kmrp-controller.dll" for c in cols):
            old = [c for c in cols if len(c) == 64 and all(ch in "0123456789ABCDEFabcdef" for ch in c)]
            if len(old) != 1:
                raise SystemExit(f"manifest row has {len(old)} hash columns: {row!r}")
            rows[i] = row.replace(old[0], digest)
            hit += 1
    if hit != 1:
        raise SystemExit(f"manifest rows for the DLL: {hit}")
    print(f"KMRP_KPM.manifest: hash set to {digest[:12]}…")

    for live in (target, config, manifest):
        shutil.copy2(live, live.with_name(live.name + ".prev"))
    shutil.copy2(dll, target)
    config.write_text(new_text)
    manifest.write_text("".join(rows))
    print("installed")


if __name__ == "__main__":
    main()
