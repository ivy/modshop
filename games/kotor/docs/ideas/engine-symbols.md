---
title: Engine symbols and disassembly helpers
priority: p1
status: idea
depends_on: []
---

# Engine symbols and disassembly helpers

A named, saved analysis of the decrypted executable, so every reverse-engineering session starts from what is already known instead of from addresses found by grepping, plus the handful of disassembly questions that keep being answered by throwaway scripts.

## The problem

`modshop kotor re dump` gives a PE that REA and Ghidra open as it is, but the analysis it produces knows nothing:

- **Functions found by grepping someone else's comments.** On 2026-10-15/16 every engine function used came from searching KMRP's source and reverse-engineering notes for an address: `ProcessInput` (`0x006227E0`), the action router (`0x00621210`), `CSWGuiMainInterface`'s combat buttons (`0x0068B050`, `0x0068B0A0`), the GUI manager (`0x007A39F4`), the movement controller (`0x00679940`). KMRP's source alone names several hundred addresses as `constexpr std::uintptr_t K1_* = 0x…` with a comment saying what each is, and its hook lists name every hooked site; none of it reaches the disassembler.
- **Functions Ghidra never defines.** A function reached only through a handler pointer has no procedure: decompiling `OnClearOneButtonPressed` at `0x0068B050` failed with "no loaded source mapping", and both references to `k_trg_transfail` (`0x0058C31A`, `0x0058F47C`) resolved to "not_in_procedure", inside the area transition handler at `0x0058B850`. Each time the fallback was capstone over raw bytes.
- **The same helpers written again.** Disassembling a range (`dis.py`), finding a function's start from the padding before it (`func.py`), and listing every call to a function with the immediates pushed before it (`callargs.py`) were each written in a scratch directory and lost. `callargs.py` is how the class-1 registration of event `0x19` (the left mouse button, the minigame's fire) was found.
- **Analysis that does not persist.** Each REA session re-runs Ghidra's auto-analysis (75 s on this executable) and drops any names given in the previous one.
- **x87 code the decompiler muddles.** The minigame input block (`0x00623F48`) decompiled with its operands in the wrong places; the instruction listing was right. The decompiler is a first look, not the answer, for floating-point code.

## The idea

- **A symbol table, built.** `modshop kotor re symbols` reads KMRP's `K1_*` address constants with their comments, its `kotor1*.hooks.toml` (address and handler name), and a hand-kept `games/kotor/re/symbols.toml` for what this repository finds (the transition handler, the party distance check `0x00635350`, the minigame input step `0x00670FB0`), and writes `data/re/symbols.json`: address, name, kind (function, global, handler, hook site), source.
- **A named analysis, saved.** The command opens the dump in REA, forces a function at every function-kind symbol, names everything (`set_addresses_names`), and saves an analysis snapshot under `data/re/` keyed by the unpacked executable's hash. A session opens the snapshot instead of analysing from scratch; a new dump with a new hash rebuilds it.
- **The helpers as subcommands.** `re dis ADDR [LEN]`, `re func ADDR` (the containing function, from Ghidra when it has one and from padding when it does not), and `re calls TARGET` (call sites with their pushed immediates). Capstone is already a locked dependency in the `kmrp-build` group; the checkpoint key takes only the patcher's closure of `uv.lock`, so a group for these changes no key.
- **Redirect candidates as bookmarks.** `dump.json`'s module-redirect candidates become bookmarks, so an address near one is visibly suspect in the disassembler.

## Unknowns

- How well KMRP's comments name functions, as opposed to describing them; a constant called `K1_ON_CLEAR_ONE` is a good name, one called `K1_HUD_CLEAR_ONE` is a field offset, and the kinds have to be told apart (an offset is small, an address is in the image).
- Whether REA's snapshot import keeps forced functions and names across sessions as its documentation says; one round trip settles it.
- Licensing: KMRP's names are derived from its source; using them locally is fine, publishing a derived symbol file would need checking.

## First step

`re symbols` over KMRP's `K1_*` constants only, then open the dump and confirm `0x0068B050` decompiles as a named function.
