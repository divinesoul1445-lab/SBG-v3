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

The subtitle generator controls:
    - subtitle chunking
    - subtitle timing
    - scene boundaries
    - readable caption lengths

Visual styling is handled by videos.py / FFmpeg.
"""

from pathlib import Path
import re
import subprocess

from config import FFPROBE_PATH


class SubtitleGenerator:

    # =========================================================
    # SETTINGS
    # =========================================================

    # Prefer short cinematic captions.
    MAX_WORDS_PER_LINE = 6

    # Avoid extremely short subtitle flashes.
    MIN_SUBTITLE_DURATION = 0.8

    # Prefer at least this many words before forcing
    # a new caption, unless a sentence boundary occurs.
    MIN_WORDS_PER_CHUNK = 3

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
            # Split narration
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
            # Create timed entries
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
        # Calculate word counts
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
        # Allocate duration proportionally by words
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
        # Prevent extremely short flashes
        # -----------------------------------------------------

        if len(chunks) > 1:

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
        # Force exact audio boundary
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
        Prevent very short subtitle flashes without
        ever exceeding the actual scene duration.
        """

        count = len(
            durations
        )

        if (
            total_duration
            < self.MIN_SUBTITLE_DURATION
            * count
        ):

            return durations

        result = list(
            durations
        )

        deficit = 0.0

        # -----------------------------------------------------
        # Raise short entries
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

        if deficit <= 0:

            return result

        # -----------------------------------------------------
        # Take excess from longer entries
        # -----------------------------------------------------

        while deficit > 0.0001:

            long_indices = [

                i

                for i in range(
                    count
                )

                if result[i]
                > self.MIN_SUBTITLE_DURATION
                + 0.0001

            ]

            if not long_indices:

                break

            available = sum(

                result[i]
                - self.MIN_SUBTITLE_DURATION

                for i in long_indices

            )

            if available <= 0:

                break

            removed = 0.0

            for i in long_indices:

                available_i = (
                    result[i]
                    - self.MIN_SUBTITLE_DURATION
                )

                reduction = (
                    deficit
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

                removed += reduction

            deficit -= removed

            if removed <= 0.000001:

                break

        # -----------------------------------------------------
        # Floating point correction
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

        # -----------------------------------------------------
        # Normalize whitespace
        # -----------------------------------------------------

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
        # Split at natural sentence boundaries
        #
        # English:
        # .
        # !
        # ?
        #
        # Devanagari:
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
        # Process each sentence
        # -----------------------------------------------------

        for sentence in sentences:

            words = sentence.split()

            # -------------------------------------------------
            # Short sentence
            # -------------------------------------------------

            if (
                len(words)
                <= self.MAX_WORDS_PER_LINE
            ):

                chunks.append(
                    sentence
                )

                continue

            # -------------------------------------------------
            # Long sentence
            #
            # Break at natural punctuation first,
            # then word count.
            # -------------------------------------------------

            current_words = []

            for word in words:

                current_words.append(
                    word
                )

                # -------------------------------------------------
                # Normal maximum
                # -------------------------------------------------

                if len(
                    current_words
                ) >= self.MAX_WORDS_PER_LINE:

                    chunks.append(
                        " ".join(
                            current_words
                        )
                    )

                    current_words = []

            # -------------------------------------------------
            # Remaining words
            # -------------------------------------------------

            if current_words:

                remaining = (
                    " ".join(
                        current_words
                    )
                )

                # If the previous chunk is very short,
                # merge the remainder into it.
                if (
                    chunks
                    and len(
                        remaining.split()
                    )
                    < self.MIN_WORDS_PER_CHUNK
                ):

                    combined = (
                        chunks[-1]
                        + " "
                        + remaining
                    )

                    if len(
                        combined.split()
                    ) <= (
                        self.MAX_WORDS_PER_LINE
                        + 2
                    ):

                        chunks[-1] = (
                            combined
                        )

                    else:

                        chunks.append(
                            remaining
                        )

                else:

                    chunks.append(
                        remaining
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
                f"Audio has zero duration:\n"
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
    # FORMAT SRT TIME
    # =========================================================

    def _format_time(
        self,
        seconds: float,
    ) -> str:

        milliseconds = int(
            round(
                seconds * 1000
            )
        )

        hours = (
            milliseconds
            // 3_600_000
        )

        milliseconds %= (
            3_600_000
        )

        minutes = (
            milliseconds
            // 60_000
        )

        milliseconds %= (
            60_000
        )

        secs = (
            milliseconds
            // 1000
        )

        milliseconds %= (
            1000
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d},"
            f"{milliseconds:03d}"
        )