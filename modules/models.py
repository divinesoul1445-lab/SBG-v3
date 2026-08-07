"""
Domain Models

These dataclasses represent the business objects used
throughout the application.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ============================================================
# Verse
# ============================================================

@dataclass(slots=True)
class Verse:

    id: Optional[int] = None

    chapter: int = 0

    verse: int = 0

    sanskrit: str = ""

    transliteration: str = ""

    english_translation: str = ""

    life_lesson: Optional[str] = None

    generated_narration: Optional[str] = None

    youtube_title: Optional[str] = None

    youtube_description: Optional[str] = None

    hashtags: Optional[str] = None

    status: str = "Pending"

    created_at: Optional[str] = None

    updated_at: Optional[str] = None


# ============================================================
# Teaching Script
# ============================================================

# ============================================================
# Teaching Script
# ============================================================

@dataclass(slots=True)
class TeachingScript:

    verse_id: int = 0

    hook: str = ""

    meaning: str = ""

    lesson: str = ""

    reflection: str = ""

    full_script: str = ""
