# `/kotor:voice-sample` — A Character's Voice Sample from KotOR

Cuts a few minutes of one character's speech from KotOR's own voice-over into a single leveled WAV, with a transcript, ready to hand to a voice-cloning or TTS tool. Claude finds the folders that hold the character's lines, checks who actually speaks them, and builds the sample with one script.

```text
/kotor:voice-sample Carth, about 2 minutes
/kotor:voice-sample Mission 3 min
/kotor:voice-sample Juhani from ~/games/swkotor
```

Claude also loads it on its own when someone asks for a character's voice lines or a sample to clone.

## Why this exists

Each of these came up while building the first three samples:

- **A folder's name is not its speaker.** The game files its voice-over by conversation in hundreds of folders under `streamwaves/`. Most `miss*` folders are Mission, but `m40aa/miss08` is the Sith guard who locks her up. A sample built from every folder with the right prefix would have a stranger's voice in it.
- **The files misreport themselves.** Every file has a WAV header claiming about a second of 8-bit PCM, and `ffprobe` believes it. The real audio is an MP3 stream after that header, and a few files open with an ID3 tag. Converting them as WAV produces noise.
- **A transcript that doesn't match the audio.** `dialog.tlk` holds the text for each voice file, but some lines carry `<FullName>`, `<Sigh>`, `*emphasis*` or `[stage directions]` that nobody says aloud. Clone tools that align text to audio need those lines left out.
- **Choosing by hand.** A character has hundreds of lines, many of them one-word barks. Taking the longest lines first fills three minutes with about fifteen full sentences in the character's range of moods.

## How it works

`SKILL.md` covers where the game is and how to choose the folders, build, and report. [`scripts/voice-sample.py`](scripts/voice-sample.py) does the work:

- `survey` reads `dialog.tlk` directly (no PyKotor needed) and lists the speakers or one speaker's folders, with sample lines.
- `build` pulls the MP3 out of each file, filters the lines, picks them, and joins them with ffmpeg into a 22.05 kHz mono WAV leveled to −18 LUFS.

It needs Python 3.10 or later, `ffmpeg` and `ffprobe`. It only reads the game and refuses to write inside it.

The game ships its voice-over as 22.05 kHz MP3, which caps what any clone made from it can sound like. The voices belong to living actors: a clone for your own playthrough or testing is one thing, and publishing one, in a released mod for instance, raises consent questions that this skill doesn't answer.

## Where the facts come from

An unmodded KotOR 1 from Steam, in October 2026: all 13,799 files under `streamwaves/` were checked for their layout, the script's `dialog.tlk` reader was compared with PyKotor 2.3.12's on all 26,212 voiced entries, and samples of Carth, Mission and Juhani were built from it, the first judged by ear. TSL was not tried.
