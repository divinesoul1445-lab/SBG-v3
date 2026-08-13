"""
Text To Speech

Uses Microsoft Edge TTS.

Scene voices:
    Scene 1 -> English
    Scene 2 -> Hindi/Sanskrit
    Scene 3 -> English
    Scene 4 -> English

Generates:
    scene1.mp3
    scene2.mp3
    scene3.mp3
    scene4.mp3
"""

import asyncio
from pathlib import Path

import edge_tts


# ============================================================
# VOICES
# ============================================================

ENGLISH_VOICE = "en-IN-PrabhatNeural"

# Available hi-IN voice confirmed on this machine
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
    # GENERATE AUDIO
    # ========================================================

    async def _generate(
        self,
        text: str,
        output_file: Path,
        voice: str,
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
        print("Output:", output_file)

        print("=" * 80)
        print()

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=RATE,
            volume=VOLUME,
        )

        await communicate.save(
            str(output_file)
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

        text = str(text).strip()

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

        # ----------------------------------------------------
        # Voice
        # ----------------------------------------------------

        voice = self._get_voice(
            scene_number
        )

        # ----------------------------------------------------
        # Reuse only valid audio
        # ----------------------------------------------------

        if (
            audio_file.exists()
            and audio_file.stat().st_size > 0
        ):
            print(
                f"✓ Scene {scene_number} audio already exists:"
            )

            print(
                f"  {audio_file}"
            )

            return audio_file

        # ----------------------------------------------------
        # Delete broken/empty audio
        # ----------------------------------------------------

        if audio_file.exists():

            print(
                f"Removing invalid Scene {scene_number} audio:"
            )

            print(
                f"  {audio_file}"
            )

            audio_file.unlink()

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        print(
            f"Generating Scene {scene_number} audio..."
        )

        print(
            f"Scene {scene_number} text:"
        )

        print(
            repr(text)
        )

        asyncio.run(
            self._generate(
                text,
                audio_file,
                voice,
            )
        )

        # ----------------------------------------------------
        # Verify
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

        print(
            f"✓ Scene {scene_number} audio created:"
        )

        print(
            f"  {audio_file}"
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

            audio_file = self.generate_scene(
                scene_number=index,
                text=text,
                output_folder=output_folder,
            )

            audio_files.append(
                audio_file
            )

        # ----------------------------------------------------
        # Final validation
        # ----------------------------------------------------

        if len(audio_files) != 4:
            raise Exception(
                "TTS did not produce four scene audio files."
            )

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):

            audio_file = Path(
                audio_file
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

        Generates one English narration file:

            teaching.mp3

        Kept for compatibility with older pipeline code.
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

        text = str(text).strip()

        if not text:
            raise Exception(
                "Input text is empty."
            )

        asyncio.run(
            self._generate(
                text,
                audio_file,
                ENGLISH_VOICE,
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