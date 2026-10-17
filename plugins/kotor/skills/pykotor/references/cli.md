# The `pykotor` command line

`pykotor` (entry point `pykotor.cli.__main__:main`) is installed with pykotor, beside `python`. It has no reference-finding command; for "what uses X?" see the references file. `$GAME` below is a game root (the directory holding `chitin.key`).

Every command below was run against an unmodded K1 install. Run from a scratch directory: commands write `logs/` into the current directory, and `get` refuses output paths outside it.

```bash
pykotor --no-color find k_trans_abort.utp --path "$GAME" 2>/dev/null
```

Results and errors go to **stdout** as `[INFO] …` / `[ERROR] …` lines; stderr carries about 130 lines of DEBUG path-resolution noise per run, which `--quiet` does not silence. Use `--no-color` and `2>/dev/null`. `--quiet` drops the `[INFO]` lines. Failures exit 1.

## Commands that work

| Task | Invocation | Notes |
|---|---|---|
| Where does a resource resolve from | `pykotor find k_trans_abort.utp --path "$GAME"` | Needs an extension or `--type utp`. Glob: `find 'k_trans*' --path "$GAME"` (searches BIFs and modules too). `--all-locations` lists every copy, winner first. Exit 1 when absent. |
| Copy a resource out | `pykotor get k_transabort.dlg --path "$GAME" -o out` | `--format json` writes `k_transabort.dlg.json`. `--source CHITIN` (or `OVERRIDE`, `MODULES`) picks a copy other than the winner. `--path` may be a single RIM/MOD. |
| Text resource to stdout | `pykotor cat "$GAME/chitin.key" k_trg_transfail --type nss` | Archive may be a KEY, RIM or ERF. Pass `--type`; without it the lookup fails. Text only: see Traps. |
| List an archive | `pykotor list-archive --file "$GAME/modules/danm13_s.rim" -v` | Names appear only with `-v`. KEY: `--file "$GAME/chitin.key" --resources --filter 'k_trans*' -v` prints BIF and index. BIF: add `--key-file "$GAME/chitin.key"` or names come out as `resource_00000.dlg`. |
| Find by name | `pykotor search-archive 'k_trans*' --file "$GAME/chitin.key"` | 0.2 s. One archive per call. |
| Grep resource bytes | `pykotor search-archive k_trans_abort --file "$GAME/chitin.key" --content` | Substring of the UTF-8-decoded bytes, case-insensitive; 10 s on `chitin.key`. Finds string resrefs and tags, not strrefs. |
| Extract | `pykotor extract --file "$GAME/chitin.key" --filter 'k_trans*' -o out` | From a KEY, writes one subdirectory per BIF (`out/templates/`). RIM/MOD: `--file "$GAME/modules/danm13.rim" -o out`. A BIF alone needs `--key-file`. |
| Read a GFF | `pykotor gff2xml k_transabort.dlg -o dlg.xml` | Input is a file on disk (`get` it first). Strrefs show as `<locstring label="Text" strref="42724" />`. `gff2json` also works; without `-o` it writes `<stem>.json` beside the input. |
| Grep one file | `pykotor grep k_transabort.dlg 42724` | GFFs are matched field by field (`Text (LocalizedString): 42724`); text files line by line, `-n` for line numbers. |
| Strref to text | `pykotor tlk2json "$GAME/dialog.tlk" -o dialog.json` | 0.4 s, 9 MB. Then `jq -r '.strings[42724].text' dialog.json`. |
| Text to strrefs | `jq -r '.strings[] \| select(.text \| test("gather your party"; "i")) \| ._index' dialog.json` | Prints 42724 and 44230. |
| 2DA as CSV | `pykotor 2da2csv placeables.2da -o placeables.csv` | First column is the row index; the header row is always written (`--headers` changes nothing). |
| Disassemble a script | `pykotor disassemble k_trg_transfail.ncs -o dis.txt` | `ACTION args=[229, 3]` is routine 229 with 3 arguments (no function names); `CONSTS args=['k_trans_abort']` shows string constants. |
| Compile a script | `pykotor assemble k_trg_transfail.nss -o out.ncs` | Compiles; the output is not byte-identical to the shipped NCS. Only tried on a script without `#include`. |
| Compare two resources | `pykotor diff a.dlg b.dlg` | GFF diffs are readable (`GFFList … length 93 -> 95`, added fields). 2DA diffs dump whole rows, twice. `--output-mode quiet` prints nothing and only sets the exit code: 0 same, 1 different. |
| Module texture list | `pykotor module-resources --module danm13 --path "$GAME" -o mr.json` | Textures and lightmaps referenced by the module's models. `investigate-module` prints the same per model. |
| Sanity checks | `pykotor validate-game-root --path "$GAME"`, `pykotor check-2da --2da placeables --path "$GAME"`, `pykotor stats f.dlg`, `pykotor validate f.dlg` | |

## Traps

- **`decompile` is broken**: it fails with `ModuleNotFoundError: No module named 'pykotor.resource.formats.ncs.dencs'`. Use the shipped source instead (`scripts.bif` has `.nss` for nearly all global scripts: `pykotor cat "$GAME/chitin.key" NAME --type nss`) or `disassemble`. Module scripts have no shipped source.
- **`find` mislabels locations.** The label is taken from the search order by position, so the winner always says `Custom_Folders` and the rest are shifted by one. In a modded install `find appearance.2da --all-locations` prints the Override copy as `Custom_Folders selected` and the BIF copy as `Override`; trust the sizes and the order, not the labels. A BIF copy prints no container path.
- **`get -o` must be under the current directory** (`Output path rejected: Path is outside allowed base`). `-o -` does not mean stdout: it creates a directory named `-`. Nothing writes a binary resource to stdout.
- **`cat` corrupts binary resources.** It decodes the bytes as UTF-8 with replacement before writing, so invalid sequences become `EF BF BD` (a 524,427-byte TPC came out as 1,013,155 bytes). Use it for `.nss` and other text; use `get` for GFF, NCS, TPC and the rest.
- **`cat` on a `.bif` path fails** (`Resource not found`); go through `chitin.key`.
- **`extract` on a BIF without `--key-file`** names resources by number, so `--filter` matches nothing and it reports 0 extracted with exit 0.
- **`diff -o FILE`** writes an empty file; capture stdout instead.
- **`--game k1` / `kotor-paths`** find no default game roots on Linux; always pass `--path`.
- `list` is not a resource lister: it lists targets in a `pykotorcli.cfg` project. The project commands (`init`, `unpack`, `convert`, `compile`, `pack`, `install`, `launch`), the `patch-*` commands, the GUI/indoor/kit commands and `diff` over whole game roots were not exercised.
