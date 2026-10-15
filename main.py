from pathlib import Path
import shutil
import re

from modules.pipeline import Pipeline


def clear_output_folder():
    output_folder = Path("output")

    if output_folder.exists():
        print()
        print("=" * 80)
        print("CLEANING PREVIOUS OUTPUT")
        print("=" * 80)
        print(f"Removing: {output_folder.resolve()}")
        shutil.rmtree(output_folder)
        print("Previous output folder removed.")

    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"Fresh output folder created: {output_folder.resolve()}")
    print()


def export_final_videos():
    output_folder = Path("output")
    destination = Path("final_videos")
    destination.mkdir(parents=True, exist_ok=True)

    copied = 0

    for video in output_folder.glob(
        "chapter_*/verse_*/final/merged_video.mp4"
    ):
        match = re.fullmatch(
            r"chapter_(\d+)/verse_(\d+)",
            f"{video.parents[2].name}/{video.parents[1].name}",
        )

        if not match:
            continue

        chapter, verse = map(int, match.groups())
        target = destination / (
            f"Chapter_{chapter:03d}Verse_{verse:03d}.mp4"
        )

        shutil.copy2(video, target)
        print(f"Exported: {target}")

        copied += 1

    print()
    print(f"Export complete: {copied} video(s) in {destination.resolve()}")


def main():
    clear_output_folder()

    pipeline = Pipeline()
    pipeline.run()

    export_final_videos()


if __name__ == "__main__":
    import time

    start_time = time.perf_counter()

    try:
        main()
    finally:
        elapsed = time.perf_counter() - start_time
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        print()
        print("=" * 60)
        print(
            f"TOTAL PIPELINE TIME: "
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        print("=" * 60)
