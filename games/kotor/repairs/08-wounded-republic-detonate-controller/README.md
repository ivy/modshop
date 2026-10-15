# 08: the clinic room's bubble emitters without their detonate controller

Entering Upper City South from Upper City North ended the game under Proton on the area's first frame, every time, at `0x0048DCBD` in the game's emitter render path (a float read through a parent pointer of `0x80`); entering from the apartment side never did. The clinic room, `m02ac_02h`, is the first thing in view from the north door and is the room the Diversified Wounded Republic Soldiers mod (DeadlyStream file 1179) rebuilds, with seven kolto-tank bubble emitters (`MA2_Bubbles` and the rest) the vanilla room does not have. With the mod's room set aside the door was safe; with it back, it was not.

What differs from the game's own 54 bubble emitters (`m28ab_03a` and its siblings): the mod's carry emitter flags 266 (p2p_sel, tinted, inherit_local) against the game's 2, and a `detonate` controller (type 502, one row, value 0) that none of the game's bubble emitters has. Tested one at a time on the device, 2026-10-15: the flags set to 2 still crashed; the detonate controller dropped, flags as the mod had them, did not. So `make.py` drops the controller and nothing else. It is the last key of each node's controller array, so the fix is the node's two controller counts, 50 to 49, two bytes per emitter; the key and its row stay in the file, unread.

The input is the mod's own `m02ac_02h.mdl`, extracted from its archive at run time (SHA-256 of the v1.4 file in `SHA256SUMS`); nothing of the mod is kept here. `m02ac_02h.mdx` and `.wok` stay the mod's, as the build installed them.

```bash
python3 repairs/08-wounded-republic-detonate-controller/make.py /path/to/swkotor/Override   # or: make.py <Override> <archive.7z>
```
