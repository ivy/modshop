# Oops! All Juhani

A voiced, branching rework of the duel with Juhani in Dantooine's grove (`danm14ac`), written in [`SCRIPT.md`](SCRIPT.md). When the party reaches her, she speaks before the fight. Answered civilly, the fight is the game's. Insult her twice, with Carth and Mission in the party, and she turns both of them into copies of herself, and the player fights three Juhanis. Afterwards she is defeated in a conversation of her own and leaves for the Enclave as in the game, the two companions lie unconscious until the player talks each of them back up, Mission and Carth trade a few lines, and from then on Carth has one question he will not discuss. The mod's files, resrefs and globals use the prefix `oaj`.

`make.py` is the recipe's last entry, `mod:juhani-clones`, and writes everything below into the build.

## What it installs

| File | What |
| --- | --- |
| `dan14_cutjuh.dlg` | the grove cutscene: Scenes 1 to 3 after the entry that walks her to her mark, and the transformation |
| `dan14_juhani.dlg` | her conversation: Scene 5, her defeat, tried before her own opening line |
| `k_hcar_dialog.dlg`, `k_hmis_dialog.dlg` | Carth's and Mission's own conversations: their recoveries (Scenes 6 to 10), tried first while they are down, and Carth's epilogue question in each of his menus |
| `oaj_banter.dlg` | Scene 11, Mission and Carth's banter, with the settings of the game's `banter.dlg` |
| `streamwaves/oaj_*.wav`, `oaj_*.lip` | the 80 voice lines and their lip sync, made from `voice/` by `voice.py` |
| `k_pdan_juhani31.ncs` | replaces the game's script of that name, the cutscene's EndConversation: the game's fight with her battlecry, or the clones' fight |
| `k_pdan_14juh_d.ncs` | her user-defined script, decompiled from the game's, without the battlecry on her way to her mark, which spoke over her first line |
| `k_oaj_*.ncs` | the rest of the scripts, sharing `k_oaj_inc.nss` |
| `oaj_juhani1.utc`, `oaj_juhani2.utc` | the clones: Juhani's blueprint as the build loads it, with their own tag and spawn script (`k_oaj_clsp`), no user-defined script, no conversation, no hit-point floor, nothing to drop, and half her six ability scores, hit points and Force points |
| `globalcat.2da` | the build's, declaring the mod's globals, all Boolean: `OAJ_SPECIAL` (the last insult was made), `OAJ_DOWN_0` to `OAJ_DOWN_8` (that NPC is down), `OAJ_DONE` (Carth is back up), `OAJ_BANTER` (Scene 11 has started) |
| `appearance.2da` | the build's, with one row, `Juhani_Clones_Hidden`: the brith's row with the model of the game's invisible placeables (`PLC_Invis`), to hide a companion in place |

The dialogs are the copies the build loads (`Override`'s, else the module's), with nodes added at the ends of their lists, so nothing they had is renumbered. Their new lines carry their text in the dialog, not in `dialog.tlk`; the four lines borrowed from the game's own (`nm14acjuha07024_`, `07043_`, `07050_`, `07049_`) keep their `dialog.tlk` text and the game's voice and lip sync. The scripts compile with the build's pinned `nws` against the build's `nwscript.nss` and includes; `make.py` generates one more, `k_oaj_gen`, with `APPEARANCE_HIDDEN` and `NpcTag`, each NPC number's tag from the build's party blueprints. `k_pdan_14juh_d` compiles in BioWare's mode (`--declarations bioware --compat bioware`), in which the unchanged decompile recompiles to the game's bytes; the changed one differs from the game's by exactly one `ActionDoCommand(SignalEvent(...))`. The build stops if any copy of `k_pdan_juhani31` or `k_pdan_14juh_d` in the build is not the game's, if a mod already put either in `Override`, or if `globalcat.2da` already declares one of the mod's globals.

## How it hooks the game

