from pathlib import Path
import subprocess
import sys

from config import (
    FFMPEG_PATH,
    FFPROBE_PATH,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
)

# ==========================================================
# PATHS
# ==========================================================

VERSE_FOLDER = Path(
    r"C:\SBG\SBG-v4\output\chapter_001\verse_001"
)

SCENE_FOLDER = (
    VERSE_FOLDER / "scene1"
)

IMAGE_FILE = (
    SCENE_FOLDER / "composed_image.png"
)

AUDIO_FILE = (
    SCENE_FOLDER / "narration.mp3"
)

SUBTITLE_FRAMES = (
    SCENE_FOLDER / "_subtitle_frames"
)

OUTPUT_FILE = (
    SCENE_FOLDER / "scene1_zoom_test.mp4"
)

FFMPEG = Path(
    FFMPEG_PATH
)

FFPROBE = Path(
    FFPROBE_PATH
)

# ==========================================================
# SETTINGS
# ==========================================================

ZOOM_START = 1.0
ZOOM_END = 1.10

# ==========================================================
# CHECK FILES
# ==========================================================

def check_file(path, description):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"{description} not found:\n{path}"
        )

    if path.stat().st_size <= 0:
        raise RuntimeError(
            f"{description} is empty:\n{path}"
        )

    print(
        f"✓ {description}: {path}"
    )

    return path


check_file(
    IMAGE_FILE,
    "Scene 1 image",
)

check_file(
    AUDIO_FILE,
    "Scene 1 narration",
)

if not SUBTITLE_FRAMES.exists():

    raise FileNotFoundError(
        "Scene 1 subtitle frames not found:\n"
        f"{SUBTITLE_FRAMES}\n\n"
        "Run the normal pipeline first so that "
        "_subtitle_frames are created."
    )

subtitle_pattern = (
    SUBTITLE_FRAMES
    / "frame_%06d.png"
)

print(
    f"✓ Subtitle frames: {SUBTITLE_FRAMES}"
)

# ==========================================================
# GET AUDIO DURATION
# ==========================================================

probe_command = [
    str(FFPROBE),

    "-v",
    "error",

    "-show_entries",
    "format=duration",

    "-of",
    "default=noprint_wrappers=1:nokey=1",

    str(AUDIO_FILE),
]

probe = subprocess.run(
    probe_command,
    capture_output=True,
    text=True,
    check=True,
)

duration = float(
    probe.stdout.strip()
)

if duration <= 0:
    raise RuntimeError(
        "Invalid narration duration."
    )

print()
print(
    f"Scene 1 duration: {duration:.3f} seconds"
)

# ==========================================================
# ZOOM FILTER
# ==========================================================
#
# We first create a large canvas.
#
# Then progressively zoom from:
#
#       1.00x
#          ↓
#       1.10x
#
# The image remains centered.
#
# ==========================================================

# ==========================================================
# KEN BURNS ZOOM
# ==========================================================
#
# IMPORTANT:
# The image is first fitted completely inside the
# 1080x1920 frame.
#
# Then a very subtle zoom is applied.
#
# No additional crop is performed.
#
# ==========================================================

zoom_filter = (

    f"[0:v]"
    
    # Fit the complete image to the Shorts canvas.
    f"scale="
    f"{VIDEO_WIDTH}:"
    f"{VIDEO_HEIGHT}:"
    f"force_original_aspect_ratio=decrease,"

    # Put the complete image in the canvas.
    f"pad="
    f"{VIDEO_WIDTH}:"
    f"{VIDEO_HEIGHT}:"
    f"(ow-iw)/2:"
    f"(oh-ih)/2,"
    
    f"fps={FPS},"

    # Subtle zoom.
    f"zoompan="
    f"z='min("
    f"{ZOOM_START}+"
    f"({ZOOM_END - ZOOM_START:.6f})*"
    f"on/"
    f"max(1,{int(round(duration * FPS)) - 1}),"
    f"{ZOOM_END}"
    f")':"
    
    f"x='iw/2-(iw/zoom/2)':"
    f"y='ih/2-(ih/zoom/2)':"
    
    f"d=1:"
    f"s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:"
    f"fps={FPS},"

    f"format=rgba"
    f"[bg];"

    # ------------------------------------------------------
    # Subtitle overlay
    # ------------------------------------------------------

    f"[2:v]"
    f"format=rgba"
    f"[sub];"

    # ------------------------------------------------------
    # Composite
    # ------------------------------------------------------

    f"[bg][sub]"
    f"overlay=0:0,"
    f"format=yuv420p"
    f"[v]"
)


# ==========================================================
# FFMPEG COMMAND
# ==========================================================

command = [

    str(FFMPEG),

    "-hide_banner",

    "-loglevel",
    "error",

    "-y",

    # ======================================================
    # IMAGE
    # ======================================================

    "-loop",
    "1",

    "-i",
    str(IMAGE_FILE),

    # ======================================================
    # AUDIO
    # ======================================================

    "-i",
    str(AUDIO_FILE),

    # ======================================================
    # SUBTITLE FRAMES
    # ======================================================

    "-framerate",
    str(FPS),

    "-i",
    str(subtitle_pattern),

    # ======================================================
    # FILTER
    # ======================================================

    "-filter_complex",
    zoom_filter,

    # ======================================================
    # MAP
    # ======================================================

    "-map",
    "[v]",

    "-map",
    "1:a",

    # ======================================================
    # VIDEO
    # ======================================================

    "-c:v",
    "libx264",

    "-preset",
    "medium",

    "-crf",
    "18",

    "-pix_fmt",
    "yuv420p",

    # ======================================================
    # AUDIO
    # ======================================================

    "-c:a",
    "aac",

    "-b:a",
    "192k",

    "-ar",
    "48000",

    # ======================================================
    # EXACT DURATION
    # ======================================================

    "-t",
    f"{duration:.6f}",

    "-movflags",
    "+faststart",

    str(OUTPUT_FILE),
]

# ==========================================================
# PRINT
# ==========================================================

print()
print("=" * 80)
print("SBG V4 — SCENE 1 ZOOM TEST")
print("=" * 80)

print()
print(f"Image       : {IMAGE_FILE}")
print(f"Audio       : {AUDIO_FILE}")
print(f"Subtitles   : {SUBTITLE_FRAMES}")
print(f"Zoom        : {ZOOM_START:.2f}x -> {ZOOM_END:.2f}x")
print(f"FPS         : {FPS}")
print(f"Duration    : {duration:.3f}s")
print(f"Output      : {OUTPUT_FILE}")

print()
print("Rendering Scene 1 only...")
print()

# ==========================================================
# RUN
# ==========================================================

subprocess.run(
    command,
    check=True,
)

# ==========================================================
# VERIFY
# ==========================================================

if not OUTPUT_FILE.exists():
    raise RuntimeError(
        "FFmpeg completed but output was not created:\n"
        f"{OUTPUT_FILE}"
    )

if OUTPUT_FILE.stat().st_size <= 0:
    raise RuntimeError(
        "Output video is empty:\n"
        f"{OUTPUT_FILE}"
    )

print()
print("=" * 80)
print("✓ SCENE 1 ZOOM TEST COMPLETE")
print("=" * 80)
print()
print(
    f"Output:\n{OUTPUT_FILE}"
)
print()