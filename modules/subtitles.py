"""
Subtitle Generator (V3)

Creates one subtitle file for each scene.

Architecture:

    Scene narration
        +
    Edge TTS narration.mp3
        +
    narration.json
        |
        v
    WordBoundary timestamps
        |
        v
    scene/subtitles.srt

Subtitle timing is based on the ACTUAL
Edge TTS WordBoundary timestamps.

No proportional duration estimation is used.

Visual styling is handled by videos.py / FFmpeg.
"""

from pathlib import Path
import json
import re
import subprocess

from config import FFPROBE_PATH


class SubtitleGenerator:

    # =========================================================
    # SETTINGS
    # =========================================================

    # Maximum words displayed in one subtitle entry.
    MAX_WORDS_PER_LINE = 6

    # Prefer at least this many words in a chunk.
    MIN_WORDS_PER_CHUNK = 3

    # Very small gaps between words are considered
    # continuous speech.
    WORD_GAP_THRESHOLD = 0.45

    # Small minimum duration for a subtitle entry.
    #
    # IMPORTANT:
    # This is NOT used to move subtitle boundaries.
    # Actual WordBoundary timing remains authoritative.
    MIN_SUBTITLE_DURATION = 0.25

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
        # Validate scene texts
        # -----------------------------------------------------

        if not scene_texts:

            raise Exception(
                "No scene narration text supplied."
            )

        # -----------------------------------------------------
        # Validate audio files
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

            print()
            print(
                "-" * 70
            )

            print(
                f"SUBTITLE SCENE {scene_number}"
            )

            print(
                "-" * 70
            )

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
            # Timing JSON
            # -------------------------------------------------

            timing_file = (
                scene_folder
                / "narration.json"
            )

            # -------------------------------------------------
            # Validate narration
            # -------------------------------------------------

            text = (
                ""
                if text is None
                else str(text).strip()
            )

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
            # Validate timing JSON
            # -------------------------------------------------

            if not timing_file.exists():

                raise FileNotFoundError(
                    f"Scene {scene_number} "
                    f"WordBoundary timing file not found:\n"
                    f"{timing_file}\n\n"
                    f"Run test_tts.py first."
                )

            if timing_file.stat().st_size <= 0:

                raise Exception(
                    f"Scene {scene_number} "
                    f"timing file is empty:\n"
                    f"{timing_file}"
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
                f"Audio duration: "
                f"{audio_duration:.3f}s"
            )

            print(
                f"Timing file:"
            )

            print(
                f"  {timing_file}"
            )

            # -------------------------------------------------
            # Load WordBoundary timestamps
            # -------------------------------------------------

            words = (
                self._load_word_boundaries(
                    timing_file
                )
            )

            if not words:

                raise Exception(
                    f"Scene {scene_number} "
                    f"contains no WordBoundary data."
                )

            print(
                f"Word boundaries: "
                f"{len(words)}"
            )

            # -------------------------------------------------
            # Build subtitle entries
            # -------------------------------------------------

            entries = (
                self._create_word_timed_entries(
                    words=words,
                    audio_duration=audio_duration,
                    narration_text=text,
                )
            )

            if not entries:

                raise Exception(
                    f"Scene {scene_number} "
                    f"produced no subtitle entries."
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
                f"  Entries: "
                f"{len(entries)}"
            )

            subtitle_files.append(
                subtitle_file
            )

        # -----------------------------------------------------
        # Return subtitle files
        # -----------------------------------------------------

        return subtitle_files

    # =========================================================
    # LOAD WORD BOUNDARIES
    # =========================================================

    def _load_word_boundaries(
        self,
        timing_file: Path,
    ):

        timing_file = Path(
            timing_file
        )

        try:

            with open(
                timing_file,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(
                    f
                )

        except json.JSONDecodeError as e:

            raise Exception(
                f"Invalid narration timing JSON:\n"
                f"{timing_file}\n"
                f"{e}"
            )

        words = data.get(
            "words"
        )

        if not isinstance(
            words,
            list,
        ):

            raise Exception(
                f"Invalid WordBoundary structure:\n"
                f"{timing_file}\n\n"
                f"Expected a 'words' list."
            )

        result = []

        for item in words:

            if not isinstance(
                item,
                dict,
            ):

                continue

            word = item.get(
                "text"
            )

            start = item.get(
                "start"
            )

            end = item.get(
                "end"
            )

            # -------------------------------------------------
            # Validate timing
            # -------------------------------------------------

            if word is None:

                continue

            try:

                start = float(
                    start
                )

                end = float(
                    end
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            word = str(
                word
            ).strip()

            if not word:

                continue

            if end <= start:

                continue

            result.append(
                {
                    "text": word,
                    "start": max(
                        0.0,
                        start,
                    ),
                    "end": max(
                        0.0,
                        end,
                    ),
                }
            )

        # -----------------------------------------------------
        # Sort by actual speech position
        # -----------------------------------------------------

        result.sort(
            key=lambda item:
                item["start"]
        )

        return result

    # =========================================================
    # CREATE WORD-TIMED ENTRIES
    # =========================================================

    def _create_word_timed_entries(
        self,
        words,
        audio_duration,
        narration_text,
    ):

        if not words:

            return []

        # -----------------------------------------------------
        # Clean / normalize boundaries
        # -----------------------------------------------------

        cleaned = []

        for item in words:

            start = float(
                item["start"]
            )

            end = float(
                item["end"]
            )

            if start >= audio_duration:

                continue

            end = min(
                end,
                audio_duration,
            )

            if end <= start:

                continue

            cleaned.append(
                {
                    "text":
                        item["text"],

                    "start":
                        start,

                    "end":
                        end,
                }
            )

        if not cleaned:

            return []

        # -----------------------------------------------------
        # Group actual spoken words
        # -----------------------------------------------------

        groups = []

        current = []

        for word in cleaned:

            if not current:

                current.append(
                    word
                )

                continue

            previous = (
                current[-1]
            )

            gap = (
                word["start"]
                - previous["end"]
            )

            current_text = " ".join(
                item["text"]
                for item in current
            )

            # -------------------------------------------------
            # Natural punctuation
            # -------------------------------------------------

            punctuation_boundary = (
                self._ends_sentence(
                    previous["text"]
                )
            )

            # -------------------------------------------------
            # Maximum words
            # -------------------------------------------------

            max_words_reached = (
                len(current)
                >= self.MAX_WORDS_PER_LINE
            )

            # -------------------------------------------------
            # Large pause
            # -------------------------------------------------

            large_gap = (
                gap
                >= self.WORD_GAP_THRESHOLD
            )

            # -------------------------------------------------
            # Decide whether to start a new subtitle
            # -------------------------------------------------

            should_split = False

            if max_words_reached:

                should_split = True

            elif (
                punctuation_boundary
                and len(current)
                >= self.MIN_WORDS_PER_CHUNK
            ):

                should_split = True

            elif (
                large_gap
                and len(current)
                >= self.MIN_WORDS_PER_CHUNK
            ):

                should_split = True

            if should_split:

                groups.append(
                    current
                )

                current = [
                    word
                ]

            else:

                current.append(
                    word
                )

        # -----------------------------------------------------
        # Final group
        # -----------------------------------------------------

        if current:

            groups.append(
                current
            )

        # -----------------------------------------------------
        # Merge tiny final group
        #
        # Example:
        #
        # 1 2 3 4 5 6
        # 7
        #
        # becomes:
        #
        # 1 2 3 4 5 6 7
        # -----------------------------------------------------

        groups = (
            self._merge_small_groups(
                groups
            )
        )

        # -----------------------------------------------------
        # Build final entries
        # -----------------------------------------------------

        entries = []

        for index, group in enumerate(
            groups,
            start=1,
        ):

            if not group:

                continue

            start = float(
                group[0]["start"]
            )

            end = float(
                group[-1]["end"]
            )

            text = " ".join(
                item["text"]
                for item in group
            ).strip()

            if not text:

                continue

            # -------------------------------------------------
            # Never allow invalid timestamps
            # -------------------------------------------------

            start = max(
                0.0,
                min(
                    start,
                    audio_duration,
                ),
            )

            end = max(
                start,
                min(
                    end,
                    audio_duration,
                ),
            )

            # -------------------------------------------------
            # If actual word timing is extremely short,
            # don't invent a long duration.
            #
            # Instead retain the actual speech timing.
            # -------------------------------------------------

            entries.append(
                {
                    "index":
                        index,

                    "start":
                        start,

                    "end":
                        end,

                    "text":
                        text,
                }
            )

        # -----------------------------------------------------
        # Final boundary
        #
        # Don't leave the last subtitle ending before
        # the end of the actual spoken audio if the
        # last WordBoundary ends slightly early.
        #
        # A small tail is acceptable and makes the
        # final subtitle remain visible through the
        # end of the spoken sentence.
        # -----------------------------------------------------

        if entries:

            last_end = (
                entries[-1]["end"]
            )

            remaining = (
                audio_duration
                - last_end
            )

            if remaining > 0:
                entries[-1]["end"] = (
                    audio_duration
                )

        return entries

    # =========================================================
    # MERGE SMALL GROUPS
    # =========================================================

    def _merge_small_groups(
        self,
        groups,
    ):

        if len(groups) <= 1:

            return groups

        result = []

        for group in groups:

            if not result:

                result.append(
                    group
                )

                continue

            word_count = len(
                group
            )

            # -------------------------------------------------
            # Small group
            # -------------------------------------------------

            if (
                word_count
                < self.MIN_WORDS_PER_CHUNK
            ):

                previous = result[-1]

                combined_count = (
                    len(previous)
                    + word_count
                )

                # -------------------------------------------------
                # Merge if still reasonably readable.
                # -------------------------------------------------

                if combined_count <= (
                    self.MAX_WORDS_PER_LINE
                    + 2
                ):

                    result[-1] = (
                        previous
                        + group
                    )

                    continue

            result.append(
                group
            )

        return result

    # =========================================================
    # SENTENCE END
    # =========================================================

    def _ends_sentence(
        self,
        word: str,
    ) -> bool:

        if not word:

            return False

        word = str(
            word
        ).strip()

        return bool(
            re.search(
                r"[.!?।॥]$",
                word,
            )
        )

    # =========================================================
    # AUDIO DURATION
    # =========================================================

    def _audio_duration(
        self,
        audio_file: Path,
    ) -> float:

        audio_file = Path(
            audio_file
        )

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

        subtitle_file = Path(
            subtitle_file
        )

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

        seconds = max(
            0.0,
            float(seconds),
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