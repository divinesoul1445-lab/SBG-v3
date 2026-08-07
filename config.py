"""
SBG AI v2

Global configuration
"""

from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

FAL_KEY = os.getenv("FAL_KEY")

DEBUG = False

LIPSYNC_MODE = "test"


# =====================================================
# PROJECT
# =====================================================

PROJECT_NAME = "SBG AI v3"

ROOT_DIR = Path(__file__).resolve().parent

# =====================================================
# DATA
# =====================================================

DATA_DIR = ROOT_DIR / "data"

DATABASE_FILE = DATA_DIR / "bhagavad_gita.db"

EXCEL_FILE = DATA_DIR / "Bhagavad_Gita.xlsx"

# =====================================================
# OUTPUT
# =====================================================

OUTPUT_DIR = ROOT_DIR / "output"

AUDIO_DIR = OUTPUT_DIR / "audio"

IMAGE_DIR = OUTPUT_DIR / "images"

SUBTITLE_DIR = OUTPUT_DIR / "subtitles"

VIDEO_DIR = OUTPUT_DIR / "videos"

THUMBNAIL_DIR = OUTPUT_DIR / "thumbnails"

LOG_DIR = ROOT_DIR / "logs"

# =====================================================
# ASSETS
# =====================================================

ASSET_DIR = ROOT_DIR / "assets"

FONT_DIR = ASSET_DIR / "fonts"

MUSIC_DIR = ASSET_DIR / "music"

OVERLAY_DIR = ASSET_DIR / "overlays"

AVATAR_DIR = ASSET_DIR / "avatars"

# =====================================================
# PROMPTS
# =====================================================

PROMPT_DIR = ROOT_DIR / "prompts"

# =====================================================
# OLLAMA
# =====================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

# OLLAMA_MODEL = os.getenv(
#     "OLLAMA_MODEL",
#     "qwen3:8b"
# )

#OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_MODEL = "qwen3:8b"

# =====================================================
# FAL AI
# =====================================================

FAL_KEY = os.getenv("FAL_KEY")

FAL_MODEL = "fal-ai/flux-1/dev"

# =====================================================
# VIDEO
# =====================================================

VIDEO_WIDTH = 1080

VIDEO_HEIGHT = 1920

FPS = 30

IMAGE_DURATION = 5

TRANSITION_DURATION = 0.6

# =====================================================
# AUDIO
# =====================================================

VOICE = "en-IN-PrabhatNeural"

BACKGROUND_MUSIC = (
    MUSIC_DIR / "background.mp3"
)

BACKGROUND_MUSIC_VOLUME = 0.15

# =====================================================
# SUBTITLE
# =====================================================

FONT_FILE = FONT_DIR / "NotoSans-Regular.ttf"

FONT_SIZE = 56

FONT_COLOR = "white"

STROKE_COLOR = "black"

STROKE_WIDTH = 3

# =====================================================
# IMAGE GENERATION
# =====================================================

IMAGES_PER_VERSE = 6

IMAGE_SIZE = "1080x1920"

MAX_RETRIES = 3

REQUEST_TIMEOUT = 300

# =====================================================
# CREATE DIRECTORIES
# =====================================================

DIRECTORIES = [

    DATA_DIR,

    OUTPUT_DIR,

    AUDIO_DIR,

    IMAGE_DIR,

    SUBTITLE_DIR,

    VIDEO_DIR,

    THUMBNAIL_DIR,

    LOG_DIR,

]

for directory in DIRECTORIES:

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

from pathlib import Path

BASE_DIR = Path(__file__).parent

FFMPEG_PATH = str(
    BASE_DIR
    / "tools"
    / "ffmpeg"
    / "bin"
    / "ffmpeg.exe"
)

FFPROBE_PATH = str(
    BASE_DIR
    / "tools"
    / "ffmpeg"
    / "bin"
    / "ffprobe.exe"
)