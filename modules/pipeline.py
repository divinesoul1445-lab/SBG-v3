"""
SBG V3 Pipeline

CURRENT DEVELOPMENT MODE:

Chapter 1, Verse 1 ONLY

Architecture:

Excel
    â†“
Approved Scene 1 to 4 Narrations
    â†“
Fixed Scene Images
    â†“
Scene Composer
    â†“
Composed Scene Images
    â†“
Scene TTS
    â†“
Scene Subtitles
    â†“
Individual Scene Videos
    â†“
Merge Scene Videos
    â†“
Background Music
    â†“
Final Video


Output:

output/
â””â”€â”€ chapter_001/
    â””â”€â”€ verse_001/
        â”œâ”€â”€ scene1/
        â”‚   â”œâ”€â”€ composed_image.png
        â”‚   â”œâ”€â”€ narration.mp3
        â”‚   â”œâ”€â”€ subtitles.srt
        â”‚   â””â”€â”€ scene_video.mp4
        â”‚
        â”œâ”€â”€ scene2/
        â”‚   â”œâ”€â”€ composed_image.png
        â”‚   â”œâ”€â”€ narration.mp3
        â”‚   â”œâ”€â”€ subtitles.srt
        â”‚   â””â”€â”€ scene_video.mp4
        â”‚
        â”œâ”€â”€ scene3/
        â”‚   â”œâ”€â”€ composed_image.png
        â”‚   â”œâ”€â”€ narration.mp3
        â”‚   â”œâ”€â”€ subtitles.srt
        â”‚   â””â”€â”€ scene_video.mp4
        â”‚
        â”œâ”€â”€ scene4/
        â”‚   â”œâ”€â”€ composed_image.png
        â”‚   â”œâ”€â”€ narration.mp3
        â”‚   â”œâ”€â”€ subtitles.srt
        â”‚   â””â”€â”€ scene_video.mp4
        â”‚
        â”œâ”€â”€ final/
        â”‚   â”œâ”€â”€ scenes.txt
        â”‚   â”œâ”€â”€ merged_video.mp4
        â”‚   â””â”€â”€ final_video.mp4
        â”‚
        â””â”€â”€ pipeline_output.json


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
from modules.shloka_highlighter import create_shloka_overlay_from_narration
import subprocess

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
        **kwargs,
    ):

        Logger.info(
            message
        )

        result = func(
            *args,
            **kwargs,
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

    def _get_verse(self, chapter=1, verse=1):
        """Load the requested verse from the approved workbook."""
        return self.excel.get_verse(chapter, verse)

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
                    f"for Chapter {self.current_chapter}, Verse {self.current_verse}."
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

        Scene 1:
            No Shloka text.

        Scenes 2-4:
            Shloka text enabled.

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

            # ==================================================
            # SHLOKA DISPLAY RULE
            # ==================================================
            #
            # Scene 1 -> NO SHLOKA
            # Scene 2 -> SHLOKA
            # Scene 3 -> SHLOKA
            # Scene 4 -> SHLOKA
            #
            # ==================================================

            show_shloka = (
                index == 2
            )

            Logger.info(
                f"Scene {index} Shloka : "
                f"{'ON' if show_shloka else 'OFF'}"
            )

            composed_image = (
                self.scene_composer.compose(
                    image_file=source_image,
                    output_file=output_file,
                    shloka=shloka,
                    chapter=chapter,
                    verse=verse,
                    scene_number=index,
                    show_shloka=show_shloka,
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

            "chapter": self.current_chapter,

            "verse": self.current_verse,

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
        verse_folder = Path(verse_folder)

        data = {
            "chapter": self.current_chapter,
            "verse": self.current_verse,
            "scenes": [],
            "final_video": str(final_video) if final_video is not None else None,
        }

        # Scene 0: opening
        opening_folder = self._scene_output_folder(verse_folder, 0)
        opening_json = opening_folder / "scene.json"
        if opening_json.is_file():
            opening = json.loads(opening_json.read_text(encoding="utf-8-sig"))
            data["scenes"].append({
                "scene": 0,
                "narration": opening.get("narration"),
                "source_image": str(Path("assets/images/Scene0-Opening.png")),
                "composed_image": opening.get("composed_image_file"),
                "audio": opening.get("audio_file"),
                "subtitle": opening.get("subtitle_file"),
                "video": str(opening_folder / "scene_video.mp4"),
            })

        # Existing Scenes 1-4: preserve their established metadata.
        for index in range(4):
            data["scenes"].append({
                "scene": index + 1,
                "narration": scenes[index],
                "source_image": str(source_image_files[index]),
                "composed_image": str(composed_image_files[index]),
                "audio": str(audio_files[index]),
                "subtitle": str(subtitle_files[index]),
                "video": str(scene_videos[index]),
            })

        # Scene 5: CTA outro
        cta_folder = self._scene_output_folder(verse_folder, 5)
        cta_json = cta_folder / "scene.json"
        if cta_json.is_file():
            cta = json.loads(cta_json.read_text(encoding="utf-8-sig"))
            data["scenes"].append({
                "scene": 5,
                "narration": cta.get("narration"),
                "source_image": str(Path("assets/images/Scene5-likeIncentive.png")),
                "composed_image": cta.get("composed_image_file"),
                "audio": cta.get("audio_file"),
                "subtitle": cta.get("subtitle_file"),
                "video": str(cta_folder / "scene_video.mp4"),
            })

        self._save_json(
            verse_folder / "pipeline_output.json",
            data,
        )

    # ==========================================================
    # CHECK FILE
    # ==========================================================

    def _check_file(
        self,
        file_path,
        description="File",
    ):
        """
        Validate that a required file exists and is not empty.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"{description} was not found:\n"
                f"{file_path}"
            )

        if not file_path.is_file():
            raise Exception(
                f"{description} is not a file:\n"
                f"{file_path}"
            )

        if file_path.stat().st_size <= 0:
            raise Exception(
                f"{description} is empty (0 bytes):\n"
                f"{file_path}"
            )

        return file_path



    # ==========================================================
    # CREATE SCENE 5 CTA OUTRO
    # ==========================================================

    def _create_cta_scene(
        self,
        verse_folder,
        background_image,
        audio_file,
    ):
        """
        Create Scene 5 CTA outro.

        This is intentionally independent from Scenes 1-4.
        It does not modify any existing scene rendering logic.
        """

        scene_folder = self._scene_output_folder(
            verse_folder,
            5,
        )

        scene_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            scene_folder
            / "scene_video.mp4"
        )

        # ------------------------------------------------------
        # CTA text
        # ------------------------------------------------------

        cta_text = (
            "Please write\n"
            "Jai Shree Krishna\n"
            "in the comments section."
        )

        # ------------------------------------------------------
        # Escape text for FFmpeg drawtext
        # ------------------------------------------------------

        escaped_text = (
            cta_text
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace(",", "\\,")
        )

        # ------------------------------------------------------
        # Use the existing Scene 4 composed image as the
        # CTA background.
        #
        # IMPORTANT:
        # This does NOT modify the source image.
        # ------------------------------------------------------

        command = [
            self.video.ffmpeg,

            "-hide_banner",
            "-loglevel",
            "error",
            "-y",

            "-loop",
            "1",

            "-i",
            str(background_image),

            "-i",
            str(audio_file),

            "-filter_complex",

            (
                "[0:v]"
                "scale=1080:1920,"
                "zoompan="
                "z='min(zoom+0.0005,1.12)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1:s=1080x1920:fps=24,"
                "setsar=1,"
                "format=yuv420p,"
                "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
                "text='Please write':"
                "fontcolor=white:fontsize=44:"
                "x=(w-text_w)/2:y=1584,"
                "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
                "text='Jai Shree Krishna':"
                "fontcolor=white:fontsize=44:"
                "x=(w-text_w)/2:y=1664,"
                "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
                "text='in the comments section.':"
                "fontcolor=white:fontsize=44:"
                "x=(w-text_w)/2:y=1744"
                "[v]"
            ),

            "-map",
            "[v]",

            "-map",
            "1:a",

            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "18",

            "-pix_fmt",
            "yuv420p",

            "-r",
            "24",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-ar",
            "48000",

            "-shortest",

            str(output_file),
        ]

        Logger.info(
            "Creating Scene 5 CTA outro..."
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Scene 5 CTA rendering failed:\n"
                f"{result.stderr}"
            )

        if not output_file.exists():

            raise FileNotFoundError(
                "Scene 5 CTA video was not created:\n"
                f"{output_file}"
            )

        if output_file.stat().st_size <= 0:

            raise Exception(
                "Scene 5 CTA video is empty:\n"
                f"{output_file}"
            )

        self._save_json(
            scene_folder / "scene.json",
            {
                "chapter": self.current_chapter,
                "verse": self.current_verse,
                "scene": 5,
                "narration": (
                    "Please write Jai Shree Krishna "
                    "in the comments section. "
                    "If this helped you, please like, comment and subscribe."
                ),
                "source_image_file": str(background_image),
                "composed_image_file": str(background_image),
                "audio_file": str(audio_file),
                "subtitle_file": None,
                "video_file": str(output_file),
            },
        )

        Logger.success(
            f"Scene 5 CTA video : "
            f"{output_file}"
        )

        return output_file



    # ==========================================================
    # CREATE SCENE 0 OPENING
    # ==========================================================

    def _create_opening_scene(
        self,
        verse_folder,
        background_image,
        audio_file,
    ):
        """Render an animated welcome scene independently."""

        scene_folder = self._scene_output_folder(
            verse_folder,
            0,
        )

        background_image = Path(background_image)
        audio_file = Path(audio_file)

        if not background_image.is_file():
            raise FileNotFoundError(
                f"Scene 0 image not found: {background_image}"
            )

        if not audio_file.is_file() or audio_file.stat().st_size == 0:
            raise FileNotFoundError(
                f"Scene 0 narration missing or empty: {audio_file}"
            )

        output_file = scene_folder / "scene_video.mp4"

        command = [
            self.video.ffmpeg,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-loop", "1",
            "-i", str(background_image),
            "-i", str(audio_file),
            "-filter_complex",
            (
                "[0:v]"
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "zoompan="
                "z='min(zoom+0.0005,1.12)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1:s=1080x1920:fps=24,"
                "setsar=1,"
                "format=yuv420p[v]"
            ),
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-shortest",
            str(output_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Scene 0 rendering failed:\n" + result.stderr
            )

        if not output_file.is_file() or output_file.stat().st_size == 0:
            raise RuntimeError(
                f"Scene 0 video was not created: {output_file}"
            )

        self._save_json(
            scene_folder / "scene.json",
            {
                "chapter": self.current_chapter,
                "verse": self.current_verse,
                "scene": 0,
                "narration": (
                    "Welcome to the Bhagavad Gita. "
                    "Discover timeless wisdom, one verse at a time."
                ),
                "source_image_file": str(background_image),
                "composed_image_file": str(background_image),
                "audio_file": str(audio_file),
                "subtitle_file": None,
                "video_file": str(output_file),
            },
        )

        Logger.success(f"Scene 0 video: {output_file}")
        return output_file


    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    def run(self, chapter=1, verse=1):
        if chapter != 1 or not 1 <= verse <= 47:
            raise ValueError("This batch supports Chapter 1, Verses 1-47 only.")
        self.current_chapter = chapter
        self.current_verse = verse


        Logger.section(
            "Shree Bhagavad Gita AI Video Generator (V3)"
        )

        # ======================================================
        # 1. LOAD CHAPTER 1 VERSE 1
        # ======================================================

        verse_data = self._run_step(
            f"Loading Chapter {chapter}, Verse {verse}...",
            self._get_verse,
            chapter,
            verse,
        )

        # ======================================================
        # 2. PREPARE VERSE OUTPUT
        # ======================================================

        verse_folder = self._run_step(
            "Preparing output folder...",
            self._verse_output_folder,
            chapter,
            verse,
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
                f"Sanskrit shloka is empty for Chapter {chapter}, Verse {verse}."
            )

        composed_image_files = (
            self._run_step(
                "Composing Scene 1â€“4 images...",
                self._compose_scene_images,
                verse_folder,
                source_image_files,
                str(shloka).strip(),
                chapter,
                verse,
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
        # 8. RENDER ALL 4 SCENE VIDEOS
        #
        # PIPELINE:
        #
        # animated_sceneN.mp4
        #        +
        # narration.mp3
        #        â†“
        # Wav2Lip
        #        â†“
        # lipsync_sceneN.mp4
        #        +
        # existing subtitle system
        #        â†“
        # scene_video.mp4
        #
        # Scene 2 additionally receives the existing
        # Shloka highlight overlay.
        # ======================================================

        scene_videos = []

        for index in range(1, 5):

            print()
            print("=" * 80)
            print(f"RENDERING SCENE {index} / 4")
            print("=" * 80)

            scene_folder = self._scene_output_folder(
                verse_folder,
                index,
            )

            # --------------------------------------------------
            # Input files
            # --------------------------------------------------

            audio_file = Path(
                audio_files[index - 1]
            )

            narration_json = (
                scene_folder
                / "narration.json"
            )

            animated_video = (
                Path.cwd()
                / "assets"
                / "animations"
                / f"animated_scene{index}.mp4"
            )

            lipsync_video = (
                scene_folder
                / f"lipsync_scene{index}.mp4"
            )

            scene_video = (
                scene_folder
                / "scene_video.mp4"
            )

            # --------------------------------------------------
            # Validate
            # --------------------------------------------------

            if not audio_file.exists():

                raise FileNotFoundError(
                    f"Scene {index} narration not found:\n"
                    f"{audio_file}"
                )

            if not narration_json.exists():

                raise FileNotFoundError(
                    f"Scene {index} narration JSON not found:\n"
                    f"{narration_json}"
                )

            if not animated_video.exists():

                raise FileNotFoundError(
                    f"Scene {index} animated video not found:\n"
                    f"{animated_video}\n\n"
                    f"Expected the 15-second Fal animation "
                    f"to exist before Wav2Lip."
                )

                        # ==================================================
            # 8A. WAV2LIP
            # ==================================================

            Logger.info(
                f"Running Wav2Lip for Scene {index}..."
            )

            wav2lip_dir = (
                Path.cwd()
                / "Wav2Lip"
            )

            # --------------------------------------------------
            # Scene 4 SPECIAL CASE
            #
            # Scene 4 contains two faces.
            # RetinaFace consistently selects Arjuna instead
            # of Krishna.
            #
            # We therefore:
            #   1. Crop Krishna from the source animation.
            #   2. Run Wav2Lip on Krishna only.
            #   3. Overlay the lip-synced Krishna face back onto
            #      the original Scene 4 animation.
            #
            # DO NOT change the frozen scene renderer.
            # --------------------------------------------------

            if index == 4:

                krishna_source = (
                    scene_folder
                    / "krishna_only.mp4"
                )

                krishna_lipsync = (
                    scene_folder
                    / "krishna_only_lipsync.mp4"
                )

                # ----------------------------------------------
                # Step 1: Extract Krishna face
                #
                # Source animation is 720x1280.
                # Krishna face region:
                #   x = 310
                #   y = 410
                #   width  = 105
                #   height = 125
                # ----------------------------------------------

                crop_command = [
                    str(
                        Path.cwd()
                        / "tools"
                        / "ffmpeg"
                        / "bin"
                        / "ffmpeg.exe"
                    ),

                    "-y",

                    "-i",
                    str(animated_video.resolve()),

                    "-vf",
                    "crop=105:125:310:410,scale=420:500",

                    "-an",

                    str(krishna_source.resolve()),
                ]

                self._run_step(
                    "Extracting Krishna face for Scene 4...",
                    subprocess.run,
                    crop_command,
                    check=True,
                )

                # ----------------------------------------------
                # Step 2: Wav2Lip on Krishna ONLY
                # ----------------------------------------------

                wav2lip_command = [
                    r"C:\ProgramData\miniconda3\envs\wav2lip_cpu\python.exe",

                    "inference.py",

                    "--checkpoint_path",
                    str(
                        Path("checkpoints")
                        / "wav2lip_gan.pth"
                    ),

                    "--face",
                    str(
                        krishna_source.resolve()
                    ),

                    "--audio",
                    str(
                        audio_file.resolve()
                    ),

                    "--outfile",
                    str(
                        krishna_lipsync.resolve()
                    ),

                    "--resize_factor",
                    "1",

                    "--out_height",
                    "500",

                    "--pads",
                    "0",
                    "0",
                    "0",
                    "0",
                ]

                self._run_step(
                    "Wav2Lip Krishna Scene 4...",
                    subprocess.run,
                    wav2lip_command,
                    cwd=str(wav2lip_dir),
                    check=True,
                )

                # ----------------------------------------------
                # Step 3: Put the lip-synced Krishna face back
                # onto the original Scene 4 animation.
                #
                # This preserves:
                #   - Krishna's original appearance
                #   - Arjuna completely untouched
                #   - original Scene 4 composition
                # ----------------------------------------------

                replace_command = [
                    str(
                        Path.cwd()
                        / "tools"
                        / "ffmpeg"
                        / "bin"
                        / "ffmpeg.exe"
                    ),

                    "-y",

                    "-i",
                    str(animated_video.resolve()),

                    "-i",
                    str(krishna_lipsync.resolve()),

                    "-filter_complex",
                    (
                        "[1:v]"
                        "scale=105:125"
                        "[krishna];"
                        "[0:v][krishna]"
                        "overlay=310:410:shortest=1"
                        "[outv]"
                    ),

                    "-map",
                    "[outv]",

                    "-map",
                    "1:a?",

                    "-c:v",
                    "libx264",

                    "-preset",
                    "medium",

                    "-crf",
                    "18",

                    "-r",
                    "24",

                    "-pix_fmt",
                    "yuv420p",

                    "-c:a",
                    "aac",

                    "-shortest",

                    str(lipsync_video.resolve()),
                ]

                self._run_step(
                    "Rebuilding Scene 4 with Krishna lip-sync...",
                    subprocess.run,
                    replace_command,
                    check=True,
                )

            # --------------------------------------------------
            # Scene 3: Arjuna is listening; no lip-sync.
            # --------------------------------------------------

            elif index == 3:

                lipsync_video = animated_video

                Logger.info(
                    "Scene 3: Skipping Arjuna lip-sync; "
                    "using the original animated scene."
                )

            # --------------------------------------------------
            # Scenes 1 and 2 use the existing Wav2Lip path.
            # Scene 4 retains its dedicated Krishna lip-sync.
            # --------------------------------------------------

            else:

                wav2lip_command  = [
                    r"C:\ProgramData\miniconda3\envs\wav2lip_cpu\python.exe",

                    "inference.py",

                    "--checkpoint_path",
                    str(
                        Path("checkpoints")
                        / "wav2lip_gan.pth"
                    ),

                    "--face",
                    str(
                        animated_video.resolve()
                    ),

                    "--audio",
                    str(
                        audio_file.resolve()
                    ),

                    "--outfile",
                    str(
                        lipsync_video.resolve()
                    ),

                    "--resize_factor",
                    "2",

                    "--out_height",
                    "1920",

                    "--pads",
                    "0",
                    "10",
                    "0",
                    "0",
                ]

                self._run_step(
                    f"Wav2Lip Scene {index}...",
                    subprocess.run,
                    wav2lip_command,
                    cwd=str(wav2lip_dir),
                    check=True,
                )

            # --------------------------------------------------
            # Validate Wav2Lip output
            # --------------------------------------------------

            if not lipsync_video.exists():

                raise FileNotFoundError(
                    f"Wav2Lip did not create Scene {index} output:\n"
                    f"{lipsync_video}"
                )

            if lipsync_video.stat().st_size <= 0:

                raise RuntimeError(
                    f"Wav2Lip output is empty:\n"
                    f"{lipsync_video}"
                )

            Logger.success(
                f"Wav2Lip Scene {index} : "
                f"{lipsync_video}"
            )

            # ==================================================
            # 8B. SCENE 2 SHLOKA OVERLAY
            # ==================================================

            shloka_overlay = None

            if index == 2:

                shloka_overlay = (
                    scene_folder
                    / "shloka_overlay.mov"
                )

                # --------------------------------------------------
                # Generate automatically if missing.
                # --------------------------------------------------

                if not shloka_overlay.exists():

                    Logger.info(
                        "Generating Scene 2 Shloka overlay..."
                    )

                    create_shloka_overlay_from_narration(
                        shloka=shloka,
                        narration_json=str(narration_json),
                        output_path=str(shloka_overlay),
                        width=1080,
                        height=1920,
                        fps=30,
                    )

                # --------------------------------------------------
                # Validate overlay
                # --------------------------------------------------

                if not shloka_overlay.exists():

                    raise FileNotFoundError(
                        f"Scene 2 Shloka overlay was not created:\n"
                        f"{shloka_overlay}"
                    )

                if shloka_overlay.stat().st_size <= 0:

                    raise RuntimeError(
                        f"Scene 2 Shloka overlay is empty:\n"
                        f"{shloka_overlay}"
                    )

                Logger.success(
                    f"Scene 2 Shloka overlay : "
                    f"{shloka_overlay}"
                )
            # 8C. ADD EXISTING SUBTITLE SYSTEM
            # ==================================================

            scene_video = self._run_step(
                f"Rendering Scene {index} subtitles...",
                self.video.render_lipsync_scene,

                str(
                    lipsync_video
                ),

                str(
                    audio_file
                ),

                str(
                    narration_json
                ),

                str(
                    scene_video
                ),

                index,

                (
                    str(shloka_overlay)
                    if shloka_overlay
                    else None
                ),
            )

            scene_video = Path(
                scene_video
            )

            # --------------------------------------------------
            # Validate final scene video
            # --------------------------------------------------

            if not scene_video.exists():

                raise FileNotFoundError(
                    f"Scene {index} video was not created:\n"
                    f"{scene_video}"
                )

            if scene_video.stat().st_size <= 0:

                raise RuntimeError(
                    f"Scene {index} video is empty:\n"
                    f"{scene_video}"
                )

            Logger.success(
                f"Scene {index} video : "
                f"{scene_video}"
            )

            scene_videos.append(
                scene_video
            )
        
        # ======================================================
        # 8.5. CREATE SCENE 0 OPENING
        # ======================================================

        opening_narration = (
            "Welcome to the Bhagavad Gita. "
            "Discover timeless wisdom, one verse at a time."
        )

        opening_scene_folder = self._scene_output_folder(
            verse_folder,
            0,
        )

        opening_audio_file = self._run_step(
            "Generating Scene 0 welcome narration...",
            self.tts.generate_scene,
            0,
            opening_narration,
            opening_scene_folder,
        )

        opening_video = self._create_opening_scene(
            verse_folder=verse_folder,
            background_image=Path("assets/images/Scene0-Opening.png"),
            audio_file=opening_audio_file,
        )

        # ======================================================
        # 9. PRINT SCENE DURATIONS
        # ======================================================

        self.video.print_scene_durations(
            audio_files
        )


                # ======================================================
        # 9.5. CREATE SCENE 5 CTA OUTRO
        # ======================================================

        cta_narration = (
            "Please write Jai Shree Krishna "
            "in the comments section. "
            "If this helped you, please like, comment and subscribe."
        )

        cta_scene_folder = (
            self._scene_output_folder(
                verse_folder,
                5,
            )
        )

        cta_audio_file = self._run_step(
            "Generating Scene 5 CTA narration...",
            self.tts.generate_scene,
            5,
            cta_narration,
            cta_scene_folder,
        )

        cta_audio_file = Path(
            cta_audio_file
        )

        if not cta_audio_file.exists():

            raise FileNotFoundError(
                "Scene 5 CTA audio was not created:\n"
                f"{cta_audio_file}"
            )

        # Use the dedicated Scene 5 CTA image.
        # Scenes 1-4 remain unchanged.
        cta_background = Path(
            "assets/images/Scene5-likeIncentive.png"
        )

        if not cta_background.is_file():
            raise FileNotFoundError(
                f"Scene 5 CTA image not found: {cta_background}"
            )

        cta_video = self._create_cta_scene(
            verse_folder=verse_folder,
            background_image=cta_background,
            audio_file=cta_audio_file,
        )

        scene_videos.append(
            cta_video
        )

        Logger.success(
            f"Scene 5 video : "
            f"{cta_video}"
        )


        # ======================================================
        # 10. MERGE ALL 5 SCENE VIDEOS
        #
        # Background music is added ONLY inside
        # merge_scenes().
        # ======================================================

        video_file = self._run_step(
            "Merging scene videos...",
            self.video.merge_scenes,
            [opening_video, *scene_videos],
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

        Logger.success(
            f"Final video : "
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
                f"Scene {index} Shloka overlay : "
                f"{self._scene_output_folder(verse_folder, index) / 'shloka_overlay.mov'}"
            )

        Logger.success(
            f"Final video : {video_file}"
        )

        return True



