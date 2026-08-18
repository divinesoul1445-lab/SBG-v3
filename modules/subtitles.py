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
        """
        Build subtitle groups using:

            Edge WordBoundary timings -> timing only
            narration_text             -> authoritative text

        This is important for Sanskrit / Devanagari because the
        WordBoundary text can be mojibake even when the original
        narration text is correct.

        Punctuation such as । and ॥ is kept attached to the
        preceding word and never starts a new subtitle.
        """

        # =========================================================
        # CLEAN SOURCE TEXT
        # =========================================================

        if narration_text is None:

            raise Exception(
                "Narration text is None while creating subtitles."
            )

        narration_text = str(
            narration_text
        ).strip()

        if not narration_text:

            raise Exception(
                "Narration text is empty while creating subtitles."
            )

        # ---------------------------------------------------------
        # Normalise whitespace
        # ---------------------------------------------------------

        narration_text = re.sub(
            r"\s+",
            " ",
            narration_text,
        ).strip()

        # =========================================================
        # SOURCE TOKENS
        # =========================================================
        #
        # Keep punctuation attached to the preceding word.
        #
        # Example:
        #
        # धृतराष्ट्र उवाच ।
        #
        # becomes:
        #
        # ["धृतराष्ट्र", "उवाच", "।"]
        #
        # and later "।" is attached to "उवाच".
        # =========================================================

        source_tokens = (
            narration_text.split()
        )

        if not source_tokens:

            return []

        # =========================================================
        # NORMALISE EDGE WORDS
        # =========================================================

        edge_words = []

        for word in words:

            if not isinstance(
                word,
                dict,
            ):
                continue

            text = word.get(
                "text",
                "",
            )

            if text is None:
                text = ""

            text = str(
                text
            ).strip()

            if not text:
                continue

            try:

                start = float(
                    word.get(
                        "start",
                        0,
                    )
                )

                end = float(
                    word.get(
                        "end",
                        0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if end <= start:
                continue

            edge_words.append(
                {
                    "text": text,
                    "start": start,
                    "end": end,
                }
            )

        if not edge_words:

            raise Exception(
                "No valid Edge TTS word timings available."
            )

        # =========================================================
        # REMOVE PUNCTUATION-ONLY EDGE EVENTS
        # =========================================================
        #
        # Edge can return punctuation as its own timing event.
        #
        # We DO NOT use its text for subtitles.
        #
        # Its timing is nevertheless useful: punctuation belongs
        # to the preceding source word.
        # =========================================================

        punctuation_tokens = {
            "।",
            "॥",
            ".",
            ",",
            "?",
            "!",
            ";",
            ":",
        }

        edge_content_words = []
        edge_punctuation = []

        for item in edge_words:

            cleaned = item["text"].strip()

            if cleaned in punctuation_tokens:

                edge_punctuation.append(
                    item
                )

            else:

                edge_content_words.append(
                    item
                )

        # =========================================================
        # SOURCE WORDS WITHOUT PUNCTUATION
        # =========================================================

        source_word_items = []

        for token in source_tokens:

            # -----------------------------------------------------
            # Separate punctuation from source token only when
            # punctuation is actually attached.
            #
            # Example:
            #
            # युयुत्सवः ।
            #
            # remains two tokens.
            # -----------------------------------------------------

            if token in punctuation_tokens:

                continue

            source_word_items.append(
                token
            )

        # =========================================================
        # SAFETY CHECK
        # =========================================================

        if not source_word_items:

            return []

        # =========================================================
        # MAP SOURCE WORDS -> EDGE TIMINGS
        # =========================================================
        #
        # We deliberately DO NOT require textual equality here.
        #
        # Edge may return mojibake:
        #
        # à¤§à¥ƒ...
        #
        # while source is:
        #
        # धृतराष्ट्र
        #
        # We only need the timing sequence.
        # =========================================================

        timing_count = len(
            edge_content_words
        )

        source_count = len(
            source_word_items
        )

        # ---------------------------------------------------------
        # If counts match, this is the ideal case.
        # ---------------------------------------------------------

        if timing_count == source_count:

            mapped_words = []

            for index, source_word in enumerate(
                source_word_items
            ):

                timing = (
                    edge_content_words[index]
                )

                mapped_words.append(
                    {
                        "text": source_word,
                        "start": timing["start"],
                        "end": timing["end"],
                    }
                )

        else:

            # -----------------------------------------------------
            # Edge sometimes includes/excludes tokens differently.
            #
            # Use proportional mapping as a fallback.
            #
            # IMPORTANT:
            # The actual displayed text STILL comes from the
            # clean source.
            # -----------------------------------------------------

            mapped_words = []

            if source_count == 1:

                mapped_words.append(
                    {
                        "text": source_word_items[0],
                        "start": edge_content_words[0]["start"],
                        "end": edge_content_words[-1]["end"],
                    }
                )

            else:

                for index, source_word in enumerate(
                    source_word_items
                ):

                    source_position = (
                        index
                        / max(
                            source_count - 1,
                            1,
                        )
                    )

                    edge_position = round(
                        source_position
                        * (
                            timing_count - 1
                        )
                    )

                    edge_position = max(
                        0,
                        min(
                            edge_position,
                            timing_count - 1,
                        ),
                    )

                    timing = (
                        edge_content_words[
                            edge_position
                        ]
                    )

                    # -------------------------------------------------
                    # Estimate the end from the next mapped position.
                    # -------------------------------------------------

                    if index < source_count - 1:

                        next_source_position = (
                            (index + 1)
                            / max(
                                source_count - 1,
                                1,
                            )
                        )

                        next_edge_position = round(
                            next_source_position
                            * (
                                timing_count - 1
                            )
                        )

                        next_edge_position = max(
                            edge_position,
                            min(
                                next_edge_position,
                                timing_count - 1,
                            ),
                        )

                        next_timing = (
                            edge_content_words[
                                next_edge_position
                            ]
                        )

                        end = next_timing[
                            "start"
                        ]

                    else:

                        end = timing[
                            "end"
                        ]

                    if end <= timing["start"]:

                        end = timing[
                            "end"
                        ]

                    mapped_words.append(
                        {
                            "text": source_word,
                            "start": timing["start"],
                            "end": end,
                        }
                    )

        # =========================================================
        # ATTACH SOURCE PUNCTUATION
        # =========================================================
        #
        # We now rebuild the source exactly.
        #
        # Example:
        #
        # source:
        #
        # धृतराष्ट्र उवाच । धर्मक्षेत्रे ...
        #
        # mapped words:
        #
        # धृतराष्ट्र
        # उवाच
        # धर्मक्षेत्रे
        #
        # becomes:
        #
        # धृतराष्ट्र
        # उवाच ।
        # धर्मक्षेत्रे
        #
        # The punctuation gets the END time of the preceding word.
        # =========================================================

        source_with_punctuation = []

        word_index = 0

        for token in source_tokens:

            if token in punctuation_tokens:

                if source_with_punctuation:

                    previous = (
                        source_with_punctuation[-1]
                    )

                    previous["text"] = (
                        previous["text"]
                        + " "
                        + token
                    )

                continue

            if word_index >= len(
                mapped_words
            ):

                break

            source_with_punctuation.append(
                {
                    "text":
                        mapped_words[
                            word_index
                        ]["text"],

                    "start":
                        mapped_words[
                            word_index
                        ]["start"],

                    "end":
                        mapped_words[
                            word_index
                        ]["end"],
                }
            )

            word_index += 1

        if not source_with_punctuation:

            return []

        # =========================================================
        # CREATE SUBTITLE GROUPS
        # =========================================================

        groups = []

        current_words = []
        current_start = None
        current_end = None

        for item in source_with_punctuation:

            text = item["text"]
            start = item["start"]
            end = item["end"]

            if current_start is None:

                current_start = start

            current_words.append(
                text
            )

            current_end = end

            # -----------------------------------------------------
            # Sentence-ending punctuation
            # -----------------------------------------------------

            sentence_end = (
                text.endswith("।")
                or text.endswith("॥")
                or text.endswith(".")
                or text.endswith("?")
                or text.endswith("!")
            )

            # -----------------------------------------------------
            # Gap to next word
            # -----------------------------------------------------

            next_index = (
                len(current_words)
            )

            global_index = (
                source_with_punctuation.index(
                    item
                )
            )

            if (
                global_index
                < len(source_with_punctuation) - 1
            ):

                next_item = (
                    source_with_punctuation[
                        global_index + 1
                    ]
                )

                gap = (
                    next_item["start"]
                    - end
                )

            else:

                gap = 0

            # -----------------------------------------------------
            # Maximum words
            # -----------------------------------------------------

            too_many_words = (
                len(current_words)
                >= self.MAX_WORDS_PER_LINE
            )

            # -----------------------------------------------------
            # Close subtitle
            # -----------------------------------------------------

            should_close = (

                sentence_end

                or too_many_words

                or (
                    gap
                    > self.WORD_GAP_THRESHOLD
                    and len(current_words)
                    >= self.MIN_WORDS_PER_CHUNK
                )
            )

            if should_close:

                groups.append(
                    {
                        "words":
                            current_words.copy(),

                        "start":
                            current_start,

                        "end":
                            current_end,
                    }
                )

                current_words = []
                current_start = None
                current_end = None

        # =========================================================
        # REMAINING WORDS
        # =========================================================

        if current_words:

            groups.append(
                {
                    "words":
                        current_words.copy(),

                    "start":
                        current_start,

                    "end":
                        current_end,
                }
            )

        # =========================================================
        # FINAL NORMALISATION
        # =========================================================

        entries = []

        for index, group in enumerate(
            groups,
            start=1,
        ):

            start = float(
                group["start"]
            )

            end = float(
                group["end"]
            )

            # -----------------------------------------------------
            # Clamp to actual audio duration
            # -----------------------------------------------------

            start = max(
                0.0,
                min(
                    start,
                    float(audio_duration),
                ),
            )

            end = max(
                start,
                min(
                    end,
                    float(audio_duration),
                ),
            )

            # -----------------------------------------------------
            # Ensure minimum visible duration
            #
            # Do not move the start.
            # Only extend the end when possible.
            # -----------------------------------------------------

            if (
                end - start
                < self.MIN_SUBTITLE_DURATION
            ):

                end = min(
                    float(audio_duration),
                    start
                    + self.MIN_SUBTITLE_DURATION,
                )

            text = " ".join(
                group["words"]
            ).strip()

            if not text:
                continue

            entries.append(
                {
                    "index":
                        index,

                    "start":
                        round(
                            start,
                            4,
                        ),

                    "end":
                        round(
                            end,
                            4,
                        ),

                    "text":
                        text,
                }
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