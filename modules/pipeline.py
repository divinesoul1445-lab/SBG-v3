"""
SBG V3 Pipeline

CURRENT DEVELOPMENT MODE:

Chapter 1, Verse 1 ONLY

Architecture:

Excel
    ↓
Approved Scene 1–4 Narrations
    ↓
Scene TTS
    ↓
Scene Subtitles
    ↓
Fixed Asset Images
    ↓
Individual Scene Videos
    ↓
Merge Scene Videos
    ↓
Background Music
    ↓
Final Video

Output:

output/
└── chapter_001/
    └── verse_001/
        ├── scene1/
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene2/
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene3/
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene4/
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        └── final/
            ├── scenes.txt
            ├── merged_video.mp4
            └── final_video.mp4

Images are NEVER generated.
The four fixed images from assets/images are used.
"""


from pathlib import Path
import json

from config import SCENE_IMAGES

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
        # TTS
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

        # ------------------------------------------------------
        # Project output
        # ------------------------------------------------------

        self.output_dir = Path(
            "output"
        )

    # ==========================================================
    # STEP RUNNER
    # ==========================================================

    def _run_step(
        self,
        message,
        func,
        *args,
    ):

        Logger.info(
            message
        )

        result = func(
            *args
        )

        Logger.success(
            message
        )

        return result

    # ==========================================================
    # VERSE OUTPUT FOLDER
    # ==========================================================

    def _verse_output_folder(
        self,
        chapter,
        verse,
    ):

        folder = (
            self.output_dir
            / f"chapter_{chapter:03d}"
            / f"verse_{verse:03d}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        Logger.success(
            f"Output folder : {folder.resolve()}"
        )

        return folder

    # ==========================================================
    # SCENE OUTPUT FOLDER
    # ==========================================================

    def _scene_output_folder(
        self,
        verse_folder,
        scene_number,
    ):

        folder = (
            Path(verse_folder)
            / f"scene{scene_number}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # ==========================================================
    # FINAL OUTPUT FOLDER
    # ==========================================================

    def _final_output_folder(
        self,
        verse_folder,
    ):

        folder = (
            Path(verse_folder)
            / "final"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # ==========================================================
    # LOAD CHAPTER 1 VERSE 1
    # ==========================================================

    def _get_verse(
        self,
    ):

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
                    row.get(
                        "Chapter"
                    )
                )

                verse = int(
                    row.get(
                        "Verse"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if (
                chapter == 1
                and verse == 1
            ):

                return row

        raise Exception(
            "Chapter 1, Verse 1 was not found "
            "in the Excel content master."
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
        # Validate
        # ------------------------------------------------------

        for index, narration in enumerate(
            scenes,
            start=1,
        ):

            if (
                narration is None
                or not str(
                    narration
                ).strip()
            ):

                raise Exception(
                    f"Scene {index} narration is empty "
                    f"for Chapter 1, Verse 1."
                )

        return [
            str(
                narration
            ).strip()
            for narration in scenes
        ]

    # ==========================================================
    # GET FIXED SCENE IMAGES
    # ==========================================================

    def _get_scene_images(
        self,
    ):

        """
        DO NOT generate images.

        Use the four existing fixed images
        from assets/images.
        """

        images = []

        for scene_number in range(
            1,
            5,
        ):

            if scene_number not in SCENE_IMAGES:

                raise Exception(
                    f"Scene {scene_number} image mapping "
                    f"is missing from SCENE_IMAGES."
                )

            image = Path(
                SCENE_IMAGES[
                    scene_number
                ]
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
    # SAVE SCENE CONTENT
    # ==========================================================

    def _save_scene_json(
        self,
        scene_folder,
        scene_number,
        narration,
        image_file,
        audio_file,
        subtitle_file,
        video_file,
    ):

        data = {

            "chapter": 1,

            "verse": 1,

            "scene": scene_number,

            "narration": narration,

            "image_file": str(
                image_file
            ),

            "audio_file": str(
                audio_file
            ),

            "subtitle_file": str(
                subtitle_file
            ),

            "video_file": str(
                video_file
            ),
        }

        self._save_json(
            Path(scene_folder)
            / "scene.json",
            data,
        )

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
    # SAVE PIPELINE SUMMARY
    # ==========================================================

    def _save_pipeline_summary(
        self,
        verse_folder,
        scenes,
        image_files,
        audio_files,
        subtitle_files,
        scene_videos,
        final_video,
    ):

        data = {

            "chapter": 1,

            "verse": 1,

            "scenes": [],

            "final_video": str(
                final_video
            ),
        }

        for index in range(
            4
        ):

            data[
                "scenes"
            ].append({

                "scene": index + 1,

                "narration": scenes[
                    index
                ],

                "image": str(
                    image_files[
                        index
                    ]
                ),

                "audio": str(
                    audio_files[
                        index
                    ]
                ),

                "subtitle": str(
                    subtitle_files[
                        index
                    ]
                ),

                "video": str(
                    scene_videos[
                        index
                    ]
                ),
            })

        self._save_json(
            Path(
                verse_folder
            )
            / "pipeline_output.json",
            data,
        )

    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    def run(
        self,
    ):

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
        # 2. PREPARE VERSE OUTPUT
        # ======================================================

        verse_folder = self._run_step(
            "Preparing output folder...",
            self._verse_output_folder,
            1,
            1,
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
        # 4. LOAD FIXED IMAGES
        # ======================================================

        image_files = self._run_step(
            "Loading fixed scene images...",
            self._get_scene_images,
        )

        # ------------------------------------------------------
        # Display image mapping
        # ------------------------------------------------------

        for index, image in enumerate(
            image_files,
            start=1,
        ):

            Logger.success(
                f"Scene {index} image : {image}"
            )

        # ======================================================
        # 5. GENERATE SCENE AUDIO
        # ======================================================

        audio_files = []

        for index, narration in enumerate(
            scenes,
            start=1,
        ):

            scene_folder = (
                self._scene_output_folder(
                    verse_folder,
                    index,
                )
            )

            audio_file = self._run_step(
                f"Generating Scene {index} narration...",
                self.tts.generate_scene,
                index,
                narration,
                scene_folder,
            )

            audio_file = Path(
                audio_file
            )

            if not audio_file.exists():

                raise FileNotFoundError(
                    f"Scene {index} audio was not created:\n"
                    f"{audio_file}"
                )

            if audio_file.stat().st_size <= 0:

                raise Exception(
                    f"Scene {index} audio is 0 KB:\n"
                    f"{audio_file}"
                )

            Logger.success(
                f"Scene {index} audio : {audio_file}"
            )

            audio_files.append(
                audio_file
            )

        # ======================================================
        # 6. GENERATE SCENE SUBTITLES
        # ======================================================

        subtitle_files = self._run_step(
            "Generating subtitles...",
            self.subtitles.generate,
            scenes,
            audio_files,
            verse_folder,
        )


        
        # ======================================================
        # 7. RENDER INDIVIDUAL SCENE VIDEOS
        # ======================================================

        scene_videos = []

        for index in range(
            1,
            5,
        ):

            scene_folder = (
                self._scene_output_folder(
                    verse_folder,
                    index,
                )
            )

            scene_video = (
                scene_folder
                / "scene_video.mp4"
            )

            scene_video = self._run_step(
                f"Rendering Scene {index} video...",
                self.video.render_scene,
                image_files[
                    index - 1
                ],
                audio_files[
                    index - 1
                ],
                subtitle_files[
                    index - 1
                ],
                scene_video,
            )

            scene_video = Path(
                scene_video
            )

            if not scene_video.exists():

                raise FileNotFoundError(
                    f"Scene {index} video was not created:\n"
                    f"{scene_video}"
                )

            if scene_video.stat().st_size <= 0:

                raise Exception(
                    f"Scene {index} video is empty:\n"
                    f"{scene_video}"
                )

            scene_videos.append(
                scene_video
            )

        # ======================================================
        # 8. PRINT SCENE DURATIONS
        # ======================================================

        self.video.print_scene_durations(
            audio_files
        )

        # ======================================================
        # 9. RENDER EACH SCENE VIDEO
        # ======================================================

        scene_videos = []

        for index in range(1, 5):

            scene_folder = (
                verse_folder
                / f"scene{index}"
            )

            scene_video = (
                scene_folder
                / "scene_video.mp4"
            )

            scene_video = self._run_step(
                f"Rendering Scene {index} video...",
                self.video.render_scene,
                image_files[index - 1],
                audio_files[index - 1],
                subtitle_files[index - 1],
                scene_video,
            )

            scene_videos.append(
                scene_video
            )

        # ======================================================
        # 10. MERGE ALL SCENE VIDEOS
        # ======================================================

        video_file = self._run_step(
            "Merging scene videos...",
            self.video.merge_scenes,
            scene_videos,
            verse_folder,
        )

        # ======================================================
        # 11. SAVE SCENE JSON FILES
        # ======================================================

        for index in range(
            1,
            5,
        ):

            scene_folder = (
                self._scene_output_folder(
                    verse_folder,
                    index,
                )
            )

            self._save_scene_json(
                scene_folder,
                index,
                scenes[
                    index - 1
                ],
                image_files[
                    index - 1
                ],
                audio_files[
                    index - 1
                ],
                subtitle_files[
                    index - 1
                ],
                scene_videos[
                    index - 1
                ],
            )

        # ======================================================
        # 12. SAVE PIPELINE SUMMARY
        # ======================================================

        self._save_pipeline_summary(
            verse_folder,
            scenes,
            image_files,
            audio_files,
            subtitle_files,
            scene_videos,
            video_file,
        )

        # ======================================================
        # 13. COMPLETE
        # ======================================================

        Logger.section(
            "Pipeline Complete"
        )

        for index in range(
            1,
            5,
        ):

            Logger.success(
                f"Scene {index} video : "
                f"{scene_videos[index - 1]}"
            )

        Logger.success(
            f"Final video : {video_file}"
        )

        return True