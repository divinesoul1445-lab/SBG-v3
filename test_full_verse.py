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


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 80)
    print("SBG V3 — FULL VERSE VIDEO TEST")
    print("=" * 80)
    print()

    print(
        f"Verse folder:\n"
        f"  {VERSE_FOLDER}"
    )

    print()

    # -----------------------------------------------------
    # Build Scene 1 → Scene 4 paths
    # -----------------------------------------------------

    scene_images = []
    scene_audio = []
    scene_subtitles = []

    for scene_number in range(1, 5):

        scene_folder = (
            VERSE_FOLDER
            / f"scene{scene_number}"
        )

        image_file = (
            scene_folder
            / f"scene{scene_number}_composed.png"
        )

        audio_file = (
            scene_folder
            / "narration.mp3"
        )

        subtitle_file = (
            scene_folder
            / "subtitles.srt"
        )

        print(
            f"Scene {scene_number}:"
        )

        print(
            f"  Image:     {image_file}"
        )

        print(
            f"  Audio:     {audio_file}"
        )

        print(
            f"  Subtitles: {subtitle_file}"
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        for label, path in (
            ("Image", image_file),
            ("Audio", audio_file),
            ("Subtitles", subtitle_file),
        ):

            if not path.exists():

                raise FileNotFoundError(
                    f"\nScene {scene_number} "
                    f"{label} not found:\n"
                    f"{path}"
                )

            if path.stat().st_size == 0:

                raise RuntimeError(
                    f"\nScene {scene_number} "
                    f"{label} is empty:\n"
                    f"{path}"
                )

            print(
                f"    ✓ {label} found"
            )

        scene_images.append(
            image_file
        )

        scene_audio.append(
            audio_file
        )

        scene_subtitles.append(
            subtitle_file
        )

        print()

    # =====================================================
    # RENDER
    # =====================================================

    renderer = VideoRenderer()

    print("=" * 80)
    print("STARTING FULL VERSE RENDER")
    print("=" * 80)
    print()

    result = renderer.render_verse(
        scene_images=scene_images,
        scene_audio_files=scene_audio,
        scene_subtitle_files=scene_subtitles,
        output_folder=VERSE_FOLDER,
        merge=True,
    )

    # =====================================================
    # RESULT
    # =====================================================

    print()
    print("=" * 80)
    print("FULL VERSE TEST COMPLETE")
    print("=" * 80)
    print()

    print(
        "Scene videos:"
    )

    for index, path in enumerate(
        result["scene_videos"],
        start=1,
    ):

        print(
            f"  Scene {index}:"
        )

        print(
            f"    {path}"
        )

    print()

    final_video = result[
        "final_video"
    ]

    if final_video:

        print(
            "Final video:"
        )

        print(
            f"  {final_video}"
        )

        print()

        if Path(final_video).exists():

            print(
                "✓ Final video exists."
            )

        else:

            print(
                "⚠ Final video was not found."
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
        print("=" * 80)
        print("FULL VERSE TEST FAILED")
        print("=" * 80)
        print()

        print(
            str(e)
        )

        print()

        raise