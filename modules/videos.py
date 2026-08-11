"""
Video Renderer (V3)

Creates the final Shorts video from:

- 4 fixed scene images
- 4 scene narration audio files
- SRT subtitles
- Optional background music

Scene flow:

    Scene 1 image + Scene 1 audio
        ↓
    Scene 2 image + Scene 2 audio
        ↓
    Scene 3 image + Scene 3 audio
        ↓
    Scene 4 image + Scene 4 audio
        ↓
    subtitles + music
        ↓
    final_video.mp4

The renderer does NOT generate images.
"""

from pathlib import Path
import subprocess

from config import (
    FFMPEG_PATH,
    FFPROBE_PATH,
    BACKGROUND_MUSIC,
    BACKGROUND_MUSIC_VOLUME,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
)

from modules.logger import Logger


class VideoRenderer:

    def __init__(self):

        self.ffmpeg = str(FFMPEG_PATH)
        self.ffprobe = str(FFPROBE_PATH)

    # ==========================================================
    # AUDIO DURATION
    # ==========================================================

    def _audio_duration(
        self,
        audio_file: Path,
    ) -> float:

        audio_file = Path(audio_file)

        command = [
            self.ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        value = result.stdout.strip()

        if not value:

            raise Exception(
                f"Could not determine audio duration:\n"
                f"{audio_file}"
            )

        duration = float(value)

        if duration <= 0:

            raise Exception(
                f"Audio has zero duration:\n"
                f"{audio_file}"
            )

        return duration

    # ==========================================================
    # CHECK FILE
    # ==========================================================

    def _check_file(
        self,
        file_path,
        description,
    ):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(
                f"{description} not found:\n"
                f"{file_path}"
            )

        if file_path.stat().st_size <= 0:

            raise Exception(
                f"{description} is empty:\n"
                f"{file_path}"
            )

        return file_path

    # ==========================================================
    # ESCAPE SUBTITLE PATH FOR FFMPEG
    # ==========================================================

    def _escape_filter_path(
        self,
        file_path,
    ):

        path = str(
            Path(file_path).resolve()
        )

        # FFmpeg subtitles filter expects
        # forward slashes even on Windows.

        path = path.replace(
            "\\",
            "/",
        )

        path = path.replace(
            ":",
            "\\:",
        )

        path = path.replace(
            "'",
            "\\'",
        )

        return path

    # ==========================================================
    # RENDER
    # ==========================================================

    def render(
        self,
        images,
        audio_files,
        subtitle_file,
        output_folder,
    ):

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_folder
            / "final_video.mp4"
        )

        # ======================================================
        # VALIDATE SCENES
        # ======================================================

        if not images:

            raise Exception(
                "No scene images supplied."
            )

        if not audio_files:

            raise Exception(
                "No scene audio files supplied."
            )

        if len(images) != 4:

            raise Exception(
                f"Expected exactly 4 scene images, "
                f"received {len(images)}."
            )

        if len(audio_files) != 4:

            raise Exception(
                f"Expected exactly 4 scene audio files, "
                f"received {len(audio_files)}."
            )

        # ======================================================
        # VALIDATE IMAGES
        # ======================================================

        checked_images = []

        for index, image in enumerate(
            images,
            start=1,
        ):

            checked_image = self._check_file(
                image,
                f"Scene {index} image",
            )

            checked_images.append(
                checked_image
            )

        # ======================================================
        # VALIDATE AUDIO
        # ======================================================

        checked_audio = []

        for index, audio in enumerate(
            audio_files,
            start=1,
        ):

            checked_audio_file = self._check_file(
                audio,
                f"Scene {index} narration audio",
            )

            checked_audio.append(
                checked_audio_file
            )

        # ======================================================
        # SUBTITLES
        # ======================================================

        subtitle_file = self._check_file(
            subtitle_file,
            "Subtitle file",
        )

        # ======================================================
        # BACKGROUND MUSIC
        # ======================================================

        music_file = Path(
            BACKGROUND_MUSIC
        )

        music_exists = (
            music_file.exists()
            and music_file.stat().st_size > 0
        )

        if music_exists:

            music_file = self._check_file(
                music_file,
                "Background music",
            )

        else:

            Logger.info(
                "Background music not found. "
                "Rendering without music."
            )

        # ======================================================
        # GET EACH SCENE DURATION
        # ======================================================

        scene_durations = []

        for index, audio in enumerate(
            checked_audio,
            start=1,
        ):

            duration = self._audio_duration(
                audio
            )

            scene_durations.append(
                duration
            )

            Logger.info(
                f"Scene {index} duration: "
                f"{duration:.2f}s"
            )

        # ======================================================
        # TOTAL DURATION
        # ======================================================

        total_duration = sum(
            scene_durations
        )

        if total_duration <= 0:

            raise Exception(
                "Total narration duration is zero."
            )

        Logger.info(
            f"Total narration duration: "
            f"{total_duration:.2f}s"
        )

        # ======================================================
        # INPUT INDEXES
        # ======================================================
        #
        # Inputs:
        #
        # 0 = Scene 1 image
        # 1 = Scene 2 image
        # 2 = Scene 3 image
        # 3 = Scene 4 image
        #
        # 4 = Scene 1 audio
        # 5 = Scene 2 audio
        # 6 = Scene 3 audio
        # 7 = Scene 4 audio
        #
        # 8 = music, if enabled
        #
        # ======================================================

        image_count = 4

        audio_start = image_count

        music_index = (
            audio_start + 4
            if music_exists
            else None
        )

        # ======================================================
        # FFMPEG COMMAND
        # ======================================================

        command = [
            self.ffmpeg,
            "-y",
        ]

        # ======================================================
        # IMAGE INPUTS
        # ======================================================

        for image in checked_images:

            command.extend([
                "-loop",
                "1",
                "-i",
                str(image),
            ])

        # ======================================================
        # AUDIO INPUTS
        # ======================================================

        for audio in checked_audio:

            command.extend([
                "-i",
                str(audio),
            ])

        # ======================================================
        # MUSIC INPUT
        # ======================================================

        if music_exists:

            command.extend([
                "-stream_loop",
                "-1",
                "-i",
                str(music_file),
            ])

        # ======================================================
        # FILTERS
        # ======================================================

        filters = []

        # ======================================================
        # PREPARE IMAGES
        # ======================================================

        for index, duration in enumerate(
            scene_durations
        ):

            filters.append(

                f"[{index}:v]"

                f"scale="
                f"{VIDEO_WIDTH}:"
                f"{VIDEO_HEIGHT}:"
                f"force_original_aspect_ratio=decrease,"

                f"pad="
                f"{VIDEO_WIDTH}:"
                f"{VIDEO_HEIGHT}:"
                f"(ow-iw)/2:"
                f"(oh-ih)/2,"

                f"fps={FPS},"

                f"format=yuv420p,"

                f"setsar=1,"

                f"trim="
                f"duration={duration:.6f},"

                f"setpts=PTS-STARTPTS"

                f"[v{index}]"

            )

        # ======================================================
        # IMAGE TRANSITIONS
        # ======================================================
        #
        # IMPORTANT:
        #
        # We use a small transition.
        #
        # The final video is trimmed to the exact combined
        # narration duration.
        #
        # ======================================================

        transition = 0.20

        current = "v0"

        # The first transition begins near the end of Scene 1.
        offset = max(
            0,
            scene_durations[0] - transition,
        )

        for index in range(
            1,
            4,
        ):

            output = (
                f"xf{index}"
            )

            filters.append(

                f"[{current}]"
                f"[v{index}]"

                f"xfade="
                f"transition=fade:"
                f"duration={transition}:"
                f"offset={offset:.6f}"

                f"[{output}]"

            )

            current = output

            offset += (
                scene_durations[index]
                - transition
            )

        # ======================================================
        # SUBTITLES
        # ======================================================

        subtitle_path = (
            self._escape_filter_path(
                subtitle_file
            )
        )

        filters.append(
            f"[{current}]"
            f"subtitles="
            f"'{subtitle_path}':"
            f"force_style='"
            f"FontName=Arial,"
            f"FontSize=18,"
            f"Bold=1,"
            f"PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,"
            f"BorderStyle=1,"
            f"Outline=3,"
            f"Shadow=1,"
            f"Alignment=2,"
            f"MarginV=120"
            f"'"
            f"[vfinal]"
        )

        # ======================================================
        # SCENE AUDIO
        # ======================================================
        #
        # Each scene audio is already exactly the narration
        # for its corresponding image.
        #
        # We concatenate the four audio streams.
        #
        # ======================================================

        for index in range(4):

            input_index = (
                audio_start + index
            )

            filters.append(

                f"[{input_index}:a]"

                f"aresample=48000"

                f"[a{index}]"

            )

        filters.append(

            "[a0]"
            "[a1]"
            "[a2]"
            "[a3]"

            "concat="
            "n=4:"
            "v=0:"
            "a=1"

            "[voice]"

        )

        # ======================================================
        # VOICE FADE
        # ======================================================

        voice_fade_start = max(
            0,
            total_duration - 0.70,
        )

        filters.append(

            "[voice]"

            "volume=1.0,"

            f"afade="
            f"t=out:"
            f"st={voice_fade_start:.6f}:"
            f"d=0.70"

            "[voicefinal]"

        )

        # ======================================================
        # MUSIC
        # ======================================================

        if music_exists:

            filters.append(

                f"[{music_index}:a]"

                "aresample=48000,"

                f"volume="
                f"{BACKGROUND_MUSIC_VOLUME},"

                f"atrim="
                f"duration={total_duration:.6f},"

                "asetpts=PTS-STARTPTS"

                "[music]"

            )

            # --------------------------------------------------
            # Music fade out
            # --------------------------------------------------

            music_fade_start = max(
                0,
                total_duration - 1.20,
            )

            filters.append(

                "[music]"

                f"afade="
                f"t=out:"
                f"st={music_fade_start:.6f}:"
                f"d=1.20"

                "[musicfinal]"

            )

            # --------------------------------------------------
            # Mix voice + music
            # --------------------------------------------------

            filters.append(

                "[voicefinal]"
                "[musicfinal]"

                "amix="
                "inputs=2:"
                "duration=first:"
                "dropout_transition=1:"
                "normalize=0"

                "[aout]"

            )

            audio_map = "[aout]"

        else:

            audio_map = "[voicefinal]"

        # ======================================================
        # FILTER COMPLEX
        # ======================================================

        filter_complex = ";".join(
            filters
        )

        command.extend([

            "-filter_complex",
            filter_complex,

            # --------------------------------------------------
            # VIDEO
            # --------------------------------------------------

            "-map",
            "[vfinal]",

            # --------------------------------------------------
            # AUDIO
            # --------------------------------------------------

            "-map",
            audio_map,

            # --------------------------------------------------
            # VIDEO ENCODING
            # --------------------------------------------------

            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "18",

            "-pix_fmt",
            "yuv420p",

            # --------------------------------------------------
            # AUDIO ENCODING
            # --------------------------------------------------

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-ar",
            "48000",

            # --------------------------------------------------
            # Exact final duration
            # --------------------------------------------------

            "-t",
            f"{total_duration:.6f}",

            # --------------------------------------------------
            # MP4 compatibility
            # --------------------------------------------------

            "-movflags",
            "+faststart",

            # --------------------------------------------------
            # Output
            # --------------------------------------------------

            str(output_file),

        ])

        # ======================================================
        # PRINT COMMAND
        # ======================================================

        print(
            "\n"
            + "=" * 80
        )

        print(
            "FFMPEG COMMAND"
        )

        print(
            "=" * 80
        )

        print(
            " ".join(
                (
                    f'"{item}"'
                    if " " in str(item)
                    else str(item)
                )
                for item in command
            )
        )

        print(
            "=" * 80
            + "\n"
        )

        # ======================================================
        # RENDER
        # ======================================================

        Logger.info(
            "Rendering video..."
        )

        subprocess.run(
            command,
            check=True,
        )

        # ======================================================
        # VERIFY
        # ======================================================

        if not output_file.exists():

            raise Exception(
                "FFmpeg completed but the "
                "output video was not created."
            )

        output_size = (
            output_file.stat().st_size
        )

        if output_size <= 0:

            raise Exception(
                "Output video is empty."
            )

        # ======================================================
        # FINAL LOG
        # ======================================================

        Logger.success(
            f"Saved -> {output_file}"
        )

        Logger.success(
            f"Duration -> "
            f"{total_duration:.2f}s"
        )

        if music_exists:

            Logger.success(
                "Background music -> ON"
            )

        else:

            Logger.info(
                "Background music -> OFF"
            )

        Logger.success(
            "Subtitles -> BURNED IN"
        )

        return output_file

    def get_scene_durations(
    self,
    audio_files,
    padding=0.3,
    ):
        """
        Returns actual narration duration and image duration
        for each scene.

        Image duration = narration duration + padding.
        """

        scene_data = []

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):
            audio_file = Path(audio_file)

            narration_duration = self._audio_duration(
                audio_file
            )

            image_duration = (
                narration_duration
                + padding
            )

            scene_data.append(
                {
                    "scene": index,
                    "narration": narration_duration,
                    "image_duration": image_duration,
                }
            )

        return scene_data