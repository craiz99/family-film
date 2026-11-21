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
    ("react-drink-fox-1", "fox", "Ooh, berry fizz? Now that is five-star lounge service."),
    ("react-drink-fox-2", "fox", "Chilled to perfection. Cheers, movie crew!"),
    ("react-drink-bat-1", "bat", "Sluuurp! Fizzy bubbles tickle my fangs! Wheee!"),
    ("react-drink-bat-2", "bat", "Zoom-juice! Watch me do a double loop-de-loop!"),
    # Note: Avoid ALL-CAPS words (e.g. use "Whoa!" instead of "WHOA!") so neural TTS
    # pronounces them naturally instead of spelling them out letter by letter.
    ("react-drink-skunk-1", "skunk", "Ooh, icy... Whoa, brain freeze! Tell my fluffy tail I loved it!"),
    ("react-drink-skunk-2", "skunk", "Hic! Excuse me, hic! Totally dignified! Completely under... hic! ...control!"),

    # ---------- Corner Floor Lamp ----------
    ("react-lamp-off-skunk", "skunk", "Whoa! Nobody move! Whose giant fuzzy tail am I holding?! Oh, wait, it's mine."),
    ("react-lamp-off-bat", "bat", "Yesss! Full bat-vision mode! Now it feels like a real theater!"),
    ("react-lamp-on-bat", "bat", "Ack, my nocturnal eyes! Too bright, too bright!"),
    ("react-lamp-on-fox", "fox", "Back to golden hour. Honestly, it's my best lighting anyway."),

    # ---------- TV Remote (4 Movie Genres) ----------
    ("react-remote-scifi-skunk", "skunk", "Engage hyperdrive! Pew-pew... whoa, armrest! Totally meant to park sideways."),
    ("react-remote-spooky-skunk", "skunk", "Nope! Nope-nope-nope! That spooky hallway definitely just blinked at me!"),
    ("react-remote-action-bat", "bat", "Boom! Did you see that mega-flip?! Rewind it, rewind it!"),
    ("react-remote-romcom-fox", "fox", "Finally, a film with proper wardrobe and golden sunset lighting."),

    # ---------- String Fairy Lights ----------
    ("react-fairy-party-skunk", "skunk", "Oh yeah, watch the funky skunk groove! Woo! Wait, too funky, room is spinning!"),
    ("react-fairy-off-fox", "fox", "Ultra-cozy theater mode. Very chic, very dramatic."),
    ("react-fairy-cozy-bat", "bat", "Ooh, twinkly stars indoors! Way prettier than the cave ceiling!"),

    # ---------- Couch Throw Pillows ----------
    ("react-pillow-fox", "fox", "Mmm, freshly fluffed. Nobody steals the corner seat."),
    ("react-pillow-skunk", "skunk", "Hey! The couch just fought back! Did everyone see that pillow ambush me?!"),
    ("react-pillow-bat", "bat", "Boing! Best bat trampoline in the entire house!"),

    # ---------- Shelf Film Reel & Wall Poster ----------
    ("react-reel-fox", "fox", "Classic thirty-five millimeter reel! Now that is true cinema appreciation."),
    ("react-reel-skunk", "skunk", "Ah yes, exquisite vintage cinema... whoa, cushion abyss! Send a rescue rope!"),
    ("react-poster-bat", "bat", "Ooh, put up the Midnight Wings poster! That one's my favorite!"),

    # ---------- PoppyDash Direct-Click Physical Comedy Stunts ----------
    ("react-click-skunk-sneeze", "skunk", "Ah... ah... achoo! Whoa! Note to self: never sniff my own fluffy tail mid-movie."),
    ("react-click-skunk-bounce", "skunk", "Watch me stick this landing... whoa, extra springy cushion! Ten out of ten recovery!"),
    ("react-click-skunk-dodge", "skunk", "Slow-motion ninja dodge! Hiyah... oof, tripped over my own tail again. Smooth."),
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
