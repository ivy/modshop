#!/usr/bin/env python3
"""Drop the two baseitems.2da rows in JC's Blaster Adjustment's pistol_rifle.ini that name
sections the file does not have.

    make.py <stage directory of the mod>

The "Blaster Pistol & Blaster Rifle + Critical" option's change file lists ChangeRow12=
repeating_blaster and ChangeRow13=heavy_repeating_blaster under [baseitems.2da], but only
full.ini defines those two sections; TSLPatcher on Windows skips a row whose section is
missing, HoloPatcher refuses the whole install. The two rows are removed; the other twelve
are what the option is for.
"""
import pathlib, sys

ORPHANS = (b'ChangeRow12=repeating_blaster', b'ChangeRow13=heavy_repeating_blaster')


def main() -> None:
    stage = pathlib.Path(sys.argv[1])
    hits = [p for p in stage.rglob('pistol_rifle.ini') if 'tslpatchdata' in str(p).lower()]
    if len(hits) != 1:
        sys.exit(f'expected one pistol_rifle.ini under {stage}, found {len(hits)}')
    ini = hits[0]
    lines = ini.read_bytes().splitlines(keepends=True)
    kept = [l for l in lines if not l.strip().startswith(ORPHANS)]
    if len(lines) - len(kept) != 2:
        sys.exit(f'{ini}: expected to drop 2 rows, would drop {len(lines) - len(kept)}')
    ini.write_bytes(b''.join(kept))
    print(f'{ini.relative_to(stage)}: dropped {len(lines) - len(kept)} orphan rows')


if __name__ == '__main__':
    main()
