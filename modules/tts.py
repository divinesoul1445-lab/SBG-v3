"""
Text To Speech (V3)

Uses Microsoft Edge TTS.

Scene voices:

    Scene 1 -> English
    Scene 2 -> Hindi/Sanskrit
    Scene 3 -> English
    Scene 4 -> English

Generates:

    scene1/narration.mp3
    scene1/narration.json

    scene2/narration.mp3
    scene2/narration.json

    scene3/narration.mp3
    scene3/narration.json

    scene4/narration.mp3
    scene4/narration.json


IMPORTANT Unicode rule
----------------------

The narration source is authoritative.

For Devanagari:

    source narration
        ↓
    Edge TTS audio
        +
    Edge TTS WordBoundary timing
        ↓
    narration.json

The WordBoundary "text" returned by Edge TTS is NEVER
used for subtitle text.

This is important because Edge TTS can return mojibaked
Unicode for Devanagari WordBoundary text, for example:

    à¤§à¥ƒà¤¤à¤°

The original source text remains clean:

    धृतराष्ट्र

Therefore:

    Edge TTS boundary = TIMING ONLY
    source narration  = SUBTITLE TEXT
"""

import asyncio
import json
from pathlib import Path

import edge_tts


# ============================================================
# VOICES
# ============================================================

ENGLISH_VOICE = "en-IN-PrabhatNeural"

SANSKRIT_VOICE = "hi-IN-SwaraNeural"


# ============================================================
# AUDIO SETTINGS
# ============================================================

RATE = "-10%"

VOLUME = "+0%"


# ============================================================
# CLASS
# ============================================================

