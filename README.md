# family-film

A cozy, interactive cartoon **Movie Night** living room scene starring **Sunny Fox**, **Luna Bat**, and **PoppyDash** on a plush couch.

## Features

- **Zero-Build Static App**: Single-file [`index.html`](index.html) with layered SVG artwork, GPU-composited animations, a 60fps simulated movie-screen light engine, procedural Web Audio SFX, and a universal dual-engine voice system (`audio/*.mp3` + Web Speech API fallback).
- **6 Interactive Scene Props + Kid-Friendly Slapstick Reactions**:
  1. **Draggable & Two-Tap Soda Cups** (*Red Berry Fizz* & *Blue-Razz*): Drag either cup from the coffee table onto any character (or click a cup, then click a character). Giving PoppyDash the **Red Berry Fizz** triggers his repeatable **Mega Skunk Toot** (rocket-hop recoil, lime-green cartoon toot cloud, raspberry fart SFX, and Sunny Fox leaning away fanning her nose!); giving him the **Blue-Razz** triggers his **Super Bubble Burp** (bubbly burp SFX, floating soda bubbles, and bouncy hiccups!).
  2. **Corner Floor Lamp**: Pull the brass chain to toggle the lamp on/off, darkening the room so the movie-screen glow pops across the characters, lighting up Luna Bat's nocturnal eyes, and startling PoppyDash into his **bottle-brush tail dark panic**.
  3. **TV Remote Control**: Click to zap through **4 movie genres** (*Sci-Fi*, *Spooky*, *Action*, *Puppies*), dynamically changing the movie light falling on the room and triggering PoppyDash's **Sci-Fi Armrest Crash** and **Spooky Tickle-Monster Hover**.
  4. **String Fairy Lights**: Click the strand to cycle **Cozy Twinkle**, **Party Rainbow Chase** (triggering PoppyDash's **Wiggly Skunk Dance Spin-Out**), and **Off**.
  5. **Couch Throw Pillows**: Click the yellow pillow to fluff Sunny's corner seat, or click the coral pillow for Luna's trampoline bounce and PoppyDash's **Silly Pillow King Ambush** gag.
  6. **Vintage 35mm Film Reel & Wall Movie Poster**: Spin the shelf reel for projector clacks, warm sepia film flicker, and PoppyDash getting **eaten by the couch cushions**; click the framed wall poster to cycle between 3 movie posters (*Star Quest*, *Midnight Wings*, *Funky Skunk*).
- **PoppyDash Physical Comic Relief**: Clicking PoppyDash directly cycles through 3 non-popcorn physical comedy stunts (**Giant Tail-Tickle Sneeze**, **Squeaky-Landing Trampoline Bounce**, and **Super Skunk Tail-Bonk Spin**), while the **Spill Popcorn!** toolbar button triggers his classic popcorn tumble anytime.
- **Single-Pass Story Playback**: The 8-line Movie Night dialogue plays through once and stops cleanly after Line 8 so you can freely play with the room without looping; prop interactions mid-story pause and seamlessly resume playback. Press **Replay**, **Play**, **Prev**, or **Next Line** to restart.
- **Organic Movie-Screen & Room Lighting**:
  - `requestAnimationFrame` **Movie Light Engine** simulates realistic film color drifts, 24fps-style luminance flutter, naturalistic scene cuts, and genre-specific flashes falling directly across the characters, couch, coffee table, and shifting back-wall cast shadows.
  - Individually staggered, GPU-composited fairy-light halos, a gently breathing corner lamp, and drifting cinema dust motes.
  - Nested character transform layers eliminate snapping/teleporting on Luna Bat's flight transitions and allow idle breathing, talking head-nods, and slapstick gags to compose smoothly.
- **Universal Character Voices & Sound Effects (Mobile, iPad & Desktop)**:
  - **Studio Voices (Default)**: 34 pre-rendered neural voice clips (`audio/line-0.mp3`–`audio/line-7.mp3` and `audio/react-*.mp3`) played through a universally unlocked Web Audio / HTML5 Audio pipeline (with `navigator.audioSession.type = 'playback'` so audio works across iPhone, iPad — even in Silent Mode — Android, and desktop).
  - **Browser Voices (Optional / Offline Fallback)**: Hardened Web Speech API (`speechSynthesis`) selectable in the **Cast Voices** panel.

## Usage

Open [`index.html`](index.html) in any modern mobile, tablet, or desktop browser (or visit the GitHub Pages site) and tap/click **Play Movie Night with Voices & SFX**.

---

## Generating & Adding Character Voices

All Studio voice clips in [`audio/`](audio/) are pre-rendered with Microsoft Edge Neural TTS (`edge-tts`) as `24 kHz, 48 kbps mono` MP3 files using the canonical script [`scripts/generate_voices.py`](scripts/generate_voices.py).

### Canonical Cast Voices

| Character | Speaker Key | Neural Voice ID | Rate | Pitch |
|---|---|---|---|---|
| **Sunny Fox** (Woman) | `fox` | `en-US-AriaNeural` | `+0%` | `+0Hz` |
| **Luna Bat** (Girl) | `bat` | `en-US-AnaNeural` | `+4%` | `+2Hz` |
| **PoppyDash** (Man) | `skunk` | `en-US-GuyNeural` | `+0%` | `-2Hz` |

### Prerequisites

```bash
pip install edge-tts
```

### Common Commands

```bash
# Inspect all clips in the manifest and check which files exist in audio/
python3 scripts/generate_voices.py --list

# Generate only newly added / missing clips (leaves existing audio/*.mp3 untouched)
python3 scripts/generate_voices.py

# Regenerate specific clip(s) after editing a line
python3 scripts/generate_voices.py --only react-drink-skunk-1 react-click-skunk-sneeze

# Regenerate every clip in the manifest (main story + all interactive reactions)
python3 scripts/generate_voices.py --all
```

### Adding a New Spoken Line

1. Add a `(clip_id, speaker_key, text)` tuple to `CLIPS` in [`scripts/generate_voices.py`](scripts/generate_voices.py). *(Tip: use natural casing like `Whoa!` or `Achoo!` instead of ALL-CAPS like `WHOA!` so neural TTS pronounces them as words rather than spelling them out as acronyms.)*
2. Run `python3 scripts/generate_voices.py` to generate `audio/<clip_id>.mp3`.
3. Reference `'audio/<clip_id>.mp3'` in `DIALOGUE` or `PROP_REACTIONS` (and add it to `ALL_REACTION_AUDIO_FILES` for background warm-up) in [`index.html`](index.html).
4. Commit the updated script, HTML, and `.mp3` file together.