- **The cutscene.** The game's cutscene is owned by an invisible object, `dan14ac_cutobj01`; each of its entries pauses it, has Juhani act (her user-defined events 10 to 40) and is resumed when she is done. Her lines are added after event 10, which walks her to her mark. The civil answers go on to the game's own entries: her stasis on each companion, her saber, the fight. The last insult is offered only with Carth and Mission in the party (`k_oaj_c_cm`), and sets `OAJ_SPECIAL` (`k_oaj_special`).
- **The transformation.** Entries owned by the same object, each run by a script that pauses the cutscene while it lasts, in the module's placed cameras: Juhani casts Fear and both clutch their heads half a second in, by the looping horror animation, for four seconds (`k_oaj_cs_horror`); there is no stasis in this branch; then each in turn, Carth first so that Mission sees it, is hidden in place, taken out of the party and replaced by a clone (`k_oaj_cs_trans`); the three of them draw their sabers (`k_oaj_cs_draw`); and her line from the game, "I, Juhani, shall be your death!". Camera 10 frames her and both companions, and is the horror's, Mission's turn's and the three of them's shot; 9, Carth's turn's, frames him with Mission watching. 13, the cutscene's opening wide shot, frames only ground there. `EffectCutSceneHorrified`, which none of the game's own K1 scripts use, is not used: companions hidden under it were still cowering after every effect of hers had been removed.
- **Hiding a companion.** As Malak's stasis on the Leviathan works (`k_plev_malstun`, `k_plev_postvis`): the companion leaves the party (`RemovePartyMember`, by NPC number, found by tag), so the player can't switch to them, and becomes neutral, so nothing fights them. 0.1 s later they are hidden where they stand by one effect from Juhani, a cutscene paralysis linked with a disguise as `Juhani_Clones_Hidden`; it comes after the removal because leaving the party undoes a disguise put on before it. The clone is created 0.3 s later on their spot, neutral until the fight. If a clone can't be made, the companion rejoins the party, held in her stasis as they were.
- **The start.** `k_pdan_juhani31` signals her event 80, which makes her hostile, as the game's does. Without the last insult it first has `dan14ac_cutobj02` give her battlecry, "I will be your doom!" (`k_pdan_juhani36`), which the game has it give on her way to her mark. After it, `k_oaj_fight` runs on her: the clones turn hostile, draw her saber if they have not (her blueprint carries it unequipped) and attack.
- **Holding her yield.** She yields from her damaged event (1006) below 50 hit points, and her blueprint has `Min1HP` set, so she can't die first. While a clone stands her damaged event is off (`SW_FLAG_EVENT_ON_DAMAGED`), and her hit points are watched every half second. Below 50 while a clone stands, she stands down: her AI off, neutral, a looping tired animation. Her combat AI clears her action queue every round, so none of this is queued on it.
- **The end.** At the first watch where she is below 50 and no clone stands, each body vanishes (made destroyable again from its own context, then destroyed). Every companion down in the grove has every effect of hers taken off, and half a second later lies prone (`ANIMATION_LOOPING_PRONE`), still out of the party, as the game's banter has Bastila trip Mission (`banter.dlg`, `k_swg_bantforce`). Her AI and damaged event come back on, her actions are cleared (her conversation is queued as an action and would wait behind the looping animation), and 1006 is signalled to her; being below 50, she yields.
- **Her defeat.** Her yield starts her conversation, and `k_oaj_c_defeat` takes it ahead of her own opening line, by the same once-only flag (`DAN_JUHANIF_DONE`, as `k_pdan_anger20`). Both of its endings do what the game's redemption does: `k_pdan_juhani12` (`DAN_JEDI_PLOT` 4, `DAN_JUHANI_PLOT` 3, which lets her join the party later), the journal's `dan_trials` 45, and `k_pdan_14juh_01`, which walks her out of the grove. The rejection adds the game's `k_act_darkmed`.
- **The recoveries.** With a pad (KMRP), A on the targeted companion is the engine's default action (event `0xEF`, `GetDefaultActions` at `0x00620620`); for a creature whose standing toward the player is not hostile (the byte at `+0x2dc` of its client object, the one the target box's colour reads: 1 friendly, 0 neutral, 2 hostile) that action is talk (`i_dialog`), as a click is. The engine then runs their OnDialog script (`k_hen_dialogue01`), which hands it to their AI (`k_ai_master`, which a mod in the build replaces, with the game's logic for this event): it starts their conversation only if their AI is on (`SW_FLAG_AI_OFF` clear) and they are commandable. The cutscene's trigger (`k_pdan_juhani27`) turns the companions' AI off (`k_pman_aioff`), and her yield turns it back on (`k_pman_aion`) only for the party's members, which they are not at that moment; a save made then has local boolean 62 set on both, and interacting with them did nothing. So each companion lying down runs `k_pman_aion` first. While they are down, `k_oaj_c_down` takes the conversation ahead of the rest, and its first line gets them up with dialog animation 10055, as `banter.dlg`'s next line gets Mission up. A companion's tag in the world can differ in case from their blueprint's (the grove's Carth is `carth`, `p_carth`'s `Carth`), so tags compare without case. The conversation's end (`k_oaj_up`) puts them back in the party; Carth's sets `OAJ_DONE`. Mission's last line, sending the player to Carth, is said only while he is still down (`k_oaj_c_cardn`). Once Juhani is done (gone, dead, or `DAN_JUHANI_PLOT` 2 or more), a companion still down gets up and rejoins the party if the player is more than 30 m away, checked every second from their own context.
- **The banter.** When the second of them is back, `k_oaj_up` has Mission start `oaj_banter.dlg` with the player, once (`OAJ_BANTER`), as the game's party-initiated conversations start (`k_trg_partyinit`, `k_bant_trig`): the player leading, and the party's actions cleared first. A party member's queue always holds a standing action (in a save, action 61 on each), and a conversation queued without clearing it waits behind it for ever; in play, the banter never started, and the save had it still queued on Mission.
- **The epilogue.** "About what happened on Dantooine..." goes before "Never mind." in each of Carth's menus of questions (every entry linking to that reply), shown once `OAJ_DONE` is set; the build stops if that reply has moved.

The fight goes this way only from the cutscene. Sneaking up on her (`k_pdan_14juh_02`) and attacking her after she yields (`k_pdan_14juh_03`) don't run `k_pdan_juhani31`, so those fights are the game's.

## Voice

`voice/` holds the recordings, in Git LFS: `<character>-<words spoken>.mp3`, with the transcription's `.srt` and `.json` (AWS Transcribe: each word's time and confidence, and the phrases it heard, `audio_segments`). `scenes.py` names, for each voiced node, its take, the phrases of the take it spans (by index into `audio_segments`, or the whole take) and its subtitle, which is the script's where the transcription misheard. `voice.py` makes each line:

