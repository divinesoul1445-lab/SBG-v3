"""
SBG V3 Pipeline

CURRENT DEVELOPMENT MODE:

Chapter 1, Verse 1 ONLY

Architecture:

Excel
    ↓
Approved Scene 1–4 Narrations
    ↓
Fixed Scene Images
    ↓
Scene Composer
    ↓
Composed Scene Images
    ↓
Scene TTS
    ↓
Scene Subtitles
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
        │   ├── composed_image.png
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene2/
        │   ├── composed_image.png
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene3/
        │   ├── composed_image.png
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── scene4/
        │   ├── composed_image.png
        │   ├── narration.mp3
        │   ├── subtitles.srt
        │   └── scene_video.mp4
        │
        ├── final/
        │   ├── scenes.txt
        │   ├── merged_video.mp4
        │   └── final_video.mp4
        │
        └── pipeline_output.json


IMPORTANT:

The four fixed images from assets/images are NEVER modified.

SceneComposer creates the composed versions used by VideoRenderer.

VideoRenderer NEVER receives the raw source images.
"""


from pathlib import Path
import json

from config import SCENE_IMAGES

from modules.logger import Logger
from modules.sheet import ExcelContentManager
from modules.tts import TTSGenerator
from modules.subtitles import SubtitleGenerator
from modules.videos import VideoRenderer
from modules.scene_composer import SceneComposer


