#!/usr/bin/env python3
"""
Generate pre-rendered Studio neural voice MP3 clips for Movie Night (family-film).

Uses Microsoft Edge Neural TTS (`edge-tts`) to produce consistent, cross-platform
24 kHz 48 kbps mono MP3 clips for:
  - Sunny Fox (woman): en-US-AriaNeural
  - Luna Bat  (girl):  en-US-AnaNeural
  - PoppyDash (man):   en-US-GuyNeural

Usage:
  pip install edge-tts

  # Generate only clips that do not yet exist in audio/ (safe default)
  python3 scripts/generate_voices.py

  # Regenerate specific clip IDs (without .mp3 extension)
  python3 scripts/generate_voices.py --only react-drink-skunk-1 react-click-skunk-sneeze

  # Regenerate every clip in the manifest (main story + interactive reactions)
  python3 scripts/generate_voices.py --all

  # List all clip IDs and lines
  python3 scripts/generate_voices.py --list
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError as exc:
    sys.stderr.write(
        "Missing dependency: edge-tts.\n"
        "Install it with: pip install edge-tts\n"
    )
    raise SystemExit(1) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = REPO_ROOT / "audio"

# Canonical Studio Cast voices (matches PR #4 universal voices)
CAST_VOICES: dict[str, dict[str, str]] = {
    "fox": {
        "name": "Sunny Fox",
        "voice": "en-US-AriaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
    "bat": {
        "name": "Luna Bat",
        "voice": "en-US-AnaNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
    },
    "skunk": {
        "name": "PoppyDash",
        "voice": "en-US-GuyNeural",
        "rate": "+0%",
        "pitch": "-2Hz",
    },
}

# Full manifest of spoken clips: (clip_id, speaker_key, text)
CLIPS: list[tuple[str, str, str]] = [
    # ---------- Main 8-Line Movie Night Story ----------
    ("line-0", "bat", "Ooh! The trailers are starting! Turn it up, turn it up!"),
    ("line-1", "fox", "Relax, Luna. Every great film deserves a stylish entrance."),
    ("line-2", "skunk", "I brought extra buttered popcorn! Wait, whoa, slippery bucket!"),
    ("line-3", "skunk", "Whoooa, look out below! My popcorn! My dignity!"),
    ("line-4", "bat", "Wheee! Airborne popcorn! Catching it mid-flight counts as dinner!"),
    ("line-5", "fox", "Ten out of ten for the tumble, PoppyDash. Zero for balance."),
    ("line-6", "skunk", "Hey! At least there is a kernel on my nose for later... right?"),
    ("line-7", "fox", "Alright, crew, eyes on the screen. Best movie night yet!"),

    # ---------- Interactive Drinks (Soda Cups) ----------
    # Note: Avoid ALL-CAPS words (e.g. use "Whoa!" instead of "WHOA!") so neural TTS
    # pronounces them naturally instead of spelling them out letter by letter.
    ("react-drink-fox-1", "fox", "Mmm, yummy berry bubbles! Thanks, buddy!"),
    ("react-drink-fox-2", "fox", "Ooh, icy cold! Careful not to spill it on my fluffy tail!"),
    ("react-drink-bat-1", "bat", "Slurp! Fizzy bubbles are tickling my nose! Hehehe! Zoom zoom!"),
    ("react-drink-bat-2", "bat", "Whoa, super rocket juice! Look at me spin like a purple tornado! Wheee!"),
    ("react-drink-skunk-1", "skunk", "Uh oh, bubbly tummy... Oops, toot! Excuse me! That wasn't me, it was the couch cushion!"),
    ("react-drink-skunk-2", "skunk", "Burp! Oopsie! That blue soda gave me super bubble burps! Hic! Hehe!"),

    # ---------- Corner Floor Lamp ----------
    ("react-lamp-off-skunk", "skunk", "Eek! Who turned out the lights?! Something fluffy touched me! Oh, wait, that's my own butt!"),
    ("react-lamp-off-bat", "bat", "Yay, dark time! My sparkly bat eyes can see everything! Peek-a-boo!"),
    ("react-lamp-on-bat", "bat", "Whoa, too bright! My bat eyes are blinking like crazy! Bloop bloop!"),
    ("react-lamp-on-fox", "fox", "Phew, lights back on! Now we can see PoppyDash's silly face!"),

    # ---------- TV Remote (4 Movie Genres) ----------
    ("react-remote-scifi-skunk", "skunk", "Blast off! Pew pew! Whoa, crash landing on the squishy armrest!"),
    ("react-remote-spooky-skunk", "skunk", "Yikes! A tickle monster! Hide me! Hide my toes!"),
    ("react-remote-action-bat", "bat", "Kaboom! Super bat flip! Watch me do it again, wheee!"),
    ("react-remote-romcom-fox", "fox", "Aww, look at the cute fluffy puppies on TV! Best channel ever!"),

    # ---------- String Fairy Lights ----------
    ("react-fairy-party-skunk", "skunk", "Wiggle wiggle! Watch my silly skunk dance! Whoa, too wiggly, my head is spinning!"),
    ("react-fairy-off-fox", "fox", "Ooh, super secret movie fort! Shhh, the movie is starting!"),
    ("react-fairy-cozy-bat", "bat", "Ooh, pretty rainbow stars! Like fireflies in our living room!"),

    # ---------- Couch Throw Pillows ----------
    ("react-pillow-fox", "fox", "Poof! Super squishy! Hey, no pillow fights until after the movie!"),
    ("react-pillow-skunk", "skunk", "Bonk! Hey, the pillow jumped on my head! Do I look like a silly pillow king?"),
    ("react-pillow-bat", "bat", "Boing, boing, boing! Best bouncy pillow trampoline ever!"),

    # ---------- Shelf Film Reel & Wall Poster ----------
    ("react-reel-fox", "fox", "Spin, spin, spin! That's how old-timey cartoons used to play!"),
    ("react-reel-skunk", "skunk", "Whoa, spinny wheel! Help, the couch is eating me! Blub blub blub!"),
    ("react-poster-bat", "bat", "Ooh, the purple bat poster! Look, that looks just like me! Hehe!"),

    # ---------- PoppyDash Direct-Click Physical Comedy Stunts ----------
    ("react-click-skunk-sneeze", "skunk", "Ah... ah... achoo! Whoa! My fluffy tail tickled my nose! Hehehe!"),
    ("react-click-skunk-bounce", "skunk", "Boing! Look how high I can bounce... oops! Squeaky landing! Hehe!"),
    ("react-click-skunk-dodge", "skunk", "Hi-yah! Super skunk spin! Oops, I bonked myself with my own tail!"),
]


async def synthesize_clip(clip_id: str, speaker: str, text: str, output_path: Path) -> None:
    cfg = CAST_VOICES[speaker]
    communicate = edge_tts.Communicate(
        text=text,
        voice=cfg["voice"],
        rate=cfg["rate"],
        pitch=cfg["pitch"],
    )
    await communicate.save(str(output_path))


async def generate_targets(targets: list[tuple[str, str, str]]) -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for idx, (clip_id, speaker, text) in enumerate(targets, start=1):
        out = AUDIO_DIR / f"{clip_id}.mp3"
        voice_name = CAST_VOICES[speaker]["voice"]
        print(f"[{idx}/{len(targets)}] Generating {out.name} ({speaker} / {voice_name})...")
        await synthesize_clip(clip_id, speaker, text, out)
        size_kb = out.stat().st_size / 1024.0
        print(f"    -> saved {out.relative_to(REPO_ROOT)} ({size_kb:.1f} KB)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate pre-rendered neural voice clips for Movie Night."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all",
        action="store_true",
        help="Regenerate every clip in the manifest (including existing files).",
    )
    group.add_argument(
        "--only",
        nargs="+",
        metavar="CLIP_ID",
        help="Generate only the specified clip IDs (e.g. react-drink-skunk-1).",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="Print all clip IDs, cast voices, and lines, then exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        for clip_id, speaker, text in CLIPS:
            voice = CAST_VOICES[speaker]["voice"]
            exists = "OK" if (AUDIO_DIR / f"{clip_id}.mp3").exists() else "MISSING"
            print(f"{clip_id:28s} [{exists:7s}] {speaker:5s} ({voice:18s}): {text}")
        return

    clip_map = {clip_id: (clip_id, speaker, text) for clip_id, speaker, text in CLIPS}

    if args.only:
        unknown = [cid for cid in args.only if cid not in clip_map]
        if unknown:
            sys.stderr.write(f"Unknown clip ID(s): {', '.join(unknown)}\n")
            raise SystemExit(2)
        targets = [clip_map[cid] for cid in args.only]
    elif args.all:
        targets = list(CLIPS)
    else:
        targets = [
            entry for entry in CLIPS if not (AUDIO_DIR / f"{entry[0]}.mp3").exists()
        ]

    if not targets:
        print("All clips in manifest already exist in audio/. Use --all or --only to regenerate.")
        return

    asyncio.run(generate_targets(targets))
    print(f"Done! Generated {len(targets)} clip(s) in {AUDIO_DIR.relative_to(REPO_ROOT)}/.")


if __name__ == "__main__":
    main()
