"""
Subtitle Generator

Creates an SRT subtitle file from narration text.
"""

from __future__ import annotations

import re
from pathlib import Path


class SubtitleGenerator:

    WORDS_PER_SECOND = 2.5

    MIN_DURATION = 2.0

    MAX_DURATION = 6.0

    # ---------------------------------------------------------

    def generate(
        self,
        text: str,
        output_folder: Path,
    ) -> Path:

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        subtitle_file = output_folder / "subtitles.srt"

        sentences = self._split_sentences(text)

        current_time = 0.0

        with open(
            subtitle_file,
            "w",
            encoding="utf-8",
        ) as f:

            for index, sentence in enumerate(sentences, start=1):

                words = len(sentence.split())

                duration = words / self.WORDS_PER_SECOND

                duration = max(
                    self.MIN_DURATION,
                    min(duration, self.MAX_DURATION),
                )

                start = self._format_time(current_time)

                end = self._format_time(current_time + duration)

                f.write(
                    f"{index}\n"
                    f"{start} --> {end}\n"
                    f"{sentence}\n\n"
                )

                current_time += duration

        return subtitle_file

    # ---------------------------------------------------------

    def _split_sentences(
        self,
        text: str,
    ):

        parts = re.split(
            r'(?<=[.!?])\s+',
            text.strip(),
        )

        return [
            p.strip()
            for p in parts
            if p.strip()
        ]

    # ---------------------------------------------------------

    def _format_time(
        self,
        seconds: float,
    ):

        hours = int(seconds // 3600)

        minutes = int((seconds % 3600) // 60)

        secs = int(seconds % 60)

        millis = int((seconds - int(seconds)) * 1000)

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d},"
            f"{millis:03d}"
        )