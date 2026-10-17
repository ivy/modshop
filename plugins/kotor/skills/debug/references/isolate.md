# Narrowing a crash without a stack

What can be learned before, or instead of, a reproduction under a debugger. Each step should end in "established" or "not established", with the evidence.

## Does it follow a place?

- Count reproductions and session lengths. Two crashes at the same screen after 90 and 23 minutes follow the screen; crashes only late in long sessions point at accumulated state, and a fresh load at the same place is the test.
- Ask the player what is on screen at the moment, in their words: "the special animation for building the first lightsaber" named a one-off scene that the logs never mention.

## What does that place load?

- **The scripts.** Module scripts behind a scene (`k_pdan_*` in the Dantooine Enclave, `danm13`) can be listed and their string constants read without a decompiler ([`/kotor:pykotor`](../../pykotor/README.md), `scripts.md`); compare each with the vanilla copy to see whether any mod changed it.
- **Which mods touched it.** A build that records what each mod changed answers "who put this file here" directly (modshop: each checkpoint's `changed.txt`, `+`/`~`/`-` per path, walked in recipe order). A `.mod` in `modules/` replaces that module's `.rim` and `_s.rim` wholesale; the Community Patch creates many and later mods edit them.
- **Assets that only load there.** Models, textures and effects a scene uses that nothing else does. For textures, check sizes: non-power-of-two sides go through a rescale on some paths (a 768x768 TGA becomes 1024x1024 in `gluBuild2DMipmaps`). Header offsets: TGA width/height at bytes 12/14, TPC at 8/10 (4..7 is a float; reading there gives nonsense), DDS height/width at 12/16. DXT-compressed TPCs at non-power-of-two sizes (KMRP's 2868x1436 menu backgrounds) load on screens players open constantly, so size alone does not convict.
- **KMRP's run-time files**, not its repository's: KMRP renders its interface for the current resolution into the prefix's `AppData/Local/Temp/KMR*.tmp/` ([`evidence.md`](evidence.md)).

## Clearing a suspect in third-party code

A library that can be built from source can be tested off the device with the game's inputs. Wine's GLU (`dlls/glu32/mipmap.c` from `ValveSoftware/wine`, branch `proton_11.0`) built natively in a container with AddressSanitizer, its GL calls stubbed (`glTexImage2D` reading every byte a driver would read, honouring the unpack state), shims for `WINAPI`, `HeapAlloc` and `wglGetCurrentContext`: 768x768 and 2868x1436 in RGB/BGR/RGBA/BGRA at alignments 1 and 4 showed no out-of-bounds access, which cleared GLU. Check that the harness exercised the path (print the uploaded level-0 size) and delete the old binary before a rebuild, so a failed compile can't pass for a result.

## A/B on the device

- **With and without a suspect change**, along the same route from the same save: the only result that turns a candidate fix into a yes or a no.
- **Software rendering** (`LIBGL_ALWAYS_SOFTWARE=1` in the launch options) would separate a radeonsi bug from everything else; untested for KotOR here, and slow.
- Don't set `glibc.malloc.mmap_threshold=0` through Proton's environment to catch an overrun: the prefix's `explorer.exe` never finishes starting with it.
