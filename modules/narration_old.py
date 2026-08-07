"""
Narration Generator

Uses Ollama to generate engaging narration for one verse.
"""

from __future__ import annotations

from pathlib import Path

from ollama import Client

from config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
)

from modules.models import Verse


SYSTEM_PROMPT = """ 
You are Bhagwan Shri Krishna speaking to the world through the Bhagavad Gita.

Generate narration for ONE Bhagavad Gita verse.

Rules:

- Produce EXACTLY four sections.
- Begin each section with the marker shown below.
- Do not write any introduction.
- Do not write "Narration", "Output", "Scene", or explanations.
- Do not use Markdown.
- Speak naturally and spiritually.
- Keep the language simple and emotional.
- Total narration should be about 45–60 seconds.

Output format:

===SCENE1===
Recite the Sanskrit verse naturally.

===SCENE2===
Explain the literal meaning in simple English.

===SCENE3===
Explain the deeper spiritual meaning.

===SCENE4===
Explain the life lesson and how to apply it today.

"""

USER_PROMPT = """ 
Chapter: {chapter}

Verse: {verse}

Sanskrit:

{sanskrit}

English Translation:

{translation}

Life Lesson:

{life_lesson}
"""


class NarrationGenerator:

    def __init__(self):

        self.client = Client(
            host=OLLAMA_URL,
        )

        self.model = OLLAMA_MODEL

    # -----------------------------------------------------

    def generate(
    self,
    verse: Verse,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            options={
                    "temperature":0.3,
                    "num_predict":800,
                },
            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },

                {
                    "role": "user",
                    "content": USER_PROMPT,
                },
            ],
        )
        narration = response["message"]["content"].strip()
        return narration