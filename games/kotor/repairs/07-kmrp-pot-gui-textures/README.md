# 07: KMRP's 768x768 GUI textures at a power-of-two size

Under Proton on the handheld the game died every time the workbench upgrade screen opened: an abort inside the graphics driver with glibc's "corrupted double-linked list", raised while the game uploaded KMRP's `lbl_wupgradeb2.tga` through `gluBuild2DMipmaps`. That texture is 768x768, so wine's GLU rescales it to 1024x1024 before the driver sees it. With 1024x1024 copies of the two upgrade backgrounds in Override, where they take precedence over KMRP's bank, the screen opened and worked; but so did it afterwards with the originals back, and the difference between the runs that died and the runs that did not is more likely the session's history (both crashes came at the end of play from the Endar Spire into the apartment; every clean run loaded a save inside the apartment). So this repair is a candidate, not a proven fix, until the same route is played both ways. `lbl_custpnl.tga` (character creation's custom panel, the only other 768x768 file in the bank) gets the same treatment; the Feats-screen crashes earlier in this build happened on that screen.

What writes outside its allocation on that path is not proven; the evidence, a Mesa stack under wine's GLU rescaling the 768x768 image to 1024x1024, is in `../../README.md`'s crash notes. Until that is known, this keeps the three files out of the rescaling path.

```bash
data/venv/bin/python repairs/07-kmrp-pot-gui-textures/make.py <dir with the three originals> /path/to/swkotor/Override
```

The originals are KMRP's own: the module extracts them into its run-time bank (`AppData\\Local\\Temp\\KMR*.tmp` in the prefix while the game runs), and the same three files are `assets/override-3440x1440/` in KMRP's repository. SHA-256 of 1.5.1's: `6159a972…052d`, `fca6aca1…d882`, `a0bee0df…7798`. None is kept here.
