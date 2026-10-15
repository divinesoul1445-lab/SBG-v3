from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parent
output = root / "output"
destination = root / "final_videos"
destination.mkdir(parents=True, exist_ok=True)

copied = 0

for video in output.glob("chapter_*/verse_*/final/merged_video.mp4"):
    match = re.fullmatch(
        r"chapter_(\d+)/verse_(\d+)",
        f"{video.parents[2].name}/{video.parents[1].name}"
    )
    if not match:
        continue

    chapter, verse = map(int, match.groups())
    target = destination / f"Chapter_{chapter:03d}Verse_{verse:03d}.mp4"
    shutil.copy2(video, target)
    print(f"Copied: {video} -> {target.name}")
    copied += 1

print(f"\nExport complete: {copied} video(s) copied to {destination}")
