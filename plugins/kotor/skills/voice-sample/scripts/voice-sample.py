#!/usr/bin/env python3
"""Find a KotOR character's voice-over and cut it into one sample for voice cloning.

  voice-sample.py survey GAME                  speaker prefixes under streamwaves/, with a line each
  voice-sample.py survey GAME PREFIX           that prefix's folders: files, lines with text, samples
  voice-sample.py build GAME FOLDER... --name NAME --out DIR [--seconds 180]

GAME is a KotOR 1 install (the folder with dialog.tlk and streamwaves/). FOLDER is a
folder under streamwaves/, such as m35aa/cart04. build writes DIR/NAME.wav and
DIR/NAME.txt (one line of transcript per clip, in clip order). Needs ffmpeg and ffprobe.
"""

import argparse
import collections
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

# A line whose text carries any of these doesn't match its audio word for word:
# *emphasis* or *actions*, [stage directions], <FullName> and <Sigh> tokens.
UNSPOKEN = "*[<"


def child(parent: Path, name: str) -> Path:
    """parent/name, matching name case-insensitively as Windows installs need."""
    for p in parent.iterdir():
        if p.name.lower() == name.lower():
            return p
    sys.exit(f"no {name} in {parent}")


def read_tlk(path: Path) -> dict[str, str]:
    """Map each voiced entry's sound resref (lowercase) to its text."""
    b = path.read_bytes()
    kind, version, _lang, count, strings = struct.unpack_from("<4s4sIII", b, 0)
    if (kind, version) != (b"TLK ", b"V3.0"):
        sys.exit(f"{path}: not a TLK V3.0 file")
    out: dict[str, str] = {}
    for i in range(count):
        _flags, resref, _vol, _pitch, off, size, _len = struct.unpack_from("<I16sIIIIf", b, 20 + 40 * i)
        resref = resref.split(b"\0")[0].decode("ascii", "replace").lower()
        if resref:
            out[resref] = b[strings + off : strings + off + size].decode("cp1252").strip()
    return out


def mp3_payload(wav: Path) -> bytes:
    """The MP3 stream inside a streamwaves file: everything after the RIFF data chunk's header."""
    b = wav.read_bytes()
    i = b.find(b"data", 12, 512)
    if b[:4] != b"RIFF" or i < 0:
        sys.exit(f"{wav}: not the RIFF-wrapped MP3 the game ships")
    return b[i + 8 :]


def duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(r.stdout.strip() or 0)


def survey(game: Path, prefix: str | None) -> None:
    tlk = read_tlk(child(game, "dialog.tlk"))
    waves = child(game, "streamwaves")
    folders = sorted({p.parent for p in waves.rglob("*") if p.suffix.lower() == ".wav" and p.parent != waves})
    if prefix is None:
        groups: collections.defaultdict[str, list[Path]] = collections.defaultdict(list)
        for d in folders:
            groups[d.name[:4].lower()].append(d)
        for key, ds in sorted(groups.items()):
            files = [f for d in ds for f in d.glob("*.wav")]
            sample = next((tlk[f.stem.lower()] for f in sorted(files) if f.stem.lower() in tlk), "")
            print(f"{key}  {len(ds):3} folders {len(files):5} files  | {sample[:90]}")
        return
    for d in folders:
        if not d.name.lower().startswith(prefix.lower()):
            continue
        files = sorted(d.glob("*.wav"))
        texts = [tlk.get(f.stem.lower()) for f in files]
        known = [t for t in texts if t]
        mb = sum(f.stat().st_size for f in files) / 1e6
        print(f"\n{d.relative_to(waves)}  {len(files)} files, {len(known)} with text, {mb:.1f} MB")
        for t in known[:: max(1, len(known) // 5)][:5]:
            print(f"  | {t[:110]}")


def build(
    game: Path,
    folders: list[str],
    name: str,
    out: Path,
    seconds: float,
    shortest: float,
    longest: float,
    gap: float,
) -> None:
    if not name or Path(name).name != name:
        sys.exit("--name must be a plain file name")
    out = out.resolve()
    if out.is_relative_to(game.resolve()):
        sys.exit("--out is inside the game folder; write the sample somewhere else")
    tlk = read_tlk(child(game, "dialog.tlk"))
    waves = child(game, "streamwaves")
    skipped: collections.Counter[str] = collections.Counter()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips: list[tuple[float, str, Path, str]] = []
        for folder in folders:
            d = Path(folder) if Path(folder).is_absolute() else waves / folder
            for f in sorted(d.glob("*.wav")):
                text = tlk.get(f.stem.lower())
                if not text:
                    skipped["no text in dialog.tlk"] += 1
                    continue
                if any(c in text for c in UNSPOKEN):
                    skipped["text not spoken verbatim"] += 1
                    continue
                mp3 = tmp / f"{f.stem}.mp3"
                mp3.write_bytes(mp3_payload(f))
                secs = duration(mp3)
                if not shortest <= secs <= longest:
                    skipped[f"outside {shortest:g}-{longest:g} s"] += 1
                    continue
                clips.append((secs, f.stem, mp3, text))
        # Longest lines first carry the most speech per clip; then back into conversation order.
        chosen: list[tuple[float, str, Path, str]] = []
        total = 0.0
        for clip in sorted(clips, key=lambda c: (-c[0], c[1])):
            if total >= seconds:
                break
            chosen.append(clip)
            total += clip[0] + gap
        chosen.sort(key=lambda c: c[1])
        if not chosen:
            sys.exit(f"no usable lines; skipped: {dict(skipped)}")

        silence = tmp / "gap.wav"
        ff = ["ffmpeg", "-v", "error", "-y"]
        subprocess.run(
            [*ff, "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", str(gap), str(silence)], check=True
        )
        playlist = tmp / "list.txt"
        with playlist.open("w") as fh:
            for _secs, stem, mp3, _text in chosen:
                wav = tmp / f"{stem}.wav"
                subprocess.run([*ff, "-i", str(mp3), "-ar", "22050", "-ac", "1", str(wav)], check=True)
                fh.write(f"file '{wav}'\nfile '{silence}'\n")
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                *ff,
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(playlist),
                "-af",
                "loudnorm=I=-18:TP=-1.5",
                "-ar",
                "22050",
                "-c:a",
                "pcm_s16le",
                str(out / f"{name}.wav"),
            ],
            check=True,
        )
    (out / f"{name}.txt").write_text("".join(text + "\n" for *_, text in chosen), encoding="utf-8")

    for secs, stem, _mp3, text in chosen:
        print(f"{stem}  {secs:5.1f} s  | {text[:90]}")
    print(
        f"\n{len(chosen)} of {len(clips)} usable lines, {duration(out / f'{name}.wav'):.1f} s -> {out / name}.wav, .txt"
    )
    print(f"skipped: {dict(skipped) or 'none'}")
    if total < seconds:
        print(f"short of {seconds:g} s: add another of the speaker's folders")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("survey")
    s.add_argument("game", type=Path)
    s.add_argument("prefix", nargs="?")
    b = sub.add_parser("build")
    b.add_argument("game", type=Path)
    b.add_argument("folders", nargs="+")
    b.add_argument("--name", required=True)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--seconds", type=float, default=180)
    b.add_argument("--min", dest="shortest", type=float, default=4)
    b.add_argument("--max", dest="longest", type=float, default=15)
    b.add_argument("--gap", type=float, default=0.4)
    a = ap.parse_args()
    if a.cmd == "survey":
        survey(a.game, a.prefix)
    else:
        build(a.game, a.folders, a.name, a.out, a.seconds, a.shortest, a.longest, a.gap)


if __name__ == "__main__":
    main()
