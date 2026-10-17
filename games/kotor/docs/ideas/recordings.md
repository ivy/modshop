---
title: Game recordings
priority: p1
status: idea
depends_on: []
---

# Game recordings

Steam on the handheld keeps a background recording of every session. One command brings a session home, joins it into a video, and prints a contact sheet to read it by; another cuts it at keyframes without re-encoding.

## The problem

Steam's background recordings (`~/.local/share/Steam/userdata/<account>/gamerecordings/video/bg_<appid>_<date>_<time>/`: MPEG-DASH, `session.mpd` with `init-stream*.m4s` and `chunk-stream*-NNNNN.m4s`, H.264 1080p at about 12 Mbit/s with keyframes every 3 s, and AAC) were the main evidence while the Juhani mod was tuned (2026-10-16/17): what the transformation looked like, which camera shot was empty, where the companions stood, what a trace printed, whether a line played. Each look was done by hand:

- **About eight times**: `rsync` the session folder, join it with `ffmpeg -i session.mpd -c copy`, build a contact sheet with `fps` and `tile`, read it, then extract frames at full size around the moment in question.
- **Failures on the way**: a session still being written has `.tmp` chunks that vanish mid-copy (`rsync` exit 24); joining a session in progress hung `ffmpeg` until it was killed; one copy failed because the handheld's ssh refused connections for a while; shell quoting (`zsh` does not split `$r`) broke two loops. One folder, `bg_32370_20261016_184224`, keeps growing across sessions and is not a single session.
- **Picking the session** meant listing folders by time and guessing which held the run in question; once the guess was a run on the previous build, and the analysis was wasted.
- **The cut to share** had to be made twice: re-encoded first, then, at the owner's request, cut at keyframes with stream copy for full fidelity, which moved each cut to the 3-second keyframe grid (and a seek exactly on a keyframe's time landed on the one before).

## The idea

`modshop kotor recordings`:

- `list`: sessions with start time, duration and whether they are still being written (a `.tmp` chunk or a running game);
- `get SESSION`: copy it home, skipping `.tmp`, join it to `data/recordings/<session>.mp4`, and write a contact sheet with timestamps;
- `frames SESSION FROM TO [--fps N]`: full-size frames for a moment;
- `cut SESSION --keep FROM-TO ... [--reencode]`: segments joined by stream copy, each snapped to the keyframe at or after its start and reported as snapped; `--reencode` for exact cuts and crossfades.

## Unknowns

- Whether Steam's `gamerecording.pb` and `timelines/*.json` mark the boundaries of each game session, which would make `list` exact.

## First step

`get` for the newest finished session, with the contact sheet.
