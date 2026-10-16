#!/usr/bin/env python3
"""Stop the game minimising itself when it loses activation, as a KPM byte patch.

The game window's WM_ACTIVATEAPP case minimises the window in fullscreen
(`push 6; push ecx; call [ShowWindow]` at 0x004029D8). Under Proton in Game Mode
nothing restores it and SwapBuffers then waits forever: the black screen after the
logo movies. This adds a `simple` hook to the `kmrp` block of patch_config.toml that
replaces those nine bytes with NOPs, so KPM writes them at start-up. The gamma and
mode restore after the call still run.

    make.py <game dir>

KMRP patch 0006 (../../patches/kmrp/) makes the same change as a core hook at
0x004029D2, Wine-only; once KMRP's own module carries that hook this repair finds it
and does nothing. Runs with the build host's python3 (tomllib only).
"""
import pathlib
import sys
import tomllib

SITE = 0x004029D8
ORIGINAL = [0x6A, 0x06, 0x51, 0xFF, 0x15, 0x00, 0xD4, 0x73, 0x00]
FUNCTION = 0x004029D2, 0x004029E1  # the span KMRP's own hook stands in for
KMRP_HANDLER = "KeepWindowOnDeactivateK1"

HOOK = (
    "[[patches.hooks]]\n"
    f"address = 0x{SITE:08X}\n"
    'type = "simple"\n'
    f"original_bytes = [{', '.join(f'0x{b:02X}' for b in ORIGINAL)}]\n"
    f"replacement_bytes = [{', '.join(['0x90'] * len(ORIGINAL))}]\n"
)


def main() -> None:
    config = pathlib.Path(sys.argv[1]) / "patch_config.toml"
    text = config.read_text()
    patches = tomllib.loads(text)["patches"]
    for patch in patches:
        for hook in patch.get("hooks", []):
            start = hook["address"]
            end = start + len(hook.get("original_bytes", [])) - 1
            if end < FUNCTION[0] or start > FUNCTION[1]:
                continue
            if hook.get("function") == KMRP_HANDLER:
                print(f"{patch['id']} hooks 0x{start:08X} with {KMRP_HANDLER}: nothing to do")
                return
            if start == SITE and hook.get("replacement_bytes") == [0x90] * len(ORIGINAL):
                print(f"{patch['id']} already has this repair's hook at 0x{SITE:08X}")
                return
            raise SystemExit(f"{patch['id']} already has a hook at 0x{start:08X}; refusing to add another")

    blocks = text.split("[[patches]]")
    for i, block in enumerate(blocks):
        if 'id = "kmrp"\n' in block:
            blocks[i] = block.rstrip("\n") + "\n\n" + HOOK + "\n"
            break
    else:
        raise SystemExit("no kmrp block in patch_config.toml")
    new_text = "[[patches]]".join(blocks)
    tomllib.loads(new_text)
    config.write_text(new_text)
    print(f"kmrp: simple hook at 0x{SITE:08X}, ShowWindow(SW_MINIMIZE) replaced with NOPs")


if __name__ == "__main__":
    main()
