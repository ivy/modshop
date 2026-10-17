# Scripts: NSS source and NCS bytecode

NSS is NWScript source; NCS is the compiled bytecode the engine runs. pykotor reads and writes NCS, disassembles it, and compiles NSS with a built-in compiler. It does not decompile (see Traps). Paths below are relative to the `pykotor` package.

```python
import logging

logging.disable(logging.CRITICAL)  # pykotor logs heavily; it also writes logs/ into the cwd
from pykotor.extract.installation import Installation
from pykotor.resource.type import ResourceType
from pykotor.resource.formats.ncs import read_ncs, compile_nss, bytes_ncs
from pykotor.common.misc import Game

inst = Installation(game_dir)
src = inst.resource("k_trg_transfail", ResourceType.NSS).data.decode(
    "windows-1252"
)  # global script: source ships in scripts.bif
ncs = read_ncs(
    inst.resource("k_pdan_saber01", ResourceType.NCS).data
)  # module script: from modules/danm13_s.rim
print(ncs)  # full listing, jumps shown as target indexes
new = compile_nss(src, Game.K1)  # -> NCS; bytes(bytes_ncs(new)) for the file
```

## Where scripts are

- `inst.resource(name, ResourceType.NSS)` returns a `ResourceResult` (`.data`, `.filepath`, `.resname`, `.restype`) or `None`. Vanilla K1 ships 1,774 NSS in `chitin.key`/`data/scripts.bif`, the global scripts and the `k_inc_*` includes; 1,754 of them have a matching NCS there.
- Module scripts (everything in `modules/*.rim`) ship as NCS only: the vanilla module capsules hold no NSS at all. `inst.resource` finds them in the module capsules.
- NCS counts: vanilla K1 holds about 12,600 (1,784 in chitin, the rest in module capsules); a heavily modded build about 23,800, counting a resource once per capsule that holds it (a `.mod` built from its `.rim`s repeats them).

## Read, write, disassemble

- `read_ncs(source)` takes bytes, a path or a stream; `write_ncs(ncs, target)`; `bytes_ncs(ncs)` returns a `bytearray`.
- `NCS.instructions` is a list of `NCSInstruction` (`resource/formats/ncs/ncs_data.py`): `.ins_type` (an `NCSInstructionType`), `.args` (list), `.jump` (the target `NCSInstruction` for `JMP`/`JSR`/`JZ`/`JNZ`, else `None`), `.offset` (byte offset; set by `read_ncs`, `-1` on freshly compiled code).
- `ins_type.value` is `NCSInstructionTypeValue(byte_code, qualifier)`: `NCSByteCode` is the opcode (`CPDOWNSP`=0x01 … `STORE_STATE`=0x2C), `NCSInstructionQualifier` the operand types (`Int`=0x03, `Float`=0x04, `String`=0x05, `Object`=0x06, `IntInt`=0x20, `IntFloat`=0x25, `FloatInt`=0x26, …). Type names fuse the two: `CONSTI`, `ADDIF`, `RSADDO`.
- `ACTION` args are `[routine_id, arg_count]`; `routine_id` indexes `pykotor.common.scriptdefs.KOTOR_FUNCTIONS` (K1) or `TSL_FUNCTIONS` (K2).
- `str(ncs)` lists every instruction with jump targets as indexes. `NCS.print()`, `NCSInstruction.__str__` and `pykotor.tools.scripts.disassemble_ncs` print jump targets as Python object ids, which are useless. For offsets, raw opcodes and engine function names:

```python
from pykotor.resource.formats.ncs import NCSInstructionType
from pykotor.common.scriptdefs import KOTOR_FUNCTIONS

for ins in read_ncs(data).instructions:
    t = ins.ins_type
    note = f"-> {ins.jump.offset:#06x}" if ins.jump is not None else ""
    if t is NCSInstructionType.ACTION:
        note = f"{KOTOR_FUNCTIONS[ins.args[0]].name}/{ins.args[1]}"
    print(
        f"{ins.offset:#06x}  {t.value.byte_code:02x} {t.value.qualifier:02x}  {t.name:<10} {ins.args or ''} {note}"
    )
# 0x002b  05 00  ACTION     [578, 1] GetGlobalBoolean/1
# 0x0046  1f 00  JZ          -> 0x006f
```

## Compile

`compile_nss(source, game, optimizers=None, library_lookup=None)` (`resource/formats/ncs/ncs_auto.py`) parses with PLY and returns an `NCS`. It needs nothing outside the package:

- **Function and constant tables** come from `pykotor.common.scriptdefs` (`KOTOR_FUNCTIONS`/`KOTOR_CONSTANTS` for `Game.K1`, `TSL_*` for `Game.K2`). A `nwscript.nss` on disk is never read by the built-in compiler.
- **`#include "x"`** looks for `x.nss` in each `library_lookup` directory in order, then in `pykotor.common.scriptlib.KOTOR_LIBRARY` / `TSL_LIBRARY`, a dict of the game's own `k_inc_*` sources. Pass the mod's folder when it ships its own includes: `compile_nss(src, Game.K1, library_lookup=[tslpatchdata])`.
- **Errors** (`resource/formats/ncs/compiler/classes.py`): `CompileError` (syntax, type mismatch), its subclass `EntryPointError` (no `main()`/`StartingConditional()`, i.e. an include file) and `MissingIncludeError` are subclasses; catch `CompileError`.
- `RemoveNopOptimizer` always runs; other optimizers in `optimizers.py` are off by default and untested upstream.
- File-to-file: `InbuiltNCSCompiler().compile_script(src_path, out_path, Game.K1)` (`resource/formats/ncs/compilers.py`) adds the source's folder to the include path.

