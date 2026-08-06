"""
SQLite Database Manager

Creates the database automatically.
Creates missing tables.
Provides a singleton connection.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from config import DATABASE_FILE


class Database:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):

        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            DATABASE_FILE,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        self.connection.execute(
            "PRAGMA journal_mode = WAL;"
        )

        self.connection.execute(
            "PRAGMA synchronous = NORMAL;"
        )

        self.create_tables()

    # --------------------------------------------------

    def create_tables(self):

        cursor = self.connection.cursor()

        # ==================================================
        # VERSES
        # ==================================================


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS verses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter INTEGER NOT NULL,
                verse INTEGER NOT NULL,
                sanskrit TEXT,
                transliteration TEXT,
                english_translation TEXT,
                life_lesson TEXT,
                narration TEXT,
                youtube_title TEXT,
                youtube_description TEXT,
                hashtags TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chapter, verse)

            );

            """
        )

        # ==================================================
        # SCENE IMAGES
        # ==================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            scene_number INTEGER,
            duration REAL,
            camera TEXT,
            focus TEXT,
            action TEXT,
            mood TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (verse_id)
            REFERENCES verses(id)
            ON DELETE CASCADE
        );
            """
        )

        # ==================================================
        # image prompts
        # ==================================================


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER NOT NULL,
                prompt TEXT,
                style TEXT,
                negative_prompt TEXT,
                seed INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(scene_id)
                REFERENCES scenes(id)
                ON DELETE CASCADE
            );
            """
        )

        # ==================================================
        # image prompts
        # ==================================================

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER NOT NULL,
            image_path TEXT,
            width INTEGER,
            height INTEGER,
            model TEXT,
            generation_time REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prompt_id)
            REFERENCES image_prompts(id)
            ON DELETE CASCADE
        );
            """
        )

        # ==================================================
        # ASSETS
        # ==================================================


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verse_id INTEGER UNIQUE,
                audio_path TEXT,
                subtitle_path TEXT,
                video_path TEXT,
                thumbnail_path TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(verse_id)
                REFERENCES verses(id)
                ON DELETE CASCADE
            );
            """
        )

        self.connection.commit()

    # --------------------------------------------------

    def execute(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        cursor = self.connection.cursor()

        cursor.execute(
            query,
            parameters,
        )

        self.connection.commit()

        return cursor

    # --------------------------------------------------

    def executemany(
        self,
        query,
        values,
    ):

        cursor = self.connection.cursor()

        cursor.executemany(
            query,
            values,
        )

        self.connection.commit()

        return cursor

    # --------------------------------------------------

    def fetchone(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        cursor = self.connection.cursor()

        cursor.execute(
            query,
            parameters,
        )

        return cursor.fetchone()

    # --------------------------------------------------

    def fetchall(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        cursor = self.connection.cursor()

        cursor.execute(
            query,
            parameters,
        )

        return cursor.fetchall()

    # --------------------------------------------------

    def close(self):

        self.connection.close()


db = Database()