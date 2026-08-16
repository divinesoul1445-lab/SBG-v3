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

The JSON file contains Edge TTS word-boundary
timestamps and the ORIGINAL narration words.

IMPORTANT:

Edge TTS may return corrupted Unicode in
WordBoundary["text"] for Devanagari.

Therefore:

    Edge TTS boundary text = timing only
    Original narration text = subtitle text
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

RATE = "+0%"
VOLUME = "+0%"


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
    # MOJIBAKE DETECTION
    # ========================================================

    def _looks_like_mojibake(
        self,
        text: str,
    ) -> bool:
        """
        Detect common UTF-8 mojibake.

        Examples:

            à¤§à¥ƒ...
            Ã©
            Â
            â€™
            ï»¿
        """

        if not text:
            return False

        markers = (
            "à¤",
            "à¥",
            "Ã",
            "Â",
            "â",
            "ï»¿",
        )

        return any(
            marker in text
            for marker in markers
        )

    # ========================================================
    # REPAIR MOJIBAKE
    # ========================================================

    def _repair_mojibake(
        self,
        text,
    ):
        """
        Repair UTF-8 mojibake.

        IMPORTANT:

        Genuine Devanagari is returned unchanged.

        Example:

            धृतराष्ट्र

        remains:

            धृतराष्ट्र

        while:

            à¤§à¥ƒà¤¤à¤°

        becomes:

            धृतराष्ट्र
        """

        if text is None:
            return text

        text = str(text)

        if not text:
            return text

        # ----------------------------------------------------
        # NEVER TOUCH VALID DEVANAGARI
        # ----------------------------------------------------

        if any(
            "\u0900" <= char <= "\u097F"
            for char in text
        ):
            return text

        # ----------------------------------------------------
        # Nothing obviously corrupted
        # ----------------------------------------------------

        if not self._looks_like_mojibake(text):
            return text

        # ----------------------------------------------------
        # Try CP1252 -> UTF-8
        # ----------------------------------------------------

        candidates = []

        try:

            candidates.append(
                text
                .encode("cp1252")
                .decode("utf-8")
            )

        except (
            UnicodeEncodeError,
            UnicodeDecodeError,
        ):
            pass

        # ----------------------------------------------------
        # Try Latin-1 -> UTF-8
        # ----------------------------------------------------

        try:

            candidates.append(
                text
                .encode("latin1")
                .decode("utf-8")
            )

        except (
            UnicodeEncodeError,
            UnicodeDecodeError,
        ):
            pass

        # ----------------------------------------------------
        # Select candidate containing Devanagari
        # ----------------------------------------------------

        for candidate in candidates:

            if any(
                "\u0900" <= char <= "\u097F"
                for char in candidate
            ):

                return candidate

        # ----------------------------------------------------
        # Nothing worked
        # ----------------------------------------------------

        return text

    # ========================================================
    # SOURCE WORDS
    # ========================================================

    def _get_source_words(
        self,
        text: str,
    ):
        """
        Return authoritative narration words.

        These words are taken directly from the original
        narration and NOT from Edge TTS.

        This is critical for Sanskrit / Devanagari.
        """

        if not text:
            return []

        return str(text).split()

    # ========================================================
    # PRINT TEXT DEBUG
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

        print("=" * 80)
        print()

    # ========================================================
    # GENERATE AUDIO + WORD TIMINGS
    # ========================================================

    async def _generate(
        self,
        text: str,
        output_file: Path,
        voice: str,
        timing_file: Path,
    ):

        if text is None:

            raise Exception(
                "TTS received None text."
            )

        text = str(
            text
        ).strip()

        if not text:

            raise Exception(
                "TTS received empty text."
            )

        # ----------------------------------------------------
        # Repair only if necessary
        # ----------------------------------------------------

        original_text = text

        repaired_text = (
            self._repair_mojibake(
                text
            )
        )

        if repaired_text != original_text:

            print()
            print(
                "⚠ Mojibake detected."
            )

            print(
                "Before:",
                repr(original_text),
            )

            print(
                "After :",
                repr(repaired_text),
            )

            print()

            text = repaired_text

        # ----------------------------------------------------
        # Debug
        # ----------------------------------------------------

        print()
        print("=" * 80)
        print("EDGE TTS DEBUG")
        print("=" * 80)

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
            repr(text),
        )

        print(
            "Audio :",
            output_file,
        )

        print(
            "Timing:",
            timing_file,
        )

        print("=" * 80)
        print()

        # ----------------------------------------------------
        # Edge TTS
        # ----------------------------------------------------

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=RATE,
            volume=VOLUME,
            boundary="WordBoundary",
        )

        # ----------------------------------------------------
        # AUTHORITATIVE SOURCE WORDS
        # ----------------------------------------------------

        source_words = (
            self._get_source_words(
                text
            )
        )

        source_word_index = 0

        word_boundaries = []

        # ----------------------------------------------------
        # Write MP3 + capture boundaries
        # ----------------------------------------------------

        with open(
            output_file,
            "wb",
        ) as audio:

            async for chunk in communicate.stream():

                chunk_type = (
                    chunk.get("type")
                )

                # ============================================
                # AUDIO
                # ============================================

                if chunk_type == "audio":

                    data = (
                        chunk.get("data")
                    )

                    if data:

                        audio.write(
                            data
                        )

                # ============================================
                # WORD BOUNDARY
                # ============================================

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
                    # DO NOT use:
                    #
                    #     chunk["text"]
                    #
                    # for subtitle text.
                    #
                    # Edge TTS can return mojibake here.
                    #
                    # We use it ONLY as a timing event.
                    # ------------------------------------------------

                    if (
                        offset is None
                        or duration is None
                    ):

                        continue

                    # ------------------------------------------------
                    # Match timing event to original narration word
                    # ------------------------------------------------

                    if (
                        source_word_index
                        < len(source_words)
                    ):

                        subtitle_word = (
                            source_words[
                                source_word_index
                            ]
                        )

                        source_word_index += 1

                    else:

                        subtitle_word = ""

                    # ------------------------------------------------
                    # Edge TTS timestamps:
                    #
                    # 100 nanoseconds
                    # ------------------------------------------------

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

                    word_boundaries.append(
                        {
                            "text":
                                subtitle_word,

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

                            "duration":
                                round(
                                    word_duration,
                                    4,
                                ),
                        }
                    )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not word_boundaries:

            raise Exception(
                "Edge TTS generated audio but "
                "returned no WordBoundary events."
            )

        # ----------------------------------------------------
        # IMPORTANT VALIDATION
        #
        # If Edge returned fewer timing events than source
        # words, do NOT silently pretend everything matched.
        # ----------------------------------------------------

        if (
            len(word_boundaries)
            != len(source_words)
        ):

            print()
            print(
                "⚠ WORD COUNT MISMATCH"
            )

            print(
                "Source words :",
                len(source_words),
            )

            print(
                "TTS timings  :",
                len(word_boundaries),
            )

            print()

        # ----------------------------------------------------
        # Save narration JSON
        # ----------------------------------------------------

        timing_data = {

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

        print(
            f"✓ Word boundaries captured: "
            f"{len(word_boundaries)}"
        )

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
                f"Scene {scene_number} narration is None."
            )

        text = str(
            text
        ).strip()

        if not text:

            raise Exception(
                f"Scene {scene_number} narration is empty."
            )

        # ----------------------------------------------------
        # Repair before anything else
        # ----------------------------------------------------

        text = self._repair_mojibake(
            text
        )

        # ----------------------------------------------------
        # Debug original source
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

        voice = self._get_voice(
            scene_number
        )

        # ----------------------------------------------------
        # ALWAYS regenerate Scene 2
        #
        # Existing Scene 2 narration.json may contain
        # corrupted Edge boundary text.
        #
        # Therefore Scene 2 must not reuse old timing data.
        # ----------------------------------------------------

        force_regenerate = (
            scene_number == 2
        )

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

        print(
            f"Generating Scene "
            f"{scene_number} audio + timing..."
        )

        asyncio.run(
            self._generate(
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
                f"Scene {scene_number} audio "
                f"was not created."
            )

        if audio_file.stat().st_size == 0:

            audio_file.unlink(
                missing_ok=True
            )

            raise Exception(
                f"Scene {scene_number} audio "
                f"was created but is 0 KB."
            )

        # ----------------------------------------------------
        # Validate timing
        # ----------------------------------------------------

        if not timing_file.exists():

            raise Exception(
                f"Scene {scene_number} timing "
                f"file was not created."
            )

        if timing_file.stat().st_size == 0:

            timing_file.unlink(
                missing_ok=True
            )

            raise Exception(
                f"Scene {scene_number} timing "
                f"file was created but is empty."
            )

        print(
            f"✓ Scene {scene_number} audio created:"
        )

        print(
            f"  {audio_file}"
        )

        print(
            f"✓ Scene {scene_number} timing created:"
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
                    f"Scene {index} audio missing:\n"
                    f"{audio_file}"
                )

            if audio_file.stat().st_size == 0:

                raise Exception(
                    f"Scene {index} audio is 0 KB:\n"
                    f"{audio_file}"
                )

            if not timing_file.exists():

                raise Exception(
                    f"Scene {index} timing missing:\n"
                    f"{timing_file}"
                )

            if timing_file.stat().st_size == 0:

                raise Exception(
                    f"Scene {index} timing is empty:\n"
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

        # ----------------------------------------------------
        # Legacy TTS does not need word timing.
        # ----------------------------------------------------

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

        if audio_file.stat().st_size == 0:

            audio_file.unlink(
                missing_ok=True
            )

            raise Exception(
                "Narration audio was created "
                "but is 0 KB."
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

        text = self._repair_mojibake(
            str(text).strip()
        )

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