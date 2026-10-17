# `/kotor:pykotor` — PyKotor by Task

Gives Claude what it needs to answer questions about KotOR's game files with [PyKotor](https://github.com/OpenKotOR/PyKotor): which calls work, which ones look right and aren't, and how to get from "what uses this string?" to an answer without writing a byte scanner. It loads one short index, then only the reference file the task needs.

```text
/kotor:pykotor
/kotor:pykotor what refers to strref 42724?
/kotor:pykotor will this mod's changes.ini touch appearance.2da?
```

Claude also loads it on its own when a task involves KotOR's files or imports `pykotor`.

## Why this exists

PyKotor covers nearly every KotOR format, but most of what an agent needs from it is a one-off script, and the one-off scripts kept failing in the same ways:

- **Inconsistent object shapes.** The same resource is `.data` on one object, `.data()` on another and bare bytes from a third, so each script spent its first minutes on `AttributeError`s.
- **Plausible wrong answers.** `inst.resource()` can return the `.rim` copy of a module resource the game never loads. A reference search for one name in a chain reports "nothing uses it" when the next hop uses a different name. A generic writer quietly writes TSL fields into a K1 file. None of these raise.
- **Rebuilt tools.** PyKotor has reference finders, a disassembler and a command line, but none of them are documented where an agent would look, so a byte scanner over 90,000 resources was written five times in one evening to answer questions `find_strref_references` already answers.
- **Broken corners.** There is no working decompiler; `get_decoded()` returns `repr` strings; the compiler pushes engine-call arguments in the opposite order from BioWare's; headless uninstall stops at a GUI dialog. Knowing this up front saves the hour it takes to find each one.

## How it works

`SKILL.md` is an index of under 60 lines: environment setup, a table from task to reference file, and the traps that cut across every area. The reference files hold the API by task, with runnable snippets and a Traps section each, and Claude reads only the one it needs:

| File | Covers |
| --- | --- |
| [`installation.md`](references/installation.md) | `Installation`, search order, which copy wins, iteration, `Capsule`, `Module`, TLK strings |
| [`formats.md`](references/formats.md) | read/write for every format, GFF navigation, generics vs raw GFF, 2DA, TLK, archives, textures, models, raw header offsets |
| [`references.md`](references/references.md) | the reference finders, a one-pass search for many names, byte encodings, following a chain, a worked example |
| [`scripts.md`](references/scripts.md) | NCS reading and disassembly with engine function names, the built-in compiler and its defects, why there is no decompiler |
| [`tslpatcher.md`](references/tslpatcher.md) | inspecting a `tslpatchdata`, headless install, what each list does, the stock 2.3.12 patcher defects |
| [`cli.md`](references/cli.md) | the `pykotor` command's working invocations and its traps |

## Where the facts come from

Every snippet and claim in the reference files was run against PyKotor 2.3.12 with the [`modshop-patches` series](https://github.com/ivy/PyKotor/commits/modshop-patches) applied, on an unmodded KotOR 1 install and a heavily modded one, in October 2026. Where stock 2.3.12 behaves differently, the files say so. K2 (TSL) is covered only where the API is shared; nothing was run against a TSL install.

When pykotor is upgraded, rerun the snippets in the file you rely on before trusting it, and correct the file where the library has moved.
