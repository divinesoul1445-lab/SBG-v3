"""
Subtitle Generator

Creates subtitles.srt from narration.
"""

from pathlib import Path


class SubtitleGenerator:

    def generate(

        self,

        narration: str,

        output_folder: Path,

    ) -> Path:

        output_folder.mkdir(

            parents=True,

            exist_ok=True,

        )

        subtitle_file = output_folder / "subtitles.srt"

        lines = [

            line.strip()

            for line in narration.split(". ")

            if line.strip()

        ]

        total_words = len(narration.split())

        total_duration = max(

            total_words / 2.5,

            1,

        )

        seconds_per_line = total_duration / len(lines)

        current = 0

        with open(

            subtitle_file,

            "w",

            encoding="utf-8",

        ) as f:

            for index, line in enumerate(lines):

                start = current

                end = current + seconds_per_line

                f.write(

f"""{index+1}
00:00:{int(start):02d},000 --> 00:00:{int(end):02d},000
{line}

"""
                )

                current = end

        return subtitle_file