# The engine's own code

When the answer is in `swkotor.exe` rather than in the game's files: which function decides something, what a crash address is, where to hook.

## Getting code you can read

- **Steam's `swkotor.exe` is SteamStub-wrapped**: `.text` has entropy 8.0 and there is a `.bind` section. Nothing disassembles from the file on disk. The code is decrypted in memory at start-up, so it comes out of the running process (modshop: `modshop kotor re dump`, reference implementation `src/modshop/kotor/re.py` in modshop).
- **What the dump has to undo.** The running image carries KPM's patches: every hook in the game folder's `patch_config.toml` lists `address` and `original_bytes`; put them back (detours are `E8`/`E9` jumps; `simple` hooks are in-place byte patches, five of them in KMRP 1.5.1's configuration). Every section but `.text` is unencrypted on disk, so take those from the file: vanilla constants, and an import table a disassembler can name. Then rewrite the section table so each section's file offset equals its virtual address (`PointerToRawData = VirtualAddress`, `FileAlignment = 0x1000`).
- **What it can't undo.** KMRP's modules also redirect calls at run time without a `patch_config.toml` entry: `call`/`jmp rel32` whose target is outside the image, into a small anonymous executable allocation (KPM's caves, around `0x0316xxxx`) or a game-folder DLL. Two dumps from different sessions differ exactly there, because the targets move. Treat any address near one as suspect.
- **Which process**: see [`evidence.md`](evidence.md); select by the `00400000-…swkotor.exe` mapping and read `0x400000` to `0x400000 + SizeOfImage` (`0x8C3000`) from `/proc/<pid>/mem`.

## Reading it

- **Ghidra (through REA) opens the dump as it is**, but leaves undefined any function reached only through a handler pointer (`0x0068B050`), and some it should know (the transition handler at `0x0058B850` resolved as "not in procedure"). Fall back to capstone over the bytes: disassemble from the padding (`CC`/`90` runs) before an address to find its function's start.
- **Read x87 code as instructions.** Ghidra's decompiler put the minigame input block's operands in the wrong places; the listing was right.
- **Calls through the import table** are `call dword ptr [IAT]` or a register loaded from it. Finding no reference to an import slot (`gluBuild2DMipmaps` at `0x0073D030` has none in `.text`) is a finding, not a search failure: the call is indirect or redirected.
- **Engine strings name scripts the engine runs** (`k_trg_transfail` at `0x007499C4`): when a chain of resource references ends, search the executable's strings, then their cross-references.

## Names come from KMRP

KMRP's source names several hundred engine addresses as `constexpr std::uintptr_t K1_* = 0x…` with a comment saying what each is (`src/controller-native/*.cpp`), its `kotor1*.hooks.toml` names every hooked site, and `reverse-engineering/*.md` records how each was found. Grep them before reading disassembly cold; a small value is a field offset, an address is between `0x401000` and `0x8C3000`.

Established here:

| Address | What |
|---|---|
| `0x006227E0` | `ProcessInput`; `PollInput(event, input_class)` at `0x005DF4D0` |
| `0x005DF460` / `0x005DF470` | `CreateNewEvent` / `AddEvent` wrappers; `SetEventDescriptions` registers ids `0x01`–`0x0D`, `0x17`–`0x19` |
| `0x00621210` | the action router: event id → handler (`0x19`, `0xD9` → the minigame player's fire, `0x0066DC50`) |
| `0x00670FB0` | `CSWMiniGame`'s input step (`+0x80` type: 1 swoop, 2 turret); `0x006710E0` the swoop's lateral state |
| `0x007A39F4` | the GUI manager pointer: panels at `+0x88`, count at `+0x8C` |
| `0x00753F50` | `CSWGuiMainInterface`'s vtable; BTN_CLEARONE at `+0x6CD0` (flags `+0x44`, bit 2 = drawn) |
| `0x0068B050` → `0x006880C0` | `OnClearOneButtonPressed` → `OnCombatYButton` (pops the last queued combat action, else clears all) |
| `0x0058B850`, `0x00635350` | the area transition handler; the party check (every member within 30 m, `900.0` = 30², of the leader) |

## KPM hooks (KMRP's patch manager)

- **A stack parameter arrives as the address of its slot.** `source = "esp+4"` hands the handler a pointer to the stack slot, so a pointer argument arrives as `T**`. Registers arrive as values.
- **The wrapper's order**: call the handler, restore every register not in `exclude_from_restore`, run the stolen bytes, then test EAX for `consumed_exit_address`. Stolen bytes must be position-independent unless `skip_original_bytes` is true; KMRP's `tools/check_hook_stolen_bytes.py` checks it.
