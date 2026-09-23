import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.videos import VideoRenderer

PROJECT_ROOT = Path(r"C:\SBG\SBG-v4")

VERSE_DIR = (
    PROJECT_ROOT
    / "output"
    / "chapter_001"
    / "verse_001"
)

SCENES = [1, 2, 3, 4]


def render_scene(renderer, scene_number):
    scene_dir = VERSE_DIR / f"scene{scene_number}"

    image_file = scene_dir / "composed_image.png"
    audio_file = scene_dir / "narration.mp3"
    subtitle_file = scene_dir / "subtitles.srt"
    shloka_file = scene_dir / "shloka_overlay.ass"
    output_file = scene_dir / "scene_video.mp4"

    print("\n")
    print("=" * 70)
    print(f"RENDERING SCENE {scene_number}")
    print("=" * 70)

    required = [
        image_file,
        audio_file,
        shloka_file,
    ]

    for file in required:
        if not file.exists():
            raise FileNotFoundError(
                f"Missing required file for Scene {scene_number}:\n{file}"
            )

    # Subtitles are optional for now.
    # We will fix the subtitle system later.
    if not subtitle_file.exists():
        subtitle_file = None

    renderer.render_scene_2(
        image_file=image_file,
        audio_file=audio_file,
        subtitle_file=subtitle_file,
        shloka_overlay=shloka_file,
        output_file=output_file,
    )

    print(f"\nScene {scene_number} completed:")
    print(output_file)


def main():
    print("=" * 70)
    print("SBG - RENDER ALL FOUR SCENES")
    print("=" * 70)
    print(f"Verse directory: {VERSE_DIR}")

    renderer = VideoRenderer()

    for scene_number in SCENES:
        render_scene(renderer, scene_number)

    print("\n")
    print("=" * 70)
    print("ALL FOUR SCENES RENDERED SUCCESSFULLY")
    print("=" * 70)

    for scene_number in SCENES:
        output_file = (
            VERSE_DIR
            / f"scene{scene_number}"
            / "scene_video.mp4"
        )

        print(f"Scene {scene_number}: {output_file}")


if __name__ == "__main__":
    main()