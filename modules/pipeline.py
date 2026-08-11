"""
SBG V3 Pipeline

Current development mode:

Chapter 1, Verse 1 ONLY

Excel
    ↓
Approved Scene 1–4 Narrations
    ↓
TTS - one audio file per scene
    ↓
Subtitles
    ↓
Fixed Asset Images
    ↓
Video Renderer
    ↓
final_video.mp4
"""

from pathlib import Path
import json

from config import OUTPUT_DIR, SCENE_IMAGES

from modules.logger import Logger
from modules.sheet import ExcelContentManager
from modules.tts import TTSGenerator
from modules.subtitles import SubtitleGenerator
from modules.videos import VideoRenderer


class Pipeline:

    def __init__(self):

        # ------------------------------------------------------
        # Excel
        # ------------------------------------------------------

        self.excel = ExcelContentManager()

        # ------------------------------------------------------
        # Output
        # ------------------------------------------------------

        self.output_dir = Path(
            OUTPUT_DIR
        )

        # ------------------------------------------------------
        # Audio
        # ------------------------------------------------------

        self.tts = TTSGenerator()

        # ------------------------------------------------------
        # Subtitles
        # ------------------------------------------------------

        self.subtitles = SubtitleGenerator()

        # ------------------------------------------------------
        # Video
        # ------------------------------------------------------

        self.video = VideoRenderer()

    # ==========================================================
    # STEP RUNNER
    # ==========================================================

    def _run_step(
        self,
        message,
        func,
        *args,
    ):

        Logger.info(message)

        result = func(*args)

        Logger.success(message)

        return result

    # ==========================================================
    # VERSE OUTPUT FOLDER
    # ==========================================================

    def _verse_output_folder(
        self,
        chapter: int,
        verse: int,
    ) -> Path:

        folder = (
            self.output_dir
            / f"chapter_{chapter:03d}"
            / f"verse_{verse:03d}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # ==========================================================
    # LOAD CHAPTER 1 VERSE 1 ONLY
    # ==========================================================

    def _get_verse(self):

        """
        IMPORTANT:

        This pipeline is intentionally locked to:

            Chapter 1
            Verse 1

        No other verse can be selected.
        """

        for row in self.excel._rows():

            try:

                chapter = int(
                    row.get("Chapter")
                )

                verse = int(
                    row.get("Verse")
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if chapter == 1 and verse == 1:

                return row

        raise Exception(
            "Chapter 1, Verse 1 was not found "
            "in the Excel content master."
        )

    # ==========================================================
    # PREPARE OUTPUT
    # ==========================================================

    def _prepare_output(
        self,
        verse,
    ):

        return self._verse_output_folder(
            1,
            1,
        )

    # ==========================================================
    # GET APPROVED SCENE NARRATIONS
    # ==========================================================

    def _get_scene_narrations(
        self,
        verse,
    ):

        scenes = [

            verse.get(
                "Scene 1 Narration"
            ),

            verse.get(
                "Scene 2 Narration"
            ),

            verse.get(
                "Scene 3 Narration"
            ),

            verse.get(
                "Scene 4 Narration"
            ),
        ]

        # ------------------------------------------------------
        # Validate all four scenes
        # ------------------------------------------------------

        for index, narration in enumerate(
            scenes,
            start=1,
        ):

            if (
                narration is None
                or not str(narration).strip()
            ):

                raise Exception(
                    f"Scene {index} narration is empty "
                    f"for Chapter 1, Verse 1."
                )

        return [
            str(narration).strip()
            for narration in scenes
        ]

    # ==========================================================
    # COMBINE NARRATION
    # ==========================================================

    def _combine_narration(
        self,
        scenes,
    ):

        return " ".join(
            scene.strip()
            for scene in scenes
        )

    # ==========================================================
    # GET FIXED SCENE IMAGES
    # ==========================================================

    def _get_scene_images(self):

        """
        DO NOT generate images.

        Use the four existing images from:

            assets/images/
        """

        images = []

        for scene_number in range(1, 5):

            if scene_number not in SCENE_IMAGES:

                raise Exception(
                    f"SCENE_IMAGES does not contain "
                    f"Scene {scene_number}."
                )

            image = Path(
                SCENE_IMAGES[scene_number]
            )

            if not image.exists():

                raise FileNotFoundError(
                    f"Scene {scene_number} image not found:\n"
                    f"{image}"
                )

            images.append(
                image
            )

        return images

    # ==========================================================
    # SAVE JSON
    # ==========================================================

    def _save_json(
        self,
        file_path,
        data,
    ):

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    def run(self):

        Logger.section(
            "Shree Bhagavad Gita AI Video Generator (V3)"
        )

        # ======================================================
        # 1. LOAD CHAPTER 1 VERSE 1
        # ======================================================

        verse = self._run_step(
            "Loading Chapter 1, Verse 1...",
            self._get_verse,
        )

        # ======================================================
        # 2. PREPARE OUTPUT
        # ======================================================

        output_folder = self._run_step(
            "Preparing output folder...",
            self._prepare_output,
            verse,
        )

        Logger.success(
            f"Output folder : {output_folder}"
        )

        # ======================================================
        # 3. LOAD APPROVED SCENE NARRATIONS
        # ======================================================

        scenes = self._run_step(
            "Loading approved scene narrations...",
            self._get_scene_narrations,
            verse,
        )

        # ======================================================
        # 4. COMBINE NARRATION
        #
        # Kept temporarily because the current subtitle
        # generator may still expect one text string.
        # ======================================================

        narration = self._combine_narration(
            scenes
        )

        # ======================================================
        # 5. LOAD FIXED ASSET IMAGES
        # ======================================================

        image_files = self._run_step(
            "Loading fixed scene images...",
            self._get_scene_images,
        )

        # ------------------------------------------------------
        # Display mapping
        # ------------------------------------------------------

        for index, image in enumerate(
            image_files,
            start=1,
        ):

            Logger.success(
                f"Scene {index} image : {image}"
            )

        # ======================================================
        # 6. SAVE SCENE CONTENT
        # ======================================================

        self._save_json(
            output_folder
            / "scene_narrations.json",
            {
                "chapter": 1,
                "verse": 1,

                "hook": (
                    verse.get("Hook")
                    or ""
                ),

                "life_lesson": (
                    verse.get("Life Lesson")
                    or ""
                ),

                "scene_1": scenes[0],
                "scene_2": scenes[1],
                "scene_3": scenes[2],
                "scene_4": scenes[3],

                "full_narration": narration,

                "images": [
                    str(image)
                    for image in image_files
                ],
            },
        )


        # print("\n===== SCENES DEBUG =====")

        # for index, scene in enumerate(
        #     scenes,
        #     start=1,
        # ):
        #     print(
        #         f"Scene {index}: "
        #         f"type={type(scene)}"
        #     )
        #     print(
        #         f"Value={scene!r}"
        #     )

        # print("========================\n")
        # ======================================================
        # 7. GENERATE ONE TTS FILE PER SCENE
        # ======================================================

        audio_files = self._run_step(
            "Generating narration per scene audio...",
            self.tts.generate_scenes,
            scenes,
            output_folder,
        )

        # ------------------------------------------------------
        # Verify all audio files
        # ------------------------------------------------------

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):

            audio_file = Path(
                audio_file
            )

            if not audio_file.exists():

                raise FileNotFoundError(
                    f"Scene {index} audio was not created:\n"
                    f"{audio_file}"
                )

            if audio_file.stat().st_size == 0:

                raise Exception(
                    f"Scene {index} audio is 0 KB:\n"
                    f"{audio_file}"
                )

            Logger.success(
                f"Scene {index} audio : {audio_file}"
            )

        # ======================================================
        # 8. GENERATE SUBTITLES
        # ======================================================

        scene_texts = scenes

        subtitle_file = self._run_step(
            "Generating subtitles...",
            self.subtitles.generate,
            scene_texts,
            audio_files,
            output_folder,
        )


        scene_data = self.video.get_scene_durations(
            audio_files,
            padding=0.3,
        )

        print()
        print(
            f"{'Scene':<8}"
            f"{'Narration':>12}"
            f"{'Image duration':>18}"
        )

        print("-" * 38)

        for scene in scene_data:

            print(
                f"{scene['scene']:<8}"
                f"{scene['narration']:>9.2f} sec"
                f"{scene['image_duration']:>14.2f} sec"
            )

        print()

        # ======================================================
        # 9. RENDER VIDEO
        #
        # IMPORTANT:
        #
        # VideoRenderer must now accept:
        #
        #     image_files
        #     audio_files
        #     subtitle_file
        #     output_folder
        #
        # NOT a single audio_file.
        # ======================================================

        video_file = self._run_step(
            "Rendering final video...",
            self.video.render,
            image_files,
            audio_files,
            subtitle_file,
            output_folder,
        )

        # ======================================================
        # 10. SAVE ASSET PATHS
        # ======================================================

        self._save_json(
            output_folder
            / "pipeline_output.json",
            {
                "chapter": 1,
                "verse": 1,

                "output_folder": str(
                    output_folder
                ),

                "scene_images": [
                    str(image)
                    for image in image_files
                ],

                "scene_audio": [
                    str(audio)
                    for audio in audio_files
                ],

                "subtitle_file": str(
                    subtitle_file
                ),

                "video_file": str(
                    video_file
                ),
            },
        )

        # ======================================================
        # 11. COMPLETE
        # ======================================================

        Logger.section(
            "Pipeline Complete"
        )

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):

            Logger.success(
                f"Scene {index} Audio : {audio_file}"
            )

        Logger.success(
            f"Subtitles : {subtitle_file}"
        )

        Logger.success(
            f"Video     : {video_file}"
        )

        return True