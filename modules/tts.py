"""
Text To Speech

Uses Microsoft Edge TTS

Generates narration.mp3
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts


VOICE = "en-IN-PrabhatNeural"

RATE = "+0%"

VOLUME = "+0%"


class TTSGenerator:

    def __init__(self):

        pass

    async def _generate(
        self,
        text: str,
        output_file: Path,
    ):

        communicate = edge_tts.Communicate(
            text=text,
            voice=VOICE,
            rate=RATE,
            volume=VOLUME,
        )

        await communicate.save(str(output_file))

    def generate(
        self,
        narration: str,
        output_folder: Path,
    ) -> Path:

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio_file = output_folder / "narration.mp3"

        if audio_file.exists():
            return audio_file

        if not narration:
            raise Exception(
                "Narration is empty."
            )

        asyncio.run(
            self._generate(
                narration,
                audio_file,
            )
        )

        return audio_file