from pathlib import Path

from modules.sheet import ExcelContentManager
from modules.tts import TTSGenerator


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
    print("SBG V3 — TTS TEST")
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

    scenes = get_scene_narrations(
        verse
    )

    print(
        "✓ Approved Scene 1–4 narrations loaded."
    )

    print()

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    VERSE_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Verse output folder:"
    )

    print(
        f"  {VERSE_FOLDER}"
    )

    print()

    # -----------------------------------------------------
    # TTS
    # -----------------------------------------------------

    tts = TTSGenerator()

    audio_files = []

    for scene_number, narration in enumerate(
        scenes,
        start=1,
    ):

        print()
        print("-" * 70)
        print(
            f"SCENE {scene_number}"
        )
        print("-" * 70)

        scene_folder = (
            VERSE_FOLDER
            / f"scene{scene_number}"
        )

        scene_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"Scene folder:"
        )

        print(
            f"  {scene_folder}"
        )

        print()

        print(
            "Narration:"
        )

        print(
            narration
        )

        print()

        # -------------------------------------------------
        # Generate
        # -------------------------------------------------

        audio_file = tts.generate_scene(
            scene_number=scene_number,
            text=narration,
            output_folder=scene_folder,
        )

        audio_file = Path(
            audio_file
        )

        # -------------------------------------------------
        # Verify
        # -------------------------------------------------

        if not audio_file.exists():

            raise FileNotFoundError(
                f"Scene {scene_number} audio "
                f"was not created:\n"
                f"{audio_file}"
            )

        if audio_file.stat().st_size <= 0:

            raise RuntimeError(
                f"Scene {scene_number} audio "
                f"is empty:\n"
                f"{audio_file}"
            )

        print()

        print(
            f"✓ Scene {scene_number} audio created:"
        )

        print(
            f"  {audio_file}"
        )

        print(
            f"  Size: "
            f"{audio_file.stat().st_size:,} bytes"
        )

        audio_files.append(
            audio_file
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print()
    print("=" * 70)
    print("TTS TEST COMPLETE")
    print("=" * 70)
    print()

    for index, audio_file in enumerate(
        audio_files,
        start=1,
    ):

        print(
            f"Scene {index}: "
            f"{audio_file}"
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