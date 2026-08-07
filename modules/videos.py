"""
Video Renderer (V3)

Creates the final Shorts video from:

- Images
- Narration Audio

(Subtitles will be added later.)
"""

from pathlib import Path
import subprocess


from config import FFMPEG_PATH, FFPROBE_PATH
from modules.logger import Logger


class VideoRenderer:

    def __init__(self):

        self.ffmpeg = FFMPEG_PATH
        self.ffprobe = FFPROBE_PATH


    # --------------------------------------------------
    # Audio Duration
    # --------------------------------------------------

    def _audio_duration(
        self,
        audio_file: Path,
    ) -> float:

        command = [

            self.ffprobe,

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default=noprint_wrappers=1:nokey=1",

            str(audio_file),

        ]
        print("\n" + "=" * 80)
        print("FFMPEG COMMAND")
        print("=" * 80)

        for item in command:
            print(item)

        print("=" * 80 + "\n")

        print("FFmpeg executable :", self.ffmpeg)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )


        return float(
            result.stdout.strip()
        )

    # --------------------------------------------------
    # Render Video
    # --------------------------------------------------

    def render(

        self,

        images,

        audio_file,

        subtitle_file,

        output_folder,

    ):

        output_folder = Path(output_folder)

        output_folder.mkdir(

            parents=True,

            exist_ok=True,

        )

        output_file = output_folder / "final_video.mp4"

        total_duration = self._audio_duration(
            audio_file
        )

        image_duration = total_duration / len(images)

        command = [

            self.ffmpeg,

            "-y",

        ]

        # --------------------------------------------------
        # Inputs
        # --------------------------------------------------

        for image in images:

            command.extend([

                "-loop", "1",

                "-t", str(image_duration),

                "-i", str(image),

            ])

        command.extend([

            "-i",

            str(audio_file),

        ])

        # --------------------------------------------------
        # Video Filters
        # --------------------------------------------------

        filters = []

        for i in range(len(images)):

            filters.append(

                f"[{i}:v]"
                f"scale=1080:1920,"
                f"fps=30,"
                f"format=yuv420p,"
                f"setsar=1"
                f"[v{i}]"

            )

        fade = 0.5

        current = "v0"

        offset = image_duration - fade

        for i in range(1, len(images)):

            out = f"x{i}"

            filters.append(

                f"[{current}][v{i}]"

                f"xfade="

                f"transition=fade:"

                f"duration={fade}:"

                f"offset={offset}"

                f"[{out}]"

            )

            current = out

            offset += image_duration - fade

        filter_complex = ";".join(filters)

        # --------------------------------------------------
        # FFmpeg
        # --------------------------------------------------

        command.extend([

            "-filter_complex",

            filter_complex,

            "-map",

            f"[{current}]",

            "-map",

            f"{len(images)}:a",

            "-c:v",

            "libx264",

            "-preset",

            "medium",

            "-crf",

            "18",

            "-pix_fmt",

            "yuv420p",

            "-c:a",

            "aac",

            "-b:a",

            "192k",

            "-shortest",

            str(output_file),

        ])

        Logger.info(
            "Rendering video..."
        )

        subprocess.run(

            command,

            check=True,

        )

        Logger.success(
            f"Saved -> {output_file}"
        )

        return output_file