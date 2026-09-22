import json
import subprocess
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE = Path(r"C:\SBG\SBG-v4")

SCENE = (
    BASE
    / "output"
    / "chapter_001"
    / "verse_001"
    / "scene2"
)

JSON_FILE = SCENE / "narration.json"
ASS_FILE = SCENE / "shloka_overlay.ass"
OUTPUT_FILE = SCENE / "shloka_overlay.webm"

FFMPEG = BASE / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# ============================================================
# COLORS
# ============================================================

WHITE = "&H00FFFFFF"
TURQUOISE = "&H00D7FFFF"

# ============================================================
# LOAD JSON
# ============================================================

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

words = data["words"]

# ============================================================
# ASS TIME
# ============================================================

def ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)

    s = seconds % 60
    whole = int(s)
    centiseconds = int(round((s - whole) * 100))

    if centiseconds >= 100:
        whole += 1
        centiseconds = 0

    return f"{h}:{m:02d}:{whole:02d}.{centiseconds:02d}"


# ============================================================
# ASS HEADER
# ============================================================

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

Style: Normal,Noto Sans Devanagari,58,{WHITE},&H00000000,&H00120A05,&H00000000,1,0,0,0,100,100,2,0,1,3,2,2,90,90,360,0
Style: Highlight,Noto Sans Devanagari,58,{TURQUOISE},&H00000000,&H00120A05,&H00000000,1,0,0,0,100,100,2,0,1,3,2,2,90,90,360,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# ============================================================
# CREATE TIMED HIGHLIGHTS
# ============================================================

for index, current in enumerate(words):

    start = current["start"]
    end = current["end"]

    rendered = []

    for i, item in enumerate(words):

        text = item["text"].strip()

        if i == index:
            rendered.append(
                r"{\rHighlight}" + text + r"{\rNormal}"
            )
        else:
            rendered.append(text)

    first_line = " ".join(rendered[:6])
    second_line = " ".join(rendered[6:])

    text = first_line + r"\N" + second_line

    ass += (
        f"Dialogue: 0,"
        f"{ass_time(start)},"
        f"{ass_time(end)},"
        f"Normal,"
        f",0,0,360,,"
        f"{text}\n"
    )

# ============================================================
# WRITE ASS
# ============================================================

with open(ASS_FILE, "w", encoding="utf-8-sig") as f:
    f.write(ass)

print(f"Created ASS: {ASS_FILE}")

# ============================================================
# TOTAL DURATION
# ============================================================

duration = max(float(x["end"]) for x in words) + 0.15

# ============================================================
# IMPORTANT:
# Run FFmpeg from the Scene 2 directory.
# Therefore the ASS filter only needs:
#
#     ass=shloka_overlay.ass
#
# This avoids Windows path parsing problems.
# ============================================================

cmd = [
    str(FFMPEG),
    "-y",

    "-f", "lavfi",
    "-i",
    f"color=c=black@0.0:s={WIDTH}x{HEIGHT}:r={FPS},format=rgba",

    "-t",
    str(duration),

    "-vf",
    "ass=shloka_overlay.ass,format=yuva420p",

    "-c:v",
    "libvpx-vp9",

    "-pix_fmt",
    "yuva420p",

    "-b:v",
    "2M",

    "-an",

    "shloka_overlay.webm",
]

print("\nRunning FFmpeg...\n")

subprocess.run(
    cmd,
    cwd=str(SCENE),
    check=True
)

print("\n========================================")
print("SHLOKA OVERLAY CREATED SUCCESSFULLY")
print("========================================")
print(OUTPUT_FILE)