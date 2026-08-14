from pathlib import Path

from modules.sheet import ExcelContentManager
from modules.subtitles import SubtitleGenerator


# =========================================================
# CONFIG
# =========================================================

CHAPTER = 1
VERSE = 1

BASE_DIR = Path(
    __file__
).resolve().parent

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

VERSE_FOLDER = (
    OUTPUT_DIR
    / f"chapter_{CHAPTER:03d}"
    / f"verse_{VERSE:03d}"
)


# =========================================================
# GET VERSE
# =========================================================

def get_verse(
    excel,
):

    for row in excel._rows():

        try:

            chapter = int(
                row.get(
                    "Chapter"
                )
            )

            verse = int(
                row.get(
                    "Verse"
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        if (
            chapter == CHAPTER
            and verse == VERSE
        ):

            return row

    raise Exception(
        f"Chapter {CHAPTER}, Verse {VERSE} "
        f"was not found in Excel."
    )


# =========================================================
# GET APPROVED SCENE NARRATIONS
# =========================================================

def get_scene_narrations(
    verse,
):

    scenes = [

        verse.get(
            "Scene 1 Narration"
        ),

        verse.get(
            "Scene 2 Narration"
        ),

        verse.get(
            "Scene 3 Narration"
        ),

        verse.get(
            "Scene 4 Narration"
        ),

    ]

    for index, narration in enumerate(
        scenes,
        start=1,
    ):

        if (
            narration is None
            or not str(
                narration
            ).strip()
        ):

            raise Exception(
                f"Scene {index} narration is empty "
                f"for Chapter {CHAPTER}, "
                f"Verse {VERSE}."
            )

    return [
        str(
            narration
        ).strip()
        for narration in scenes
    ]


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("SBG V3 — SUBTITLE TEST")
    print("=" * 70)
    print()

    # -----------------------------------------------------
    # Excel
    # -----------------------------------------------------

    excel = ExcelContentManager()

    print(
        "Loading approved narration from Excel..."
    )

    verse = get_verse(
        excel
    )

    scene_texts = get_scene_narrations(
        verse
    )

    print(
        "✓ Approved Scene 1–4 narrations loaded."
    )

    print()

    # -----------------------------------------------------
    # Verify verse folder
    # -----------------------------------------------------

    if not VERSE_FOLDER.exists():

        raise FileNotFoundError(
            f"Verse output folder not found:\n"
            f"{VERSE_FOLDER}\n\n"
            f"Run test_tts.py first."
        )

    # -----------------------------------------------------
    # Find audio
    # -----------------------------------------------------

    scene_audio_files = []

    for scene_number in range(
        1,
        5,
    ):

        scene_folder = (
            VERSE_FOLDER
            / f"scene{scene_number}"
        )

        if not scene_folder.exists():

            raise FileNotFoundError(
                f"Scene folder not found:\n"
                f"{scene_folder}"
            )

        audio_file = (
            scene_folder
            / "narration.mp3"
        )

        print(
            f"Scene {scene_number} audio:"
        )

        print(
            f"  {audio_file}"
        )

        if not audio_file.exists():

            raise FileNotFoundError(
                f"Scene {scene_number} audio not found:\n"
                f"{audio_file}\n\n"
                f"Run test_tts.py first."
            )

        if audio_file.stat().st_size <= 0:

            raise RuntimeError(
                f"Scene {scene_number} audio "
                f"is empty:\n"
                f"{audio_file}"
            )

        print(
            "  ✓ Found"
        )

        print()

        scene_audio_files.append(
            audio_file
        )

    # =====================================================
    # SUBTITLE GENERATOR
    # =====================================================

    generator = SubtitleGenerator()

    # -----------------------------------------------------
    # Generate
    # -----------------------------------------------------

    subtitle_files = generator.generate(
        scene_texts=scene_texts,
        scene_audio_files=scene_audio_files,
        output_folder=VERSE_FOLDER,
    )

    # =====================================================
    # RESULTS
    # =====================================================

    print()
    print("=" * 70)
    print("SUBTITLE GENERATION COMPLETE")
    print("=" * 70)
    print()

    for index, subtitle_file in enumerate(
        subtitle_files,
        start=1,
    ):

        subtitle_file = Path(
            subtitle_file
        )

        print(
            f"Scene {index}:"
        )

        print(
            f"  {subtitle_file}"
        )

        if subtitle_file.exists():

            print(
                "  ✓ Created"
            )

        else:

            print(
                "  ✗ NOT CREATED"
            )

        print()

    # =====================================================
    # PRINT SRT CONTENT
    # =====================================================

    print("=" * 70)
    print("GENERATED SRT FILES")
    print("=" * 70)

    for index, subtitle_file in enumerate(
        subtitle_files,
        start=1,
    ):

        subtitle_file = Path(
            subtitle_file
        )

        print()
        print(
            f"--- SCENE {index} ---"
        )

        print()

        print(
            subtitle_file.read_text(
                encoding="utf-8"
            )
        )


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