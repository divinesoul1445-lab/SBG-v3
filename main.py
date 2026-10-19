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
    # Test Chapter 1, Verses 2 and 3.
    # Copy each completed video to both destinations immediately.
    import shutil

    pipeline = Pipeline()
    failures = []
    successes = []

    destinations = [
        Path("final_videos"),
        Path(r"G:\\My Drive\\Final Verses"),
    ]

    for destination in destinations:
        destination.mkdir(parents=True, exist_ok=True)

    for verse_number in (2, 3):
        print("\\n" + "=" * 60)
        print(f"PROCESSING CHAPTER 1, VERSE {verse_number}")
        print("=" * 60)

        try:
            success = pipeline.run(chapter=1, verse=verse_number)

            if not success:
                failures.append((verse_number, "pipeline returned False"))
                print(f"FAILED: Verse {verse_number}: pipeline returned False")
                continue

            source_video = (
                Path("output")
                / "chapter_001"
                / f"verse_{verse_number:03d}"
                / "final"
                / "merged_video.mp4"
            )

            if not source_video.is_file():
                failures.append((
                    verse_number,
                    f"merged video not found: {source_video}"
                ))
                print(f"FAILED TO COPY: {source_video} not found")
                continue

            target_name = f"Chapter_001Verse_{verse_number:03d}.mp4"
            copy_errors = []

            for destination in destinations:
                target = destination / target_name
                try:
                    shutil.copy2(source_video, target)
                    print(f"COPIED: {target.resolve()}")
                except Exception as copy_exc:
                    copy_errors.append(f"{target}: {copy_exc}")
                    print(f"COPY FAILED: {target}: {copy_exc}")

            if copy_errors:
                failures.append((verse_number, "; ".join(copy_errors)))
            else:
                successes.append(verse_number)
                print(f"SUCCESS: Verse {verse_number} copied to both folders.")

        except Exception as exc:
            failures.append((verse_number, str(exc)))
            print(f"FAILED: Verse {verse_number}: {exc}")

    print("\\n" + "=" * 60)
    print(f"Successfully copied to both folders: {successes}")
    print(f"Failures: {len(failures)}")

    for verse_number, error in failures:
        print(f"Verse {verse_number}: {error}")


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
