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
# Scene
# ============================================================

@dataclass(slots=True)
class Scene:

    id: Optional[int] = None

    verse_id: int = 0

    scene_number: int = 0

    duration: float = 5.0

    camera: str = ""

    focus: str = ""

    action: str = ""

    mood: str = ""

    created_at: Optional[str] = None


# ============================================================
# Image Prompt
# ============================================================

@dataclass(slots=True)
class ImagePrompt:

    id: Optional[int] = None

    scene_id: int = 0

    prompt: str = ""

    style: str = "Cinematic"

    negative_prompt: str = ""

    seed: Optional[int] = None

    created_at: Optional[str] = None


# ============================================================
# Generated Image
# ============================================================

@dataclass(slots=True)
class GeneratedImage:

    id: Optional[int] = None

    prompt_id: int = 0

    image_path: str = ""

    width: int = 1080

    height: int = 1920

    model: str = ""

    generation_time: float = 0.0

    created_at: Optional[str] = None


# ============================================================
# Assets
# ============================================================

@dataclass(slots=True)
class Asset:

    id: Optional[int] = None

    verse_id: int = 0

    audio_path: Optional[str] = None

    subtitle_path: Optional[str] = None

    video_path: Optional[str] = None

    thumbnail_path: Optional[str] = None

    completed: bool = False

    created_at: Optional[str] = None