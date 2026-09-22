from pathlib import Path
import subprocess

from config import (
    FFMPEG_PATH,
    FFPROBE_PATH,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
)


# ==========================================================
# SBG V4 — SCENE 1 ZOOM TEST
# ==========================================================

VERSE_FOLDER = Path(
    r"C:\SBG\SBG-v4\output\chapter_001\verse_001"
)

SCENE_FOLDER = VERSE_FOLDER / "scene1"

IMAGE_FILE = SCENE_FOLDER / "composed_image.png"
AUDIO_FILE = SCENE_FOLDER / "narration.mp3"
SUBTITLE_FRAMES = SCENE_FOLDER / "_subtitle_frames"

OUTPUT_FILE = SCENE_FOLDER / "scene1_zoom_test.mp4"

FFMPEG = str(FFMPEG_PATH)
FFPROBE = str(FFPROBE_PATH)


# ==========================================================
# EFFECT
# ==========================================================

ZOOM_START = 1.00
ZOOM_END = 1.20


# ==========================================================
# CHECK FILE
# ==========================================================

def check_file(path, name):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"{name} not found:\n{path}"
        )

    if path.stat().st_size <= 0:
        raise RuntimeError(
            f"{name} is empty:\n{path}"
        )

    print(f"✓ {name}: {path}")

    return path


check_file(
    IMAGE_FILE,
    "Scene 1 image",
)

check_file(
    AUDIO_FILE,
    "Scene 1 narration",
)


# ==========================================================
# CHECK SUBTITLE FRAMES
# ==========================================================

if not SUBTITLE_FRAMES.exists():

    raise FileNotFoundError(
        "Subtitle frame directory not found:\n"
        f"{SUBTITLE_FRAMES}\n\n"
        "Run the normal pipeline once first."
    )


SUBTITLE_PATTERN = (
    SUBTITLE_FRAMES / "frame_%06d.png"
)


# ==========================================================
# AUDIO DURATION
# ==========================================================

probe_command = [

    FFPROBE,

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


total_frames = max(
    1,
    int(
        round(
            duration * FPS
        )
    )
)


print()
print(
    f"Duration    : {duration:.3f}s"
)

print(
    f"Frames      : {total_frames}"
)

print(
    f"Zoom        : "
    f"{ZOOM_START:.2f}x -> "
    f"{ZOOM_END:.2f}x"
)


# ==========================================================
# FILTER
# ==========================================================
#
# IMPORTANT:
#
# 1. Image is fitted to the complete 1080x1920 canvas.
#
# 2. We create a slightly larger canvas.
#
# 3. The image slowly zooms from 1.00 to 1.04.
#
# 4. The image stays centered.
#
# 5. Subtitle overlay is added AFTER the zoom.
#
# ==========================================================

zoom_filter = (

    # ------------------------------------------------------
    # IMAGE
    # ------------------------------------------------------

    f"[0:v]"

    # Fit image while preserving aspect ratio.
    f"scale="
    f"{VIDEO_WIDTH}:"
    f"{VIDEO_HEIGHT}:"
    f"force_original_aspect_ratio=decrease,"

    # Center image on Shorts canvas.
    f"pad="
    f"{VIDEO_WIDTH}:"
    f"{VIDEO_HEIGHT}:"
    f"(ow-iw)/2:"
    f"(oh-ih)/2,"

    # Convert to RGBA.
    f"format=rgba,"

    # ------------------------------------------------------
    # ZOOM
    # ------------------------------------------------------

    f"zoompan="

    f"z='"
    f"{ZOOM_START}+"
    f"({ZOOM_END - ZOOM_START:.6f})*"
    f"on/"
    f"{max(1, total_frames - 1)}"
    f"'"

    f":"
    
    # Keep zoom centered.
    f"x='iw/2-(iw/zoom/2)'"

    f":"

    f"y='ih/2-(ih/zoom/2)'"

    f":"

    f"d=1"

    f":"

    f"s="
    f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}"

    f":"

    f"fps={FPS}"

    f"[bg];"


    # ------------------------------------------------------
    # SUBTITLE OVERLAY
    # ------------------------------------------------------

    f"[2:v]"
    f"format=rgba"
    f"[sub];"


    # ------------------------------------------------------
    # COMPOSITE
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

    FFMPEG,

    "-hide_banner",

    "-loglevel",
    "error",

    "-y",


    # ------------------------------------------------------
    # IMAGE
    # ------------------------------------------------------

    "-loop",
    "1",

    "-i",
    str(IMAGE_FILE),


    # ------------------------------------------------------
    # AUDIO
    # ------------------------------------------------------

    "-i",
    str(AUDIO_FILE),


    # ------------------------------------------------------
    # SUBTITLE FRAMES
    # ------------------------------------------------------

    "-framerate",
    str(FPS),

    "-i",
    str(SUBTITLE_PATTERN),


    # ------------------------------------------------------
    # FILTER
    # ------------------------------------------------------

    "-filter_complex",
    zoom_filter,


    # ------------------------------------------------------
    # MAP
    # ------------------------------------------------------

    "-map",
    "[v]",

    "-map",
    "1:a",


    # ------------------------------------------------------
    # VIDEO
    # ------------------------------------------------------

    "-c:v",
    "libx264",

    "-preset",
    "medium",

    "-crf",
    "18",

    "-pix_fmt",
    "yuv420p",


    # ------------------------------------------------------
    # AUDIO
    # ------------------------------------------------------

    "-c:a",
    "aac",

    "-b:a",
    "192k",

    "-ar",
    "48000",


    # ------------------------------------------------------
    # EXACT DURATION
    # ------------------------------------------------------

    "-t",
    f"{duration:.6f}",


    # ------------------------------------------------------
    # MP4
    # ------------------------------------------------------

    "-movflags",
    "+faststart",

    str(OUTPUT_FILE),
]


# ==========================================================
# PRINT COMMAND
# ==========================================================

print()
print("=" * 80)
print("RENDERING SCENE 1 — ZOOM TEST")
print("=" * 80)
print()

print(
    f"Zoom: {ZOOM_START:.2f}x → {ZOOM_END:.2f}x"
)

print(
    f"Output: {OUTPUT_FILE}"
)

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