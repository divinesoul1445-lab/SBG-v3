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
timestamps and is used by subtitles.py for
real speech synchronization.
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

        text = str(text).strip()

        if not text:
            raise Exception(
                "TTS received empty text."
            )

        print()
        print("=" * 80)
        print("EDGE TTS DEBUG")
        print("=" * 80)

        print("Voice :", voice)
        print("Rate  :", RATE)
        print("Volume:", VOLUME)
        print("Text  :", repr(text))
        print("Audio :", output_file)
        print("Timing:", timing_file)

        print("=" * 80)
        print()

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=RATE,
            volume=VOLUME,
            boundary="WordBoundary",
        )

        word_boundaries = []

        # ----------------------------------------------------
        # IMPORTANT
        #
        # We use stream() instead of save().
        #
        # This allows us to capture:
        #
        #     WordBoundary
        #
        # events while simultaneously writing the MP3.
        # ----------------------------------------------------

        with open(
            output_file,
            "wb",
        ) as audio:

            async for chunk in communicate.stream():

                chunk_type = chunk.get(
                    "type"
                )

                # ------------------------------------------------
                # AUDIO DATA
                # ------------------------------------------------

                if chunk_type == "audio":

                    data = chunk.get(
                        "data"
                    )

                    if data:

                        audio.write(
                            data
                        )

                # ------------------------------------------------
                # WORD BOUNDARY
                # ------------------------------------------------

                elif chunk_type == "WordBoundary":

                    offset = chunk.get(
                        "offset"
                    )

                    duration = chunk.get(
                        "duration"
                    )

                    boundary_text = chunk.get(
                        "text"
                    )

                    if (
                        offset is None
                        or duration is None
                    ):

                        continue

                    # Edge TTS uses 100-nanosecond
                    # units for offset/duration.
                    #
                    # Convert to seconds.

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
                                ""
                                if boundary_text is None
                                else str(
                                    boundary_text
                                ),

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
        # Verify word timings
        # ----------------------------------------------------

        if not word_boundaries:

            raise Exception(
                "Edge TTS generated audio but "
                "returned no WordBoundary events.\n"
                "Cannot create synchronized subtitles."
            )

        # ----------------------------------------------------
        # Save timing JSON
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
        # Output
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
        # Reuse ONLY when BOTH files are valid
        #
        # This is important.
        #
        # Existing MP3 files generated by the old TTS code
        # do NOT have timing information.
        # ----------------------------------------------------

        if (
            audio_file.exists()
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
        # Remove incomplete old files
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

        print(
            f"Scene {scene_number} text:"
        )

        print(
            repr(text)
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
        # Verify audio
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
        # Verify timing
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
        Legacy method.

        Generates:

            teaching.mp3

        This method is kept for compatibility with older
        pipeline code.

        Word timing is not required here.
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

            audio_file.unlink()

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
        # Legacy generation
        # ----------------------------------------------------

        asyncio.run(
            self._generate_audio_only(
                text=text,
                output_file=audio_file,
                voice=ENGLISH_VOICE,
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
    # LEGACY AUDIO-ONLY GENERATOR
    # ========================================================

    async def _generate_audio_only(
        self,
        text: str,
        output_file: Path,
        voice: str,
    ):

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=RATE,
            volume=VOLUME,
            boundary="WordBoundary",
        )

        with open(
            output_file,
            "wb",
        ) as audio:

            async for chunk in communicate.stream():

                if chunk.get(
                    "type"
                ) == "audio":

                    data = chunk.get(
                        "data"
                    )

                    if data:

                        audio.write(
                            data
                        )