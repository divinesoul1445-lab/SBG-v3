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



def ensure_tracking_columns(excel_manager):
    """Add render/export tracking columns without changing Upload Status."""
    from openpyxl import load_workbook

    workbook_path = Path(excel_manager.excel_file)
    workbook = load_workbook(workbook_path)
    try:
        worksheet = workbook[excel_manager.SHEET_NAME]
        headers = {
            str(cell.value).strip(): cell.column
            for cell in worksheet[1]
            if cell.value is not None
        }
        for header in (
            "Render Status",
            "Local Export Status",
            "Google Drive Status",
        ):
            if header not in headers:
                worksheet.cell(1, worksheet.max_column + 1).value = header
        workbook.save(workbook_path)
    finally:
        workbook.close()


def update_tracking_status(excel_manager, chapter, verse, **updates):
    """Write status fields for one verse to the content workbook."""
    from openpyxl import load_workbook

    workbook_path = Path(excel_manager.excel_file)
    workbook = load_workbook(workbook_path)
    try:
        worksheet = workbook[excel_manager.SHEET_NAME]
        headers = {
            str(cell.value).strip(): cell.column
            for cell in worksheet[1]
            if cell.value is not None
        }
        for row in range(2, worksheet.max_row + 1):
            row_chapter = excel_manager._to_int(
                worksheet.cell(row, headers["Chapter"]).value
            )
            row_verse = excel_manager._to_int(
                worksheet.cell(row, headers["Verse"]).value
            )
            if row_chapter == chapter and row_verse == verse:
                for header, value in updates.items():
                    worksheet.cell(row, headers[header]).value = value
                workbook.save(workbook_path)
                return
        raise ValueError(f"Chapter {chapter}, Verse {verse} not found in workbook")
    finally:
        workbook.close()


def main():
    # Test Chapter 1, Verses 2 and 3.
    # Copy each completed video to both destinations immediately.
    import shutil

    pipeline = Pipeline()
    ensure_tracking_columns(pipeline.excel)
    failures = []
    successes = []

    destinations = [
        Path("final_videos"),
        Path(r"G:\\My Drive\\Final Verses"),
    ]

    for destination in destinations:
        destination.mkdir(parents=True, exist_ok=True)

    for verse_number in range(4, 11):
        print("\\n" + "=" * 60)
        print(f"PROCESSING CHAPTER 1, VERSE {verse_number}")
        print("=" * 60)

        try:
            update_tracking_status(
                pipeline.excel, 1, verse_number,
                **{
                    "Render Status": "Processing",
                    "Local Export Status": "Pending",
                    "Google Drive Status": "Pending",
                },
            )
            success = pipeline.run(chapter=1, verse=verse_number)

            if not success:
                update_tracking_status(
                    pipeline.excel, 1, verse_number,
                    **{"Render Status": "Failed"},
                )
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

            if source_video.stat().st_size <= 0:
                update_tracking_status(
                    pipeline.excel, 1, verse_number,
                    **{"Render Status": "Failed"},
                )
                failures.append((verse_number, f"merged video is empty: {source_video}"))
                print(f"FAILED: Empty final video: {source_video}")
                continue

            update_tracking_status(
                pipeline.excel, 1, verse_number,
                **{"Render Status": "Completed"},
            )

            target_name = f"Chapter_001Verse_{verse_number:03d}.mp4"
            copy_errors = []

            for destination in destinations:
                target = destination / target_name
                try:
                    shutil.copy2(source_video, target)
                    if not target.is_file() or target.stat().st_size != source_video.stat().st_size:
                        raise IOError("Copied file verification failed")
                    status_header = (
                        "Local Export Status"
                        if destination == destinations[0]
                        else "Google Drive Status"
                    )
                    update_tracking_status(
                        pipeline.excel, 1, verse_number,
                        **{status_header: "Completed"},
                    )
                    print(f"COPIED AND VERIFIED: {target.resolve()}")
                except Exception as copy_exc:
                    status_header = (
                        "Local Export Status"
                        if destination == destinations[0]
                        else "Google Drive Status"
                    )
                    update_tracking_status(
                        pipeline.excel, 1, verse_number,
                        **{status_header: "Failed"},
                    )
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
