"""
Subtitle Generator (V3)

Creates one subtitle file for each scene.

Architecture:

    Scene 1 narration + Scene 1 audio
        -> scene1/subtitles.srt

    Scene 2 narration + Scene 2 audio
        -> scene2/subtitles.srt

    Scene 3 narration + Scene 3 audio
        -> scene3/subtitles.srt

    Scene 4 narration + Scene 4 audio
        -> scene4/subtitles.srt

Subtitle timing is based on the ACTUAL duration
of each scene's narration audio.

No word-per-second estimation is used for the
overall scene duration.
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
    ) -> list[Path]:

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------------------
        # Validate scene text list
        # -----------------------------------------------------

        if not scene_texts:

            raise Exception(
                "No scene narration text supplied."
            )

        # -----------------------------------------------------
        # Validate audio list
        # -----------------------------------------------------

        if not scene_audio_files:

            raise Exception(
                "No scene audio files supplied."
            )

        # -----------------------------------------------------
        # Validate counts
        # -----------------------------------------------------

        if len(scene_texts) != len(
            scene_audio_files
        ):

            raise Exception(
                "Number of scene texts does not match "
                "number of scene audio files.\n"
                f"Texts: {len(scene_texts)}\n"
                f"Audio: {len(scene_audio_files)}"
            )

        # -----------------------------------------------------
        # Generate one SRT per scene
        # -----------------------------------------------------

        subtitle_files = []

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

            # -------------------------------------------------
            # Scene folder
            # -------------------------------------------------

            scene_folder = (
                output_folder
                / f"scene{scene_number}"
            )

            scene_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            # -------------------------------------------------
            # Subtitle file
            # -------------------------------------------------

            subtitle_file = (
                scene_folder
                / "subtitles.srt"
            )

            # -------------------------------------------------
            # Validate text
            # -------------------------------------------------

            text = str(
                text
            ).strip()

            if not text:

                raise Exception(
                    f"Scene {scene_number} "
                    f"narration is empty."
                )

            # -------------------------------------------------
            # Validate audio
            # -------------------------------------------------

            audio_file = Path(
                audio_file
            )

            if not audio_file.exists():

                raise FileNotFoundError(
                    f"Scene {scene_number} "
                    f"audio not found:\n"
                    f"{audio_file}"
                )

            if audio_file.stat().st_size <= 0:

                raise Exception(
                    f"Scene {scene_number} "
                    f"audio is 0 KB:\n"
                    f"{audio_file}"
                )

            # -------------------------------------------------
            # Actual audio duration
            # -------------------------------------------------

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
            # Split narration into chunks
            # -------------------------------------------------

            chunks = self._make_chunks(
                text
            )

            if not chunks:

                raise Exception(
                    f"Scene {scene_number} "
                    f"produced no subtitle chunks."
                )

            # -------------------------------------------------
            # Create subtitle timing
            # -------------------------------------------------

            entries = (
                self._create_entries(
                    chunks,
                    audio_duration,
                )
            )

            # -------------------------------------------------
            # Write SRT
            # -------------------------------------------------

            self._write_srt(
                subtitle_file,
                entries,
            )

            print(
                f"Scene {scene_number} subtitles written:"
            )

            print(
                f"  {subtitle_file}"
            )

            print(
                f"  Entries: {len(entries)}"
            )

            subtitle_files.append(
                subtitle_file
            )

        # -----------------------------------------------------
        # Return FOUR subtitle files
        # -----------------------------------------------------

        return subtitle_files

    # =========================================================
    # CREATE TIMED ENTRIES
    # =========================================================

    def _create_entries(
        self,
        chunks,
        audio_duration,
    ):

        if not chunks:

            return []

        # -----------------------------------------------------
        # Calculate total words
        # -----------------------------------------------------

        word_counts = [
            len(
                chunk.split()
            )
            for chunk in chunks
        ]

        total_words = sum(
            word_counts
        )

        if total_words <= 0:

            total_words = len(
                chunks
            )

            word_counts = [
                1
                for _ in chunks
            ]

        # -----------------------------------------------------
        # Allocate actual audio duration
        # proportionally by words
        # -----------------------------------------------------

        durations = []

        for word_count in word_counts:

            duration = (
                audio_duration
                * word_count
                / total_words
            )

            durations.append(
                duration
            )

        # -----------------------------------------------------
        # Make sure we don't create extremely
        # short subtitle flashes.
        #
        # IMPORTANT:
        # We don't extend the scene beyond the
        # actual audio duration.
        # -----------------------------------------------------

        if len(chunks) == 1:

            durations[0] = audio_duration

        else:

            durations = (
                self._apply_minimum_duration(
                    durations,
                    audio_duration,
                )
            )

        # -----------------------------------------------------
        # Build entries
        # -----------------------------------------------------

        entries = []

        current_time = 0.0

        for index, (
            chunk,
            duration,
        ) in enumerate(
            zip(
                chunks,
                durations,
            ),
            start=1,
        ):

            start = current_time

            end = (
                current_time
                + duration
            )

            entries.append(
                {
                    "index": index,
                    "start": start,
                    "end": end,
                    "text": chunk,
                }
            )

            current_time = end

        # -----------------------------------------------------
        # Force final subtitle to end exactly
        # at the audio boundary.
        # -----------------------------------------------------

        entries[-1][
            "end"
        ] = audio_duration

        return entries

    # =========================================================
    # MINIMUM DURATION
    # =========================================================

    def _apply_minimum_duration(
        self,
        durations,
        total_duration,
    ):

        """
        Attempts to prevent very short subtitle
        flashes while NEVER exceeding the actual
        audio duration.
        """

        count = len(
            durations
        )

        if (
            total_duration
            < self.MIN_SUBTITLE_DURATION
            * count
        ):

            # Not enough time to give every
            # subtitle the minimum duration.
            #
            # In that case, distribute the
            # real duration proportionally.
            return durations

        result = list(
            durations
        )

        deficit = 0.0

        # -----------------------------------------------------
        # First raise short durations
        # -----------------------------------------------------

        for i in range(
            count
        ):

            if (
                result[i]
                < self.MIN_SUBTITLE_DURATION
            ):

                deficit += (
                    self.MIN_SUBTITLE_DURATION
                    - result[i]
                )

                result[i] = (
                    self.MIN_SUBTITLE_DURATION
                )

        # -----------------------------------------------------
        # Remove the added time from longer chunks.
        # -----------------------------------------------------

        if deficit <= 0:

            return result

        long_indices = [

            i

            for i in range(
                count
            )

            if result[i]
            > self.MIN_SUBTITLE_DURATION
        ]

        remaining = deficit

        while (
            remaining > 0.0001
            and long_indices
        ):

            available = sum(

                result[i]
                - self.MIN_SUBTITLE_DURATION

                for i in long_indices

            )

            if available <= 0:

                break

            for i in long_indices:

                available_i = (
                    result[i]
                    - self.MIN_SUBTITLE_DURATION
                )

                if available_i <= 0:

                    continue

                reduction = (
                    remaining
                    * available_i
                    / available
                )

                reduction = min(
                    reduction,
                    available_i,
                )

                result[i] -= (
                    reduction
                )

            remaining = (
                sum(result)
                - total_duration
            )

            if remaining <= 0.0001:

                break

            long_indices = [

                i

                for i in long_indices

                if result[i]
                > self.MIN_SUBTITLE_DURATION
                + 0.0001

            ]

        # -----------------------------------------------------
        # Floating-point correction
        # -----------------------------------------------------

        difference = (
            total_duration
            - sum(result)
        )

        if result:

            result[-1] += difference

        return result

    # =========================================================
    # CREATE SUBTITLE CHUNKS
    # =========================================================

    def _make_chunks(
        self,
        text: str,
    ):

        text = (
            text
            .replace(
                "\r",
                " ",
            )
            .replace(
                "\n",
                " ",
            )
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not text:

            return []

        # -----------------------------------------------------
        # Sentence boundaries
        #
        # English:
        # .
        # !
        # ?
        #
        # Sanskrit:
        # ।
        # ॥
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
        # Break long sentences
        # -----------------------------------------------------

        for sentence in sentences:

            words = sentence.split()

            if (
                len(words)
                <= self.MAX_WORDS_PER_LINE
            ):

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

            str(
                FFPROBE_PATH
            ),

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default="
            "noprint_wrappers=1:"
            "nokey=1",

            str(
                audio_file
            ),
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
    # WRITE SRT
    # =========================================================

    def _write_srt(
        self,
        subtitle_file: Path,
        entries,
    ):

        with open(
            subtitle_file,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:

            for entry in entries:

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

    # =========================================================
    # SRT TIME
    # =========================================================

    def _format_time(
        self,
        seconds: float,
    ) -> str:

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