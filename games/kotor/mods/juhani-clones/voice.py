"""The mod's voice lines: each a stretch of one recording in voice/, made into what the game loads.

A line is cut from its take at the take's transcript (voice/<take>.json, word times from AWS
Transcribe), encoded as the game's own voice files are (MP3 behind a fixed 58-byte WAV header), and
given a lip-sync file from Rhubarb's mouth cues for the same stretch.
"""

import json
import subprocess
import tempfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from pykotor.resource.formats.lip import LIP, LIPShape, bytes_lip

VOICE = Path(__file__).resolve().parent / "voice"

# The header every voice file in the game's streamwaves/ starts with: a RIFF "PCM" header whose data
# chunk is empty, the MP3 stream following it.
WAV_HEADER = bytes.fromhex(
    "52494646 32000000 57415645 666d7420 12000000 01000100 22560000 22560000 01000800 0000"
    "66616374 04000000 00000000 64617461 00000000".replace(" ", "")
)
# The game's own voice MP3s: mono, 32 kHz, 48 kbit/s
MP3 = ("-ac", "1", "-ar", "32000", "-c:a", "libmp3lame", "-b:a", "48k")
LEAD = 0.15  # seconds kept before a stretch's first word and after its last

# Rhubarb's mouth shapes (https://github.com/DanielSWolf/rhubarb-lip-sync#mouth-shapes) as the game's
RHUBARB_SHAPES = {
    "A": LIPShape.MPB,  # closed: M, B, P
    "B": LIPShape.STS,  # slightly open, teeth together: most consonants
    "C": LIPShape.EH,  # open: EH, AE
    "D": LIPShape.AH,  # wide open: AA
    "E": LIPShape.OH,  # slightly rounded: AO, ER
    "F": LIPShape.OOH,  # puckered: UW, OW, W
    "G": LIPShape.FV,  # upper teeth on the lower lip: F, V
    "H": LIPShape.L,  # tongue raised: L
    "X": LIPShape.NEUTRAL,  # at rest
}


@dataclass(frozen=True)
class Line:
    """`resref` spoken as segments `first`..`last` (inclusive, from 0) of `take`'s transcript, or
    the whole take; `text` is the subtitle, and what Rhubarb is told was said."""

    resref: str
    take: str
    text: str
    first: int | None = None
    last: int | None = None

    def span(self) -> tuple[float, float]:
        transcript = json.loads((VOICE / f"{self.take}.json").read_text())["results"]
        chosen = transcript["audio_segments"]
        if self.first is not None:
            chosen = chosen[self.first : len(chosen) if self.last is None else self.last + 1]
        if not chosen:
            raise SystemExit(f"{self.resref}: {self.take} has no segments {self.first}..{self.last}")
        return float(chosen[0]["start_time"]), float(chosen[-1]["end_time"])


def cut(ffmpeg: str, line: Line, out: Path, *codec: str) -> None:
    start, end = line.span()
    start = max(0.0, start - LEAD)
    argv = [ffmpeg, "-v", "error", "-y", "-i", str(VOICE / f"{line.take}.mp3"), "-ss", f"{start:.3f}", "-to", f"{end + LEAD:.3f}", *codec, str(out)]
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{line.resref}: ffmpeg failed:\n{r.stderr}")


def lip(rhubarb: str, wav: Path, text: str) -> bytes:
    said = wav.with_suffix(".txt")
    said.write_text(text)
    cues = wav.with_suffix(".json")
    argv = [rhubarb, "-q", "-f", "json", "--extendedShapes", "GHX", "-r", "pocketSphinx", "-d", str(said), "-o", str(cues), str(wav)]
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"rhubarb failed on {wav.name}:\n{r.stderr}")
    result = json.loads(cues.read_text())
    out = LIP()
    for cue in result["mouthCues"]:
        out.add(float(cue["start"]), RHUBARB_SHAPES[cue["value"]])
    out.add(float(result["metadata"]["duration"]), LIPShape.NEUTRAL)
    return bytes(bytes_lip(out))


def make(line: Line, ffmpeg: str, rhubarb: str, streamwaves: Path, override: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f"{line.resref}-") as tmp:
        mp3, wav = Path(tmp) / "line.mp3", Path(tmp) / "line.wav"
        cut(ffmpeg, line, mp3, *MP3)
        cut(ffmpeg, line, wav, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le")
        (streamwaves / f"{line.resref}.wav").write_bytes(WAV_HEADER + mp3.read_bytes())
        (override / f"{line.resref}.lip").write_bytes(lip(rhubarb, wav, line.text))


def make_all(lines: Sequence[Line], ffmpeg: str, rhubarb: str, game: Path) -> None:
    resrefs = [line.resref for line in lines]
    if len(set(resrefs)) != len(resrefs) or any(len(r) > 16 for r in resrefs):
        raise SystemExit("voice resrefs must be unique and at most 16 characters")
    streamwaves, override = game / "streamwaves", game / "Override"
    with ThreadPoolExecutor() as pool:  # Rhubarb takes seconds a line, in its own process
        list(pool.map(lambda line: make(line, ffmpeg, rhubarb, streamwaves, override), lines))