class Pipeline:

    def __init__(self):

        # ------------------------------------------------------
        # Excel
        # ------------------------------------------------------

        self.excel = ExcelContentManager()

        # ------------------------------------------------------
        # Scene Composer
        # ------------------------------------------------------

        self.scene_composer = SceneComposer()

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
        This pipeline is intentionally locked to:

            Chapter 1
            Verse 1
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
        Load the four fixed source images.

        These are NEVER passed directly to VideoRenderer.
        They are first passed through SceneComposer.
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
                    f"Scene {scene_number} source image "
                    f"not found:\n"
                    f"{image}"
                )

            if image.stat().st_size <= 0:

                raise Exception(
                    f"Scene {scene_number} source image "
                    f"is empty:\n"
                    f"{image}"
                )

            images.append(
                image
            )

        return images

    # ==========================================================
    # COMPOSE SCENE IMAGES
    # ==========================================================

    def _compose_scene_images(
        self,
        verse_folder,
        source_images,
        shloka,
        chapter,
        verse,
    ):

        """
        Convert the fixed source images into the polished
        scene images used by the video renderer.

        Input:

            assets/images/SceneX.jpeg

        Output:

            output/chapter_001/verse_001/sceneX/
                composed_image.png
        """

        if len(source_images) != 4:

            raise ValueError(
                "Expected exactly 4 source scene images."
            )

        composed_images = []

        for index, source_image in enumerate(
            source_images,
            start=1,
        ):

            scene_folder = (
                self._scene_output_folder(
                    verse_folder,
                    index,
                )
            )

            output_file = (
                scene_folder
                / "composed_image.png"
            )

            Logger.info(
                f"Composing Scene {index} image..."
            )

            Logger.info(
                f"Source image : {source_image}"
            )

            Logger.info(
                f"Output image : {output_file}"
            )

            composed_image = (
                self.scene_composer.compose(
                    image_file=source_image,
                    output_file=output_file,
                    shloka=shloka,
                    chapter=chapter,
                    verse=verse,
                    scene_number=index,
                    show_shloka=True,
                )
            )

            composed_image = Path(
                composed_image
            )

            if not composed_image.exists():

                raise FileNotFoundError(
                    f"Scene {index} composed image "
                    f"was not created:\n"
                    f"{composed_image}"
                )

            if composed_image.stat().st_size <= 0:

                raise Exception(
                    f"Scene {index} composed image "
                    f"is empty:\n"
                    f"{composed_image}"
                )

            Logger.success(
                f"Scene {index} composed image : "
                f"{composed_image}"
            )

            composed_images.append(
                composed_image
            )

        return composed_images

    # ==========================================================
    # SAVE SCENE CONTENT
    # ==========================================================

    def _save_scene_json(
        self,
        scene_folder,
        scene_number,
        narration,
        source_image_file,
        composed_image_file,
        audio_file,
        subtitle_file,
        video_file,
    ):

        data = {

            "chapter": 1,

            "verse": 1,

            "scene": scene_number,

            "narration": narration,

            "source_image_file": str(
                source_image_file
            ),

            "composed_image_file": str(
                composed_image_file
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

        file_path = Path(
            file_path
        )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
        source_image_files,
        composed_image_files,
        audio_files,
        subtitle_files,
        scene_videos,
        final_video,
    ):

        data = {

            "chapter": 1,

            "verse": 1,

            "scenes": [],

            "final_video": (
                str(final_video)
                if final_video is not None
                else None
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

                "source_image": str(
                    source_image_files[
                        index
                    ]
                ),

                "composed_image": str(
                    composed_image_files[
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

        verse_data = self._run_step(
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
            verse_data,
        )

        # ======================================================
        # 4. LOAD FIXED SOURCE IMAGES
        # ======================================================

        source_image_files = self._run_step(
            "Loading fixed scene images...",
            self._get_scene_images,
        )

        print()

        for index, image in enumerate(
            source_image_files,
            start=1,
        ):

            Logger.success(
                f"Scene {index} source image : "
                f"{image}"
            )

        # ======================================================
        # 5. COMPOSE SCENE IMAGES
        # ======================================================

        shloka = (
            verse_data.get(
                "Sanskrit"
            )
        )

        if (
            shloka is None
            or not str(
                shloka
            ).strip()
        ):

            raise Exception(
                "Sanskrit shloka is empty "
                "for Chapter 1, Verse 1."
            )

        composed_image_files = (
            self._run_step(
                "Composing Scene 1–4 images...",
                self._compose_scene_images,
                verse_folder,
                source_image_files,
                str(shloka).strip(),
                1,
                1,
            )
        )

        # ======================================================
        # 6. GENERATE SCENE AUDIO
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
                    f"Scene {index} audio "
                    f"was not created:\n"
                    f"{audio_file}"
                )

            if audio_file.stat().st_size <= 0:

                raise Exception(
                    f"Scene {index} audio "
                    f"is 0 KB:\n"
                    f"{audio_file}"
                )

            Logger.success(
                f"Scene {index} audio : "
                f"{audio_file}"
            )

            audio_files.append(
                audio_file
            )

        # ======================================================
        # 7. GENERATE SCENE SUBTITLES
        # ======================================================

        subtitle_files = self._run_step(
            "Generating subtitles...",
            self.subtitles.generate,
            scenes,
            audio_files,
            verse_folder,
        )

        if len(subtitle_files) != 4:

            raise ValueError(
                "Expected exactly 4 subtitle files."
            )

        # ======================================================
        # 8. RENDER INDIVIDUAL SCENE VIDEOS
        #
        # IMPORTANT:
        #
        # VideoRenderer receives composed images here,
        # NEVER the raw source images.
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

            Logger.info(
                f"Rendering Scene {index} "
                f"from composed image..."
            )

            Logger.info(
                f"Image : "
                f"{composed_image_files[index - 1]}"
            )

            scene_video = self._run_step(
                f"Rendering Scene {index} video...",
                self.video.render_scene,
                composed_image_files[
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
                    f"Scene {index} video "
                    f"was not created:\n"
                    f"{scene_video}"
                )

            if scene_video.stat().st_size <= 0:

                raise Exception(
                    f"Scene {index} video "
                    f"is empty:\n"
                    f"{scene_video}"
                )

            scene_videos.append(
                scene_video
            )

        # ======================================================
        # 9. PRINT SCENE DURATIONS
        # ======================================================

        self.video.print_scene_durations(
            audio_files
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

        video_file = Path(
            video_file
        )

        if not video_file.exists():

            raise FileNotFoundError(
                f"Final video was not created:\n"
                f"{video_file}"
            )

        if video_file.stat().st_size <= 0:

            raise Exception(
                f"Final video is empty:\n"
                f"{video_file}"
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
                scene_folder=scene_folder,
                scene_number=index,
                narration=scenes[
                    index - 1
                ],
                source_image_file=source_image_files[
                    index - 1
                ],
                composed_image_file=composed_image_files[
                    index - 1
                ],
                audio_file=audio_files[
                    index - 1
                ],
                subtitle_file=subtitle_files[
                    index - 1
                ],
                video_file=scene_videos[
                    index - 1
                ],
            )

        # ======================================================
        # 12. SAVE PIPELINE SUMMARY
        # ======================================================

        self._save_pipeline_summary(
            verse_folder=verse_folder,
            scenes=scenes,
            source_image_files=source_image_files,
            composed_image_files=composed_image_files,
            audio_files=audio_files,
            subtitle_files=subtitle_files,
            scene_videos=scene_videos,
            final_video=video_file,
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
                f"Scene {index} source image : "
                f"{source_image_files[index - 1]}"
            )

            Logger.success(
                f"Scene {index} composed image : "
                f"{composed_image_files[index - 1]}"
            )

            Logger.success(
                f"Scene {index} audio : "
                f"{audio_files[index - 1]}"
            )

            Logger.success(
                f"Scene {index} subtitles : "
                f"{subtitle_files[index - 1]}"
            )

            Logger.success(
                f"Scene {index} video : "
                f"{scene_videos[index - 1]}"
            )

        Logger.success(
            f"Final video : {video_file}"
        )

        return True