- the stretch is cut from the phrases' first word to their last, with 0.15 s kept either side, by ffmpeg;
- it is encoded as the game's own voice files are, MP3, mono, 32 kHz, 48 kbit/s, behind the fixed 58-byte WAV header every file in the game's `streamwaves/` starts with, and written to `streamwaves/<resref>.wav`;
- its lip sync is Rhubarb's mouth cues for the same stretch, told the subtitle text, with each of Rhubarb's shapes mapped to the closest of the game's 16 (`RHUBARB_SHAPES`), written with pykotor to `Override/<resref>.lip`.

`make.py` gets ffmpeg and Rhubarb from the repository's `mise.toml` (the recipe's `Tool` arguments), and the build's output is the same bytes from run to run.

## Tests

`juhani_clones_test.lua` runs the scripts in nws's world model: her stasis as in the game and no battlecry on her way to her mark; the two ways the cutscene ends; the last insult's condition and flag; the transformation's horror, turns and drawn sabers, Carth first, each hidden in place, out of the party, with a neutral clone, and the companion brought back when a clone can't be made; the clones' fight, her stand-down and the end, every effect of hers taken off and the companions lying down out of the party, each starting their recovery when the player comes close once she is done, never during a conversation, and back up when the player walks away once she is done; her defeat's condition; the recoveries' condition and end, Carth's epilogue flag, and the banter started once, only with both back.

```bash
dir=games/kotor/mods/juhani-clones
inc=games/kotor/data/corpus/nss    # nwscript.nss and the includes: `cargo xtask corpus extract` in nwscript
out=$(mktemp -d)
for f in $dir/k_*.nss; do
  s=$(basename $f .nss)
  case $s in
    k_oaj_inc) ;;
    k_pdan_14juh_d) nws -q --game k1 --declarations bioware --compat bioware -I $inc compile $f -o $out/$s.ncs ;;
    *) nws -q --game k1 -I $dir -I $inc -I $dir/test compile $f -o $out/$s.ncs ;;
  esac
done
nws --game k1 -I $inc -I $out test $dir
```

`test/k_oaj_gen.nss` stands in for the include `make.py` generates, with this build's values. The bytecode goes outside the folder because the whole folder is part of the entry's key.

## Not established

The world model doesn't run `CreateObject`, effects or conversations, doesn't clear a creature's action queue the way its combat AI does, and runs delayed commands in the order they were made rather than by their delays. The tests show the scripts make the right calls, not what the engine does with them or exactly when. Established in play: voice lines from `streamwaves/` in the game's encoding play, with their subtitles; a companion out of the party can't be switched to; the clones fight with their sabers; the transformation's polymorph effect (`visualeffects.2da` row 1046); her defeat's lines and choices. Verified only by playing:

- why companions hidden under `EffectCutSceneHorrified` stayed cowering once every effect of hers was removed;
- that the lip sync loads from `Override` and moves the mouth;
- the transformation's timing: the horror as she casts, and the three drawing their sabers;
- that with their AI back on, interacting with a companion lying down opens their recovery, and that dialog animation 10055 gets them up;
- her kneeling in her defeat: `PlayAnimation(ANIMATION_LOOPING_KNEEL_TALK_SAD)` from its first line left her standing; the game's dialog animations (`AnimList`, 10000 and up) do not number `animations.2da`'s rows (10055 gets a companion up; row 55 is `drink`), and which one kneels is not known;
- that a companion added back with `AddPartyMember` after the fight comes back whole and in the party's faction (the Leviathan does it outside combat);
- that the banter starts and plays between the two of them.
