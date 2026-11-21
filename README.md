# family-film

A cozy, cartoon-style animated **Movie Night** scene starring **Sunny Fox**, **Luna Bat**, and **PoppyDash** on a living room couch.

## Features

- **Zero-Build Static App**: `index.html` with responsive SVG artwork, CSS keyframe animations, Web Audio SFX, and a universal dual-engine voice system (`audio/line-*.mp3` + Web Speech API fallback).
- **Detailed Characters & Physical Comedy**:
  - **Sunny Fox (Woman)**: Sleek, stylish fox in a cozy plum cardigan with golden sun pin, swaying tail, eyelashes, gesturing paw, and amused side-peek reactions.
  - **Luna Bat (Girl)**: Extra-cute chibi purple bat with oversized sparkling eyes, coral-pink ear bow, scalloped wings, swooping flight paths, and mid-air happy flips.
  - **PoppyDash (Skunk, Man)**: Expressive skunk in a striped lounge shirt who nervously wobbles his overflowing popcorn bucket, tumbles off the couch onto the rug spilling popcorn everywhere, and sheepishly peeks back up with a kernel on his nose.
- **Universal Character Voices & Sound Effects (Mobile, iPad & Desktop)**:
  - **Studio Voices (Default)**: Pre-rendered neural voice clips (`audio/line-0.mp3`–`audio/line-7.mp3`) for **Sunny Fox** (woman), **Luna Bat** (girl), and **PoppyDash** (man), played through a universally unlocked Web Audio / HTML5 Audio pipeline (with `navigator.audioSession` playback mode so audio works across iPhone, iPad — even in Silent Mode — Android, and desktop).
  - **Browser Voices (Optional / Offline Fallback)**: Cross-platform hardened Web Speech API (`speechSynthesis`) selectable in the **Cast Voices** panel.
  - Procedural Web Audio API sound effects (popcorn pops, tumble slide-whistle/thud, bat flutter chimes) with **Voices: On/Muted**, **Cast Voices**, and **Spill Popcorn!** controls.

## Usage

Open `index.html` in any modern mobile, tablet, or desktop browser (or visit the GitHub Pages site) and tap/click **Play Movie Night with Voices & SFX**.
