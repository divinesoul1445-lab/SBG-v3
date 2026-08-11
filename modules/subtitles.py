"""
Subtitle Generator (V3)

Creates subtitles for the four-scene Bhagavad Gita video.

The subtitle timing is based on the actual scene audio durations,
not estimated word counts.

Scene structure:

    Scene 1 text -> Scene 1 audio duration
    Scene 2 text -> Scene 2 audio duration
    Scene 3 text -> Scene 3 audio duration
    Scene 4 text -> Scene 4 audio duration
"""

from pathlib import Path
import re
import subprocess

from config import FFPROBE_PATH


class SubtitleGenerator:

    # =========================================================
    # SETTINGS
    # =========================================================

    MAX_WORDS_PER_LINE = 7

    MIN_SUBTITLE_DURATION = 0.8

    # =========================================================
    # PUBLIC METHOD
    # =========================================================

    def generate(
        self,
        scene_texts,
        scene_audio_files,
        output_folder: Path,
    ) -> Path:

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        subtitle_file = (
            output_folder
            / "subtitles.srt"
        )

        # -----------------------------------------------------
        # Validate
        # -----------------------------------------------------

        if not scene_texts:

            raise Exception(
                "No scene narration text supplied."
            )

        if not scene_audio_files:

            raise Exception(
                "No scene audio files supplied."
            )

        if len(scene_texts) != len(scene_audio_files):

            raise Exception(
                "Number of scene texts does not match "
                "number of scene audio files.\n"
                f"Texts: {len(scene_texts)}\n"
                f"Audio: {len(scene_audio_files)}"
            )

        # -----------------------------------------------------
        # Generate subtitles
        # -----------------------------------------------------

        subtitle_entries = []

        current_time = 0.0

        subtitle_index = 1

        for scene_number, (
            text,
            audio_file,
        ) in enumerate(
            zip(
                scene_texts,
                scene_audio_files,
            ),
            start=1,
        ):

            text = (
                str(text)
                .strip()
            )

            if not text:

                continue

            audio_file = Path(
                audio_file
            )

            if not audio_file.exists():

                raise FileNotFoundError(
                    f"Scene {scene_number} "
                    f"audio not found:\n"
                    f"{audio_file}"
                )

            audio_duration = (
                self._audio_duration(
                    audio_file
                )
            )

            print(
                f"Subtitle Scene {scene_number}: "
                f"{audio_duration:.2f}s"
            )

            # -------------------------------------------------
            # Split scene into subtitle chunks
            # -------------------------------------------------

            chunks = self._make_chunks(
                text
            )

            if not chunks:

                continue

            # -------------------------------------------------
            # Allocate the actual scene duration across
            # subtitle chunks according to word count.
            # -------------------------------------------------

            total_words = sum(
                len(chunk.split())
                for chunk in chunks
            )

            scene_start = current_time

            for chunk in chunks:

                chunk_words = len(
                    chunk.split()
                )

                if total_words > 0:

                    duration = (
                        audio_duration
                        * chunk_words
                        / total_words
                    )

                else:

                    duration = (
                        audio_duration
                        / len(chunks)
                    )

                start = current_time

                end = (
                    current_time
                    + duration
                )

                subtitle_entries.append(
                    {
                        "index": subtitle_index,
                        "start": start,
                        "end": end,
                        "text": chunk,
                    }
                )

                subtitle_index += 1

                current_time = end

            # -------------------------------------------------
            # IMPORTANT:
            #
            # Force the final subtitle of the scene to end
            # exactly at the actual audio boundary.
            #
            # This prevents Scene 4 from losing its subtitle
            # because of accumulated floating-point drift.
            # -------------------------------------------------

            current_time = (
                scene_start
                + audio_duration
            )

            if subtitle_entries:

                subtitle_entries[-1][
                    "end"
                ] = current_time

        # =====================================================
        # WRITE SRT
        # =====================================================

        with open(
            subtitle_file,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:

            for entry in subtitle_entries:

                f.write(
                    f"{entry['index']}\n"
                )

                f.write(
                    f"{self._format_time(entry['start'])}"
                    f" --> "
                    f"{self._format_time(entry['end'])}\n"
                )

                f.write(
                    f"{entry['text']}\n\n"
                )

        print(
            f"Subtitles written: "
            f"{subtitle_file}"
        )

        print(
            f"Subtitle entries: "
            f"{len(subtitle_entries)}"
        )

        return subtitle_file

    # =========================================================
    # CREATE SUBTITLE CHUNKS
    # =========================================================

    def _make_chunks(
        self,
        text: str,
    ):

        text = (
            text
            .replace("\r", " ")
            .replace("\n", " ")
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not text:

            return []

        # -----------------------------------------------------
        # First split at sentence boundaries.
        #
        # Includes:
        # . ! ?
        # Sanskrit । ॥
        # -----------------------------------------------------

        sentences = re.split(
            r"(?<=[.!?।॥])\s+",
            text,
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        chunks = []

        # -----------------------------------------------------
        # Break long sentences into readable subtitle lines.
        # -----------------------------------------------------

        for sentence in sentences:

            words = sentence.split()

            if len(words) <= self.MAX_WORDS_PER_LINE:

                chunks.append(
                    sentence
                )

                continue

            for start in range(
                0,
                len(words),
                self.MAX_WORDS_PER_LINE,
            ):

                chunk = " ".join(
                    words[
                        start:
                        start
                        + self.MAX_WORDS_PER_LINE
                    ]
                )

                chunks.append(
                    chunk
                )

        return chunks

    # =========================================================
    # AUDIO DURATION
    # =========================================================

    def _audio_duration(
        self,
        audio_file: Path,
    ) -> float:

        command = [

            str(FFPROBE_PATH),

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default="
            "noprint_wrappers=1:"
            "nokey=1",

            str(audio_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        value = (
            result.stdout
            .strip()
        )

        if not value:

            raise Exception(
                f"Unable to determine duration:\n"
                f"{audio_file}"
            )

        duration = float(
            value
        )

        if duration <= 0:

            raise Exception(
                f"Audio duration is zero:\n"
                f"{audio_file}"
            )

        return duration

    # =========================================================
    # SRT TIME
    # =========================================================

    def _format_time(
        self,
        seconds: float,
    ) -> str:

        # Prevent negative values
        seconds = max(
            0.0,
            seconds,
        )

        total_milliseconds = int(
            round(
                seconds * 1000
            )
        )

        hours = (
            total_milliseconds
            // 3_600_000
        )

        remainder = (
            total_milliseconds
            % 3_600_000
        )

        minutes = (
            remainder
            // 60_000
        )

        remainder = (
            remainder
            % 60_000
        )

        secs = (
            remainder
            // 1000
        )

        milliseconds = (
            remainder
            % 1000
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d},"
            f"{milliseconds:03d}"
        )