`ExternalNCSCompiler(path_to_nwnnsscomp_exe)` runs a Windows `nwnnsscomp.exe` as a subprocess and identifies the variant by SHA-256 (`KnownExternalCompilers`: the TSLPatcher build that mods ship in `tslpatchdata/`, KOTOR Tool, v1, KOTOR Scripting Tool). On Linux it needs a binfmt-registered Wine to run at all, and HoloPatcher only tries it on Windows (`tslpatcher/mods/nss.py`). Not verified on Linux.

## Decompile

There is no working decompiler. `decompile_ncs(ncs, game)` and `NCSDecompiler.decompile_dencs()` import `pykotor.resource.formats.ncs.dencs`, which is not in the 2.3.12 wheel (nor in upstream master at `ca61ce8d5`), so every call raises `DecompileError: DeNCS decompilation failed: No module named ...dencs`. `NCSDecompiler(ncs, game).decompile()` runs but emits a stub (`void main() { int var_0; }`) for a real script. The `pykotor decompile` CLI command goes through the same path. To read a module script, disassemble it as above and name the `ACTION` calls.

## Traps

- **Engine-call arguments are pushed in the opposite order from BioWare's compiler** in 2.3.12 and upstream master (a regression from the December 2025 merge; before it the loop ran `reversed(self._args)`). The game reads such calls' arguments from the wrong slots: Alignment Affects Force Powers' Cure, compiled this way, healed nobody and applied an unrelated effect. `GetNearestObjectByTag("tag", OBJECT_SELF, 2)` compiles to `CONSTS, CONSTO, CONSTI, ACTION 229` where BioWare's has `CONSTI, CONSTO, CONSTS`. Patch #7 of the [series](https://github.com/ivy/PyKotor/commits/modshop-patches) fixes it (vanilla scripts that recompile byte-identically go from 6 to 262 of 794 with no `#include`). With stock pykotor, treat every built-in-compiled script, which includes everything HoloPatcher's `[CompileList]` builds off Windows, as broken if it calls a multi-argument engine function; patch #8 lets HoloPatcher run the mod's own `nwnnsscomp.exe` through a launcher such as `wine` (`PYKOTOR_NWNNSSCOMP_LAUNCHER`).
- **Round-trip is not byte-identical.** Of the 1,754 vanilla NSS with a shipped NCS, stock 2.3.12 recompiles 6 to identical bytes; 200 hold the same instructions in another order (the argument order above); 275 fail to compile (250 of them the `nop` bug below; the rest are type mismatches, duplicate prototypes, one case-mismatched `#include`); the other 1,273 differ in length, and in the ones inspected the difference is dead code from includes (next item). Compare behaviour, not bytes.
- **Includes are compiled whole.** Every function of every included file lands in the NCS whether called or not: `k_act_com41` is 92 instructions from BioWare's compiler and 4,943 from pykotor's. The file is larger; nothing else is known to follow from it.
- **`#include` names are case-sensitive against the bundled library**: `#include "K_inc_utility"` raises `MissingIncludeError`. Files in `library_lookup` folders match case-insensitively, so a folder holding `k_inc_utility.nss` resolves it.
- **Identifiers beginning with `nop`, any case, do not parse.** The lexer's `NOP` token is `[Nn][Oo][Pp]` with no word boundary, so `nOpponent` or `nOption` lexes as `NOP` + identifier: `CompileError: Syntax error … token='nOp'`. 250 vanilla globals fail this way, every script that includes `k_inc_man` or `k_inc_tat` among them. Rename the variable.
- **Mixed int/float arithmetic** (`nInt * fFloat`, `+ - * /`) is typed as the left operand in stock 2.3.12, so `FloatToInt(nHeal * fMod)` fails with a type mismatch. The fix (`compiler/lexer.py`, #5 in the [patch series](https://github.com/ivy/PyKotor/commits/modshop-patches)) types it float, as the engine and nwnnsscomp do.
- **NCS model equality is not byte equality.** `read_ncs` reads `INCxSP`/`DECxSP` offsets as unsigned (`4294967284` where the compiler holds `-12`), so `read_ncs(bytes_ncs(n)) == n` can be `False` while the bytes round-trip exactly. Compare `bytes_ncs(...)` output.
- **`compile_nss` returns embedded bytecode untouched.** A source containing a `/*__NCS_BYTECODE__ <base64> __END_NCS_BYTECODE__*/` block is not compiled at all; the block's NCS is returned.
- **Speed.** A script that includes `k_inc_generic` takes about a second to compile; all 1,754 vanilla globals take about eight minutes.
- **Source encoding.** Game NSS is Windows-1252; decode with `"windows-1252"`, not UTF-8.
