"""
Repository

The ONLY module allowed to access SQLite.

All CRUD operations go through this class.
"""

from __future__ import annotations

from typing import Optional

from modules.database import db
from modules.models import (
    Verse,
    Scene,
    ImagePrompt,
    GeneratedImage,
    Asset,
)


class Repository:

    # =====================================================
    # VERSES
    # =====================================================


    def add_verse(self, verse: Verse) -> int:

        cursor = db.execute(
            """
            INSERT INTO verses(
                chapter,
                verse,
                sanskrit,
                transliteration,
                english_translation,
                life_lesson,
                status
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                verse.chapter,
                verse.verse,
                verse.sanskrit,
                verse.transliteration,
                verse.english_translation,
                verse.life_lesson,
                verse.status,
            ),
        )

        return cursor.lastrowid

    # -----------------------------------------------------

    def get_verse_by_reference(
    self,
    chapter: int,
    verse: int,
    ):

        row = db.fetchone(
            """
            SELECT *
            FROM verses
            WHERE chapter = ?
            AND verse = ?
            """,
            (
                chapter,
                verse,
            ),
        )

        if row is None:
            return None
        return self._row_to_verse(row)

    # -----------------------------------------------------


    def get_next_pending_verse(self) -> Optional[Verse]:

        row = db.fetchone(
            """
            SELECT *
            FROM verses
            WHERE status='Pending'
            ORDER BY chapter, verse
            LIMIT 1
            """
        )

        print(row)

        if row is None:
            return None

        return self._row_to_verse(row)

    # -----------------------------------------------------

    def update_narration(
        self,
        verse_id: int,
        narration: str,
    ):

        db.execute(
            """
            UPDATE verses

            SET narration=?,
                updated_at=CURRENT_TIMESTAMP

            WHERE id=?
            """,
            (
                narration,
                verse_id,
            ),
        )

    # -----------------------------------------------------

    def update_life_lesson(
        self,
        verse_id: int,
        lesson: str,
    ):

        db.execute(
            """
            UPDATE verses

            SET life_lesson=?,
                updated_at=CURRENT_TIMESTAMP

            WHERE id=?
            """,
            (
                lesson,
                verse_id,
            ),
        )

    # -----------------------------------------------------

    def update_status(
        self,
        verse_id: int,
        status: str,
    ):

        db.execute(
            """
            UPDATE verses

            SET status=?,
                updated_at=CURRENT_TIMESTAMP

            WHERE id=?
            """,
            (
                status,
                verse_id,
            ),
        )

    # =====================================================
    # SCENES
    # =====================================================

    def add_scene(
        self,
        scene: Scene,
    ) -> int:

        cursor = db.execute(
            """
            INSERT INTO scenes(

                verse_id,

                scene_number,

                duration,

                camera,

                focus,

                action,

                mood

            )

            VALUES(?,?,?,?,?,?,?)
            """,
            (
                scene.verse_id,
                scene.scene_number,
                scene.duration,
                scene.camera,
                scene.focus,
                scene.action,
                scene.mood,
            ),
        )

        return cursor.lastrowid

    # =====================================================
    # IMAGE PROMPTS
    # =====================================================

    def add_prompt(
        self,
        prompt: ImagePrompt,
    ) -> int:

        cursor = db.execute(
            """
            INSERT INTO image_prompts(

                scene_id,

                prompt,

                style,

                negative_prompt,

                seed

            )

            VALUES(?,?,?,?,?)
            """,
            (
                prompt.scene_id,
                prompt.prompt,
                prompt.style,
                prompt.negative_prompt,
                prompt.seed,
            ),
        )

        return cursor.lastrowid

    # =====================================================
    # GENERATED IMAGES
    # =====================================================

    def add_image(
        self,
        image: GeneratedImage,
    ) -> int:

        cursor = db.execute(
            """
            INSERT INTO images(

                prompt_id,

                image_path,

                width,

                height,

                model,

                generation_time

            )

            VALUES(?,?,?,?,?,?)
            """,
            (
                image.prompt_id,
                image.image_path,
                image.width,
                image.height,
                image.model,
                image.generation_time,
            ),
        )

        return cursor.lastrowid

    # =====================================================
    # ASSETS
    # =====================================================

    def save_asset(
        self,
        asset: Asset,
    ):

        db.execute(
            """
            INSERT OR REPLACE INTO assets(

                verse_id,

                audio_path,

                subtitle_path,

                video_path,

                thumbnail_path,

                completed

            )

            VALUES(?,?,?,?,?,?)
            """,
            (
                asset.verse_id,
                asset.audio_path,
                asset.subtitle_path,
                asset.video_path,
                asset.thumbnail_path,
                int(asset.completed),
            ),
        )

    def _row_to_verse(self, row) -> Verse:

        return Verse(
            id=row["id"],
            chapter=row["chapter"],
            verse=row["verse"],
            sanskrit=row["sanskrit"],
            transliteration=row["transliteration"],
            english_translation=row["english_translation"],
            life_lesson=row["life_lesson"],
            generated_narration=row["narration"],
            youtube_title=row["youtube_title"],
            youtube_description=row["youtube_description"],
            hashtags=row["hashtags"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
