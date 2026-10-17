# kotor

A [Claude Code plugin](https://code.claude.com/docs/en/plugins/overview) for working on Knights of the Old Republic: reading a game install and its archives, finding what refers to a string or a script, and reading or patching resources with [PyKotor](https://github.com/OpenKotOR/PyKotor); debugging the game under Proton on Linux, from a crash's evidence to a native stack and the engine's own code; and cutting a character's voice sample from the game's voice-over. It comes from the [modshop](../../README.md) repository, where it was written while building a modded KotOR on Linux, but it doesn't depend on modshop.

## Skills

| Skill | What it gives Claude |
| --- | --- |
| [`/kotor:pykotor`](skills/pykotor/README.md) | PyKotor's capabilities by task, with the API calls that work and the traps that cost time, loaded a section at a time as the task needs it |
| [`/kotor:debug`](skills/debug/README.md) | Debugging KotOR under Proton: the evidence to save, a gdb capture at a glibc abort and symbolizing it, narrowing a crash without a stack, why a pad does nothing on a screen, and reading `swkotor.exe` |
| [`/kotor:voice-sample`](skills/voice-sample/README.md) | A few minutes of one character's voice-over as a single leveled WAV with its transcript, for a voice clone: which folders hold the character's lines, who actually speaks them, and the build |

Claude loads each skill on its own when a task calls for it (KotOR's files or PyKotor; a crash, a Proton log or a controller problem; a character's voice lines); typing `/kotor:pykotor`, `/kotor:debug` or `/kotor:voice-sample` loads one explicitly.

## Requirements

- Claude Code 2.1.275 or later for the one-step install below; older versions use the two-step form.
- PyKotor importable from the Python that Claude runs, for the skill's snippets to work: the project's own environment if it already depends on PyKotor, or a virtual environment of your own. The skill is written against PyKotor 2.3.12 with the six fixes on the [`modshop-patches`](https://github.com/ivy/PyKotor/commits/modshop-patches) branch of a fork, and the reference files mark where stock 2.3.12 differs. Stock `pip install pykotor` reads game files fine; for installing TSLPatcher mods (stock refuses any `[CompileList]`, and a `Replace#=` into a `.mod` silently does nothing) and for some 2DAs, install the patched build:

  ```bash
  pip install "pykotor @ https://github.com/ivy/PyKotor/archive/0847fc03847934b73055a0a2a3140981db754251.tar.gz#subdirectory=Libraries/PyKotor"
  ```
- A copy of the game for anything that reads game files. The plugin contains no game data.
- `ffmpeg` and `ffprobe` for `/kotor:voice-sample`, which needs nothing else (no PyKotor).

## Install

From GitHub, in a Claude Code session:

```text
/plugin install kotor --marketplace ivy/modshop
```

That adds the `modshop` marketplace to your user settings and installs the plugin at user scope, so it loads in every project. The same in two steps, which also works on older versions:

```text
/plugin marketplace add ivy/modshop
/plugin install kotor@modshop
```

To enable it for one project only, install from your shell with a scope: `claude plugin install kotor@modshop --scope project` writes the enable to the project's committed `.claude/settings.json`, so everyone who works in that repository gets it; `--scope local` writes it to the gitignored `.claude/settings.local.json`, for you alone.

From a clone of modshop instead of GitHub, add the clone's path as the marketplace:

```text
/plugin marketplace add /path/to/modshop
/plugin install kotor@modshop
```

A marketplace added from a local path loads the plugin from the clone in place, so a `git pull` or your own edits take effect at the next session start or after `/reload-plugins`.

Inside the modshop repository itself there is nothing to install: its `.claude/settings.json` registers the repository root as the `modshop` marketplace and enables `kotor@modshop`. Accept the workspace trust prompt when you first open the repository, start Claude Code from the repository root, and the plugin loads. The settings give the marketplace's path as `"."`, which Claude Code resolves against the project root; the [settings reference](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces) documents only absolute paths for a `directory` source.

## Check that it loaded

Run `/plugin` and look for `kotor` in the **Installed** tab, or type `/kotor:` and see `pykotor`, `debug` and `voice-sample` offered. If it is missing, the **Errors** tab of `/plugin` says why; [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting) covers each message.

## Update and remove

The plugin carries no version number, so Claude Code versions it by the marketplace's commit. A plugin installed from GitHub updates when you refresh the marketplace and update it, from your shell:

```bash
claude plugin marketplace update modshop
claude plugin update kotor@modshop
```

then `/reload-plugins` in a running session. Third-party marketplaces don't auto-update unless you turn it on for `modshop` in `/plugin` under **Marketplaces**. To remove the plugin, `claude plugin uninstall kotor@modshop`; `claude plugin marketplace remove modshop` removes the marketplace too.
