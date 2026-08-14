from pathlib import Path

from modules.videos import VideoRenderer


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

VERSE_FOLDER = (
    BASE_DIR
    / "output"
    / "chapter_001"
    / "verse_001"
)

SCENE_NUMBER = 1

SCENE_FOLDER = (
    VERSE_FOLDER
    / f"scene{SCENE_NUMBER}"
)

IMAGE_FILE = (
    SCENE_FOLDER
    / f"scene{SCENE_NUMBER}_composed.png"
)

AUDIO_FILE = (
    SCENE_FOLDER
    / "narration.mp3"
)

SUBTITLE_FILE = (
    SCENE_FOLDER
    / "subtitles.srt"
)

OUTPUT_FILE = (
    SCENE_FOLDER
    / f"scene{SCENE_NUMBER}_test.mp4"
)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("SBG V3 — SINGLE SCENE VIDEO TEST")
    print("=" * 70)
    print()

    print("Scene folder:")
    print(
        f"  {SCENE_FOLDER}"
    )

    print()

    # -----------------------------------------------------
    # Validate files
    # -----------------------------------------------------

    files = {
        "Image": IMAGE_FILE,
        "Audio": AUDIO_FILE,
        "Subtitles": SUBTITLE_FILE,
    }

    for name, path in files.items():

        print(
            f"{name}:"
        )

        print(
            f"  {path}"
        )

        if not path.exists():

            raise FileNotFoundError(
                f"{name} not found:\n"
                f"{path}"
            )

        if path.stat().st_size <= 0:

            raise RuntimeError(
                f"{name} exists but is empty:\n"
                f"{path}"
            )

        print(
            "  ✓ Found"
        )

        print()

    # -----------------------------------------------------
    # Renderer
    # -----------------------------------------------------

    renderer = VideoRenderer()

    print(
        "Rendering Scene 1..."
    )

    print()

    result = renderer.render_scene(
        image_file=IMAGE_FILE,
        audio_file=AUDIO_FILE,
        subtitle_file=SUBTITLE_FILE,
        output_file=OUTPUT_FILE,
    )

    result = Path(
        result
    )

    # -----------------------------------------------------
    # Verify
    # -----------------------------------------------------

    print()

    if not result.exists():

        raise RuntimeError(
            "Video rendering finished but "
            "output file was not created."
        )

    if result.stat().st_size <= 0:

        raise RuntimeError(
            "Video was created but is empty."
        )

    print("=" * 70)
    print("VIDEO TEST COMPLETE")
    print("=" * 70)
    print()

    print(
        "Output:"
    )

    print(
        f"  {result}"
    )

    print()

    print(
        f"Size: "
        f"{result.stat().st_size:,} bytes"
    )

    print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()

        print(
            str(e)
        )

        print()

        raise