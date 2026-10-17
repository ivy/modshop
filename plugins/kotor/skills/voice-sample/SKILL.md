---
name: voice-sample
description: Use when someone wants a sample of a KotOR (Knights of the Old Republic) character's voice — for a voice clone, TTS reference or listening — cut from the game's own voice-over. Finds the streamwaves folders that hold the character's lines, checks who actually speaks them, and builds one leveled WAV with its transcript.
when_to_use: "Grab me 2 minutes of Carth", "a voice sample of Mission for a clone", "extract Bastila's voice lines", "how much HK-47 audio is in the game", the same for another character.
argument-hint: "[character] [length, e.g. 3 min] [game path]"
allowed-tools:
  - Read
---

# A character's voice sample from KotOR

**Autonomy:** model-invocable · reads the game install and writes the sample only to an output directory outside it; never edits the game

## Arguments
```
$ARGUMENTS
```

## Find the game

- A KotOR 1 install is the folder holding `dialog.tlk` and `streamwaves/`. Use the path given; else the one the project records; else Steam's `~/.local/share/Steam/steamapps/common/swkotor`. Prefer an unmodded copy: mods replace voice files and `dialog.tlk`.
- K1 only. TSL keeps its voice-over in `StreamVoice/` and was never run through this; say so rather than guess.
- Run the script as `python3 -I ${CLAUDE_SKILL_DIR}/scripts/voice-sample.py`. It needs `ffmpeg` and `ffprobe`, nothing else.

## Choose the folders

- `survey GAME` lists every speaker prefix (a folder name's first four letters) with one line; `survey GAME PREFIX` shows that prefix's folders, their file counts and five lines from each.
- **A prefix names the conversation, not always the speaker.** `m40aa/miss08` is a Sith guard, not Mission. Read every folder's sample lines and keep only folders where all of them are the character.
- A character can have several prefixes (Carth is `cart` and, on Taris, `carb`). Scan the full survey for neighbours.
- Prefer the character's largest conversation folder: personal talks, calm to angry, no combat barks. Carth `m35aa/cart04`, Mission `globe/miss13`, Juhani `m35aa/juha11`. Add a second folder only when the build says it fell short.

## Build

- `build GAME FOLDER... --name NAME --out DIR --seconds N`. N defaults to 180; take it from the request. DIR is a scratch directory or a gitignored one: audio derived from the game never goes into git, and the script refuses a DIR inside the game folder.
- It keeps lines that have text in `dialog.tlk`, no `*`, `[` or `<` markup (the audio doesn't say those verbatim) and 4–15 s of audio. It takes the longest first until N, then puts them back in conversation order with 0.4 s gaps, leveled to −18 LUFS. Output is 22.05 kHz mono 16-bit `NAME.wav` plus `NAME.txt`, one transcript line per clip.
- Read its listing: every line must read as the character. If one doesn't, rebuild without that folder. Note the total length and the skip counts.

## Report

- The absolute paths of the `.wav` and `.txt`, the length and line count, which folders, and what the lines cover.
- The ceiling: the game ships 22.05 kHz MP3, so a clone may sound dull in the high end.
- Once, plainly: the voice belongs to a living actor; a clone for personal use differs from publishing one.

## Examples

- "Grab me ~2 min of Carth" → `survey GAME cart`, pick `m35aa/cart04`, `build … --seconds 120 --name carth`.
- "Closer to 3 min actually" → rebuild the same folder with `--seconds 180`.
- "Same for Mission" → `survey GAME miss`; drop `m40aa/miss08` (a guard), build from `globe/miss13`.
