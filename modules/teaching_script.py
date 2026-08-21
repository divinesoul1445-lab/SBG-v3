"""
Teaching Script Generator (V3)

Generates a short teaching experience
for one Bhagavad Gita verse.

Output Format:

<HOOK>
...
</HOOK>

<MEANING>
...
</MEANING>

<LESSON>
...
</LESSON>

<REFLECTION>
...
</REFLECTION>
"""

from __future__ import annotations

from pathlib import Path

from ollama import Client

from config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
)

from modules.models import (
    Verse,
    TeachingScript,
)


SYSTEM_PROMPT = (
    Path("prompts")
    / "teaching_system.txt"
).read_text(
    encoding="utf-8"
)

USER_PROMPT = (
    Path("prompts")
    / "teaching_user.txt"
).read_text(
    encoding="utf-8"
)


class TeachingScriptGenerator:

    def __init__(self):

        self.client = Client(
            host=OLLAMA_URL
        )

    # --------------------------------------------------

    def generate(
        self,
        verse: Verse,
    ) -> TeachingScript:

        prompt = USER_PROMPT.format(
            chapter=verse.chapter,
            verse=verse.verse,
            sanskrit=verse.sanskrit,
            transliteration=verse.transliteration,
            translation=verse.english_translation,
            life_lesson=verse.life_lesson,
        )

        response = self.client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0.1,
                "top_p": 0.8,
                "repeat_penalty": 1.1,
                "num_predict": 1200,
                "think" : False,
            },
        )

        # print("=" * 80)
        # print("FULL RESPONSE")
        # print("=" * 80)
        # print(response)
        # print("=" * 80)

        content = response["message"]["content"].strip()
        # print("CONTENT =", repr(content))

        return self._parse_script(
            verse.id or verse.verse,
            content,
        )
    # --------------------------------------------------
    # Parse Teaching Script
    # --------------------------------------------------

    def _parse_script(
        self,
        verse_id: int,
        content: str,
    ) -> TeachingScript:

        hook = self._extract_tag(
            content,
            "HOOK",
        )

        meaning = self._extract_tag(
            content,
            "MEANING",
        )

        lesson = self._extract_tag(
            content,
            "LESSON",
        )

        reflection = self._extract_tag(
            content,
            "REFLECTION",
        )

        self._validate_section(
            "HOOK",
            hook,
            max_words=8,
        )

        self._validate_section(
            "MEANING",
            meaning,
            max_words=12,
        )

        self._validate_section(
            "LESSON",
            lesson,
            max_words=10,
        )

        self._validate_section(
            "REFLECTION",
            reflection,
            max_words=8,
        )

        full_script = self._build_full_script(

            hook,

            meaning,

            lesson,

            reflection,

        )

        return TeachingScript(

            verse_id=verse_id,

            hook=hook,

            meaning=meaning,

            lesson=lesson,

            reflection=reflection,

            full_script=full_script,

        )
        # --------------------------------------------------
    # Extract XML Tag
    # --------------------------------------------------

    def _extract_tag(
        self,
        text: str,
        tag: str,
    ) -> str:

        import re

        pattern = rf"<{tag}>\s*(.*?)\s*</{tag}>"

        match = re.search(
            pattern,
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if not match:

            raise Exception(
                f"Missing <{tag}> section."
            )

        return match.group(1).strip()


    # --------------------------------------------------
    # Validate Section
    # --------------------------------------------------

    def _validate_section(
        self,
        name: str,
        text: str,
        max_words: int,
    ):

        if not text:

            raise Exception(
                f"{name} is empty."
            )

        words = len(text.split())

        if words > max_words:

            raise Exception(

                f"{name} exceeds "

                f"{max_words} words "

                f"({words} found)."

            )


    # --------------------------------------------------
    # Build Narration
    # --------------------------------------------------

    def _build_full_script(

        self,

        hook: str,

        meaning: str,

        lesson: str,

        reflection: str,

    ) -> str:

        return " ".join([

            hook.strip(),

            meaning.strip(),

            lesson.strip(),

            reflection.strip(),

        ])