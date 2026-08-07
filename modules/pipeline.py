"""
SBG V3 Pipeline

Simple orchestration.

Verse
    ↓
Narration
    ↓
Prompt Templates
    ↓
Images
    ↓
Audio
    ↓
Subtitles
    ↓
Video
"""

from pathlib import Path
import time

from modules.logger import Logger
from modules.repository import Repository
from modules.teaching_script import TeachingScriptGenerator
from modules.scene_generator import SceneGenerator

from modules.tts import TTSGenerator
from modules.subtitles import SubtitleGenerator
from modules.videos import VideoRenderer



class Pipeline:

    def __init__(self):
        self.repository = Repository()
        self.teaching_script_generator = TeachingScriptGenerator()
        self.scene_generator = SceneGenerator()
        self.tts = TTSGenerator()
        self.subtitles = SubtitleGenerator()
        self.video = VideoRenderer()

    # --------------------------------------------------
    # Step Runner
    # --------------------------------------------------

    def _run_step(
        self,
        title,
        func,
        *args,
    ):
        Logger.info(title)
        start = time.time()
        result = func(*args)
        Logger.success(
            f"{title} ({time.time()-start:.2f}s)"
        )

        return result
        # --------------------------------------------------
    # Load Verse
    # --------------------------------------------------

    # def _get_verse(self):

    #     verse = self.repository.get_next_pending_verse()

    #     if verse is None:

    #         raise Exception(
    #             "No pending verse found."
    #         )

    #     return verse
    def _get_verse(self):

        return self.repository.get_verse(
            chapter=1,
            verse=1,
        )


    # --------------------------------------------------
    # Prepare Output Folder
    # --------------------------------------------------

    def _prepare_output(
        self,
        verse,
    ) -> Path:

        output = (
            Path("output")
            / f"chapter_{verse.chapter:02d}"
            / f"verse_{verse.verse:03d}"
        )

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        return output


    # --------------------------------------------------
    # Main Pipeline
    # --------------------------------------------------

    def run(self):

        Logger.section(
            "SBG V3 Pipeline"
        )

        verse = self._run_step(
            "Loading verse...",
            self._get_verse,
        )

        output_folder = self._run_step(
            "Preparing output folder...",
            self._prepare_output,
            verse,
        )

        script = self._run_step(
            "Generating teaching script...",
            self.teaching_script_generator.generate,
            verse
        )


        scenes  = self._run_step(
            "Preparing visual sequence...",
            self.scene_generator.generate,
            verse,
            script,
            )

        image_files = [scene["image"] for scene in scenes]

        audio_file = self._run_step(
            "Generating narration audio...",
            self.tts.generate,
            script.full_script,
            output_folder,
        )

        subtitle_file = self._run_step(
            "Generating subtitles...",
            self.subtitles.generate,
            script.full_script,
            output_folder,
        )

        video_file = self._run_step(
            "Rendering final video...",
            self.video.render,
            image_files,
            audio_file,
            subtitle_file,
            output_folder,
        )

        self.repository.update_status(
            verse.verse,
            "Completed",
        )

        Logger.section(
            "Pipeline Complete"
        )

        Logger.success(
            f"Video : {video_file}"
        )

        return True