class TTSGenerator:

    def __init__(self):
        pass

    # ========================================================
    # SELECT VOICE
    # ========================================================

    def _get_voice(
        self,
        scene_number: int,
    ) -> str:

        if scene_number == 2:
            return SANSKRIT_VOICE

        return ENGLISH_VOICE

    # ========================================================
    # SOURCE WORDS
    # ========================================================

    def _get_source_words(
        self,
        text: str,
    ) -> list[str]:
        """
        Return the authoritative source words.

        NEVER use Edge TTS WordBoundary["text"].

        The source text is the text that should appear
        in subtitles.
        """

        if text is None:
            return []

        text = str(text).strip()

        if not text:
            return []

        return text.split()

    # ========================================================
    # SOURCE TEXT DEBUG
    # ========================================================

    def _print_text_debug(
        self,
        scene_number: int,
        text: str,
    ):

        print()
        print("=" * 80)
        print(
            f"TTS INPUT DEBUG — SCENE {scene_number}"
        )
        print("=" * 80)

        print()

        print("TEXT:")
        print(text)

        print()

        print("REPR:")
        print(repr(text))

        print()

        print("CODEPOINTS:")

        print(
            [
                hex(ord(char))
                for char in text
            ]
        )

        print()

        print("SOURCE WORDS:")

        print(
            self._get_source_words(text)
        )

        print()

        print("=" * 80)
        print()

    # ========================================================
    # GENERATE AUDIO + WORD TIMINGS
    # ========================================================

    async def _generate_audio_and_timings(
        self,
        text: str,
        output_file: Path,
        voice: str,
        timing_file: Path,
    ):
        """
        Generate audio and timing information.

        CRITICAL:

        Edge TTS WordBoundary events provide timing only.

        Their "text" field is ignored completely.

        Subtitle text is taken from the original clean
        source narration.
        """

        output_file = Path(
            output_file
        )

        timing_file = Path(
            timing_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        timing_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ----------------------------------------------------
        # CLEAN SOURCE TEXT
        # ----------------------------------------------------

        if text is None:

            raise ValueError(
                "TTS received None text."
            )

        text = str(
            text
        ).strip()

        if not text:

            raise ValueError(
                "TTS received empty text."
            )

        # ----------------------------------------------------
        # AUTHORITATIVE SOURCE WORDS
        # ----------------------------------------------------

        source_words = (
            self._get_source_words(
                text
            )
        )

        if not source_words:

            raise ValueError(
                "TTS source contains no words."
            )

        # ----------------------------------------------------
        # DEBUG
        # ----------------------------------------------------

        print()

        print(
            "=" * 80
        )

        print(
            "EDGE TTS INPUT"
        )

        print(
            "=" * 80
        )

        print(
            "Voice :",
            voice,
        )

        print(
            "Rate  :",
            RATE,
        )

        print(
            "Volume:",
            VOLUME,
        )

        print(
            "Text  :",
            text,
        )

        print(
            "Audio :",
            output_file,
        )

        print(
            "Timing:",
            timing_file,
        )

        print(
            "Words :",
            len(source_words),
        )

        print(
            "=" * 80
        )

        print()

        # ----------------------------------------------------
        # EDGE TTS
        # ----------------------------------------------------

        communicate = (
            edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=RATE,
                volume=VOLUME,
                boundary="WordBoundary",
            )
        )

        # ----------------------------------------------------
        # RAW TIMINGS
        #
        # We intentionally do NOT store boundary text.
        # ----------------------------------------------------

        raw_boundaries = []

        # ----------------------------------------------------
        # STREAM AUDIO
        # ----------------------------------------------------

        with open(
            output_file,
            "wb",
        ) as audio:

            async for chunk in (
                communicate.stream()
            ):

                chunk_type = (
                    chunk.get(
                        "type"
                    )
                )

                # ------------------------------------------------
                # AUDIO
                # ------------------------------------------------

                if chunk_type == "audio":

                    data = (
                        chunk.get(
                            "data"
                        )
                    )

                    if data:

                        audio.write(
                            data
                        )

                # ------------------------------------------------
                # WORD BOUNDARY
                # ------------------------------------------------

                elif (
                    chunk_type
                    == "WordBoundary"
                ):

                    offset = (
                        chunk.get(
                            "offset"
                        )
                    )

                    duration = (
                        chunk.get(
                            "duration"
                        )
                    )

                    # ------------------------------------------------
                    # IMPORTANT
                    #
                    # Do NOT read:
                    #
                    #     chunk["text"]
                    #
                    # It may contain mojibake.
                    # ------------------------------------------------

                    if (
                        offset is None
                        or duration is None
                    ):

                        continue

                    # Edge TTS uses
                    # 100-nanosecond units.

                    start = (
                        float(offset)
                        / 10_000_000
                    )

                    word_duration = (
                        float(duration)
                        / 10_000_000
                    )

                    end = (
                        start
                        + word_duration
                    )

                    raw_boundaries.append(
                        {
                            "start":
                                start,

                            "end":
                                end,

                            "duration":
                                word_duration,
                        }
                    )

        # ====================================================
        # VALIDATE EDGE TIMINGS
        # ====================================================

        if not raw_boundaries:

            raise Exception(
                "Edge TTS generated audio but "
                "returned no WordBoundary events."
            )

        # ====================================================
        # MAP CLEAN SOURCE WORDS
        # ====================================================

        source_count = len(
            source_words
        )

        boundary_count = len(
            raw_boundaries
        )

        print()

        print(
            "=" * 80
        )

        print(
            "WORD TIMING MAPPING"
        )

        print(
            "=" * 80
        )

        print(
            "Clean source words :",
            source_count,
        )

        print(
            "Edge boundaries    :",
            boundary_count,
        )

        print()

        word_boundaries = []

        # ====================================================
        # CASE 1
        #
        # Perfect 1:1 match
        # ====================================================

        if (
            boundary_count
            == source_count
        ):

            for word, boundary in zip(
                source_words,
                raw_boundaries,
            ):

                word_boundaries.append(
                    {
                        "text":
                            word,

                        "start":
                            round(
                                boundary[
                                    "start"
                                ],
                                4,
                            ),

                        "end":
                            round(
                                boundary[
                                    "end"
                                ],
                                4,
                            ),

                        "duration":
                            round(
                                boundary[
                                    "duration"
                                ],
                                4,
                            ),
                    }
                )

        # ====================================================
        # CASE 2
        #
        # Different token counts
        #
        # Example:
        #
        # Source:
        #
        #   धृतराष्ट्र उवाच ।
        #
        # Edge:
        #
        #   may return different tokenisation
        #
        # We preserve ALL source words.
        # ====================================================

        else:

            for index, boundary in enumerate(
                raw_boundaries
            ):

                source_start = int(
                    index
                    * source_count
                    / boundary_count
                )

                source_end = int(
                    (index + 1)
                    * source_count
                    / boundary_count
                )

                if (
                    source_end
                    <= source_start
                ):

                    source_end = (
                        source_start
                        + 1
                    )

                source_end = min(
                    source_end,
                    source_count,
                )

                mapped_words = (
                    source_words[
                        source_start:
                        source_end
                    ]
                )

                if not mapped_words:

                    continue

                # ------------------------------------------------
                # IMPORTANT:
                #
                # The text here comes ONLY from the clean
                # source narration.
                # ------------------------------------------------

                subtitle_text = (
                    " ".join(
                        mapped_words
                    )
                )

                word_boundaries.append(
                    {
                        "text":
                            subtitle_text,

                        "start":
                            round(
                                boundary[
                                    "start"
                                ],
                                4,
                            ),

                        "end":
                            round(
                                boundary[
                                    "end"
                                ],
                                4,
                            ),

                        "duration":
                            round(
                                boundary[
                                    "duration"
                                ],
                                4,
                            ),
                    }
                )

        # ====================================================
        # DEBUG FINAL MAPPING
        # ====================================================

        print(
            "FINAL SUBTITLE WORDS:"
        )

        print()

        for index, item in enumerate(
            word_boundaries,
            start=1,
        ):

            print(
                f"{index:02d}  "
                f"{item['start']:7.3f}"
                f" -> "
                f"{item['end']:7.3f}   "
                f"{item['text']}"
            )

        print()

        print(
            "=" * 80
        )

        print()

        # ====================================================
        # SAVE JSON
        # ====================================================

        timing_data = {

            # ALWAYS clean source text.

            "text":
                text,

            "voice":
                voice,

            "rate":
                RATE,

            "volume":
                VOLUME,

            "words":
                word_boundaries,
        }

        with open(
            timing_file,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:

            json.dump(
                timing_data,
                f,
                ensure_ascii=False,
                indent=2,
            )

        # ====================================================
        # FINAL VALIDATION
        # ====================================================

        if not output_file.exists():

            raise Exception(
                "Edge TTS completed but "
                "audio file was not created."
            )

        if (
            output_file.stat().st_size
            <= 0
        ):

            raise Exception(
                "Generated narration audio "
                "is empty."
            )

        if not timing_file.exists():

            raise Exception(
                "Word timing JSON was not created."
            )

        if (
            timing_file.stat().st_size
            <= 0
        ):

            raise Exception(
                "Word timing JSON is empty."
            )

        print(
            f"✓ Audio created -> "
            f"{output_file}"
        )

        print(
            f"✓ Word timings saved -> "
            f"{timing_file}"
        )

        print(
            f"✓ Clean source subtitle "
            f"text preserved -> "
            f"{len(word_boundaries)} entries"
        )

        return word_boundaries

    # ========================================================
    # GENERATE ONE SCENE
    # ========================================================

    def generate_scene(
        self,
        scene_number: int,
        text: str,
        output_folder: Path,
    ) -> Path:

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        if scene_number not in (
            1,
            2,
            3,
            4,
        ):

            raise ValueError(
                "scene_number must be between 1 and 4."
            )

        if text is None:

            raise Exception(
                f"Scene {scene_number} "
                f"narration is None."
            )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # Do NOT call _repair_mojibake().
        #
        # The pipeline already supplies clean source text.
        #
        # If the source is:
        #
        #     धृतराष्ट्र
        #
        # it must remain:
        #
        #     धृतराष्ट्र
        # ----------------------------------------------------

        text = str(
            text
        ).strip()

        if not text:

            raise Exception(
                f"Scene {scene_number} "
                f"narration is empty."
            )

        # ----------------------------------------------------
        # DEBUG SOURCE
        # ----------------------------------------------------

        self._print_text_debug(
            scene_number,
            text,
        )

        # ----------------------------------------------------
        # Output files
        # ----------------------------------------------------

        audio_file = (
            output_folder
            / "narration.mp3"
        )

        timing_file = (
            output_folder
            / "narration.json"
        )

        # ----------------------------------------------------
        # Voice
        # ----------------------------------------------------

        voice = (
            self._get_voice(
                scene_number
            )
        )

        # ----------------------------------------------------
        # FORCE REGENERATE SCENE 2
        #
        # Old Scene 2 JSON contains mojibake.
        #
        # Regenerate it once using the new implementation.
        # ----------------------------------------------------

        force_regenerate = (
            scene_number == 2
        )

        # ----------------------------------------------------
        # Reuse valid output for scenes 1,3,4
        # ----------------------------------------------------

        if (
            not force_regenerate
            and audio_file.exists()
            and audio_file.stat().st_size > 0
            and timing_file.exists()
            and timing_file.stat().st_size > 0
        ):

            print(
                f"✓ Scene {scene_number} "
                f"audio + timing already exist:"
            )

            print(
                f"  {audio_file}"
            )

            print(
                f"  {timing_file}"
            )

            return audio_file

        # ----------------------------------------------------
        # Remove old files
        # ----------------------------------------------------

        if audio_file.exists():

            print(
                f"Removing existing Scene "
                f"{scene_number} audio:"
            )

            print(
                f"  {audio_file}"
            )

            audio_file.unlink(
                missing_ok=True
            )

        if timing_file.exists():

            print(
                f"Removing existing Scene "
                f"{scene_number} timing:"
            )

            print(
                f"  {timing_file}"
            )

            timing_file.unlink(
                missing_ok=True
            )

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        print()

        print(
            f"Generating Scene "
            f"{scene_number} "
            f"audio + timing..."
        )

        asyncio.run(
            self._generate_audio_and_timings(
                text=text,
                output_file=audio_file,
                voice=voice,
                timing_file=timing_file,
            )
        )

        # ----------------------------------------------------
        # Validate audio
        # ----------------------------------------------------

        if not audio_file.exists():

            raise Exception(
                f"Scene {scene_number} "
                f"audio was not created."
            )

        if (
            audio_file.stat().st_size
            <= 0
        ):

            audio_file.unlink(
                missing_ok=True
            )

            raise Exception(
                f"Scene {scene_number} "
                f"audio was created but is empty."
            )

        # ----------------------------------------------------
        # Validate timing
        # ----------------------------------------------------

        if not timing_file.exists():

            raise Exception(
                f"Scene {scene_number} "
                f"timing file was not created."
            )

        if (
            timing_file.stat().st_size
            <= 0
        ):

            timing_file.unlink(
                missing_ok=True
            )

            raise Exception(
                f"Scene {scene_number} "
                f"timing file was created but is empty."
            )

        print()

        print(
            f"✓ Scene {scene_number} "
            f"audio created:"
        )

        print(
            f"  {audio_file}"
        )

        print(
            f"✓ Scene {scene_number} "
            f"timing created:"
        )

        print(
            f"  {timing_file}"
        )

        return audio_file

    # ========================================================
    # GENERATE ALL FOUR SCENES
    # ========================================================

    def generate_scenes(
        self,
        scenes,
        output_folder: Path,
    ) -> list[Path]:

        if scenes is None:

            raise Exception(
                "Scene narration list is None."
            )

        if len(scenes) != 4:

            raise Exception(
                f"Expected exactly 4 scenes, "
                f"received {len(scenes)}."
            )

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio_files = []

        for index, text in enumerate(
            scenes,
            start=1,
        ):

            scene_folder = (
                output_folder
                / f"scene{index}"
            )

            audio_file = (
                self.generate_scene(
                    scene_number=index,
                    text=text,
                    output_folder=scene_folder,
                )
            )

            audio_files.append(
                audio_file
            )

        # ----------------------------------------------------
        # Final validation
        # ----------------------------------------------------

        if len(audio_files) != 4:

            raise Exception(
                "TTS did not produce four "
                "scene audio files."
            )

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):

            audio_file = Path(
                audio_file
            )

            timing_file = (
                audio_file.parent
                / "narration.json"
            )

            if not audio_file.exists():

                raise Exception(
                    f"Scene {index} "
                    f"audio missing:\n"
                    f"{audio_file}"
                )

            if (
                audio_file.stat().st_size
                == 0
            ):

                raise Exception(
                    f"Scene {index} "
                    f"audio is empty:\n"
                    f"{audio_file}"
                )

            if not timing_file.exists():

                raise Exception(
                    f"Scene {index} "
                    f"timing missing:\n"
                    f"{timing_file}"
                )

            if (
                timing_file.stat().st_size
                == 0
            ):

                raise Exception(
                    f"Scene {index} "
                    f"timing is empty:\n"
                    f"{timing_file}"
                )

        return audio_files

    # ========================================================
    # LEGACY SINGLE AUDIO GENERATOR
    # ========================================================

    def generate(
        self,
        text: str,
        output_folder: Path,
    ) -> Path:
        """
        Legacy compatibility method.

        Generates:

            teaching.mp3

        This method does not create word timings.
        """

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio_file = (
            output_folder
            / "teaching.mp3"
        )

        if (
            audio_file.exists()
            and audio_file.stat().st_size > 0
        ):

            return audio_file

        if audio_file.exists():

            audio_file.unlink(
                missing_ok=True
            )

        if text is None:

            raise Exception(
                "Input text is None."
            )

        text = str(
            text
        ).strip()

        if not text:

            raise Exception(
                "Input text is empty."
            )

        asyncio.run(
            self._generate_legacy(
                text=text,
                output_file=audio_file,
            )
        )

        if not audio_file.exists():

            raise Exception(
                "Narration audio was not created."
            )

        if (
            audio_file.stat().st_size
            == 0
        ):

            audio_file.unlink(
                missing_ok=True
            )

            raise Exception(
                "Narration audio was created "
                "but is empty."
            )

        return audio_file

    # ========================================================
    # LEGACY GENERATION
    # ========================================================

    async def _generate_legacy(
        self,
        text: str,
        output_file: Path,
    ):
        """
        Legacy audio-only generation.
        """

        text = str(
            text
        ).strip()

        communicate = (
            edge_tts.Communicate(
                text=text,
                voice=ENGLISH_VOICE,
                rate=RATE,
                volume=VOLUME,
            )
        )

        await communicate.save(
            str(output_file)
        )