---
title: Script corpus
priority: p0
status: idea
depends_on: []
---

# Script corpus

Every script the game runs, as source that `grep` reads: the global scripts' original `.nss`, and every module script decompiled from its bytecode, kept under `data/corpus/` beside what is already extracted there.

## The problem

The corpus extracted for the nwscript work (`cargo xtask corpus extract` in nwscript, written to `data/corpus/`) has source only for the scripts BioWare shipped as source: the global scripts in the BIFs. A module's scripts (`danm14ac_s.rim` and the like) are there only as `.ncs`. While making [Oops! All Juhani](../../mods/juhani-clones/README.md) (2026-10-16/17), most of the questions that mattered were "how does the game already do this", and the module scripts were where the answer was:

- **Who turns the companions' AI off.** Interacting with a companion lying down after the fight did nothing. The cause was in a module script: the cutscene's trigger, `k_pdan_juhani27`, runs `k_pman_aioff` on the party, and Juhani's yield turns it back on only for the party. It was found with `strings` over every `.ncs` of the module, then decompiling the hits one at a time. Before that, the same symptom cost two play sessions spent on a workaround (the companions starting their own conversation) and a diagnostic build whose output never appeared.
- **How a party member starts a conversation.** The banter never played: the request waited behind a party member's standing action. The vanilla pattern (`k_trg_partyinit`: lead with the player, `ClearAllActions`, then `ActionStartConversation`) was in the global source and found by `grep`; the equivalent search over module scripts would have needed decompiling first.
- **Who uses an effect.** "No K1 script uses `EffectCutSceneHorrified`" was asserted in a README from the global source alone, and the owner challenged it (the Taris rancor scene). Checking it properly meant writing a byte search for the routine's `ACTION` opcode (`05 00 02 F2 00`) over every `.ncs`, then validating that search on a routine known to be used.
- **The cutscene's own scripts** (`k_pdan_juhani25`…`36`, `k_ptar_victrans`, `k_ptar_rancor*`, the banter scripts) were decompiled one at a time, by hand, whenever a question touched them; roughly thirty decompiles in the session, each a command line, and the long ones printed their whole included library.

## The idea

A step in the corpus extraction, or a `modshop kotor` command over the build tree, that decompiles every `.ncs` in every module capsule and in Override into `data/corpus/decompiled/<capsule>/<script>.nss`, with:

- the main function first and the library functions it inlined from includes after, or dropped when they match an include's source, so a grep hit is in the script's own logic;
- a header naming where it came from (capsule, and which copy the game loads when the same name is in several) and whether nws verified it by recompiling to the original bytes;
- an index of each script's engine calls with their literal arguments (`ExecuteScript("k_pman_aioff", …)`, `ActionPlayAnimation(23, …)`, `SetGlobalBoolean("DAN_JUHANI_FIGHT", …)`), which is what the [asset index](asset-index.md) takes as a script's references.

## Unknowns

- How long decompiling every module script takes (several thousand files; one took about a second).
- How many fail to decompile cleanly; nws reports per function, and a partly verified script is still worth grepping.

## First step

Decompile `danm14ac_s` and reproduce the `k_pman_aioff` finding with one `grep`.
