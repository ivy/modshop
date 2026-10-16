# 09: JC's Blaster Adjustment, two orphan rows in `pistol_rifle.ini`

**What breaks.** The "Blaster Pistol & Blaster Rifle + Critical" option of JC's Blaster Adjustment 1.0.0 (the option the Full Build calls for alongside Multifire and Autofire's third option) ships a `pistol_rifle.ini` whose `[baseitems.2da]` list ends with `ChangeRow12=repeating_blaster` and `ChangeRow13=heavy_repeating_blaster`, two rows copied from `full.ini` whose `[repeating_blaster]` and `[heavy_repeating_blaster]` sections `pistol_rifle.ini` does not have. TSLPatcher on Windows skips such a row; HoloPatcher raises `KeyError` and installs nothing.

**The repair.** `make.py <stage>` removes the two lines from the staged copy of the file before the patcher runs, checking that exactly two lines go. The twelve remaining rows are the option's content. The mod's archive is untouched.

**Evidence.** The error, verbatim from the patcher's log: `KeyError: "The [repeating_blaster] section was not found in the ini, referenced by 'ChangeRow12=repeating_blaster' in [baseitems.2da]"`. `full.ini` in the same archive defines both sections at lines 150 and 157; `pistol_rifle.ini` and `pistol.ini` define neither.
