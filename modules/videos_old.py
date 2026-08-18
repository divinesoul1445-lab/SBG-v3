"""
Video Renderer (V3)

Scene-based video rendering.

For each scene:

    composed image
        +
    scene narration
        +
    scene subtitles
        ↓
    scene_video.mp4

Final render:

    scene1/scene_video.mp4
    scene2/scene_video.mp4
    scene3/scene_video.mp4
    scene4/scene_video.mp4
        +
    background music
        ↓
    final/final_video.mp4

IMPORTANT:

This module does NOT generate or compose images.

The Pipeline / SceneComposer is responsible for creating:

    sceneX/composed_image.png

VideoRenderer consumes those composed images.

No legacy output/audio/
output/images/
output/subtitles/
output/videos/
output/thumbnails/
directories are used.
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

TRANSITION_DURATION = 0.25

from modules.logger import Logger


class VideoRenderer:

    # ==========================================================
    # SBG SUBTITLE STYLE
    # ==========================================================

    SUBTITLE_FONT = "Noto Sans Devanagari"

    SUBTITLE_FONT_SIZE = 54

    SUBTITLE_BOLD = True

    # ASS uses BGR / hexadecimal formatting.
    SUBTITLE_PRIMARY_COLOUR = "&H00E6F3FF"

    SUBTITLE_OUTLINE_COLOUR = "&H00120A05"

    SUBTITLE_SHADOW_COLOUR = "&H90000000"

    SUBTITLE_OUTLINE = 3

    SUBTITLE_SHADOW = 3

    # 2 = centered
    SUBTITLE_ALIGNMENT = 2

    # Lower-middle subtitle position.
    SUBTITLE_MARGIN_V = 330

    SUBTITLE_MARGIN_L = 100
    SUBTITLE_MARGIN_R = 100

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):

        self.ffmpeg = str(
            FFMPEG_PATH
        )

        self.ffprobe = str(
            FFPROBE_PATH
        )

    # ==========================================================
    # Supress useless STDOUT
    # ==========================================================


    def _run_ffmpeg(
        self,
        command,
        description="FFmpeg",
    ):
        """
        Run FFmpeg quietly.

        Shows only:
            - SBG application logs
            - FFmpeg errors if the command fails

        Suppresses:
            - frame=
            - fps=
            - bitrate=
            - speed=
            - Qavg=
            - libx264 encoding logs
            - progress output
        """

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        except Exception as exc:
            raise RuntimeError(
                f"{description} could not be started:\n{exc}"
            ) from exc

        if result.returncode != 0:

            print()
            print("=" * 70)
            print(f"FFMPEG ERROR — {description}")
            print("=" * 70)

            if result.stderr:
                print(result.stderr.strip())

            print("=" * 70)
            print()

            raise subprocess.CalledProcessError(
                result.returncode,
                command,
                stderr=result.stderr,
            )

        return result


    # ==========================================================
    # AUDIO DURATION
    # ==========================================================

    def _audio_duration(
        self,
        audio_file: Path,
    ) -> float:

        audio_file = Path(
            audio_file
        )

        command = [

            self.ffprobe,

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default="
            "noprint_wrappers=1:"
            "nokey=1",

            str(audio_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        value = (
            result.stdout
            .strip()
        )

        if not value:

            raise Exception(
                f"Could not determine audio duration:\n"
                f"{audio_file}"
            )

        duration = float(
            value
        )

        if duration <= 0:

            raise Exception(
                f"Audio has zero duration:\n"
                f"{audio_file}"
            )

        return duration

    # ==========================================================
    # VIDEO DURATION
    # ==========================================================

    def _video_duration(
        self,
        video_file: Path,
    ) -> float:
        """
        Return the exact duration of a video file in seconds.
        """

        video_file = Path(
            video_file
        )

        video_file = self._check_file(
            video_file,
            "Video file",
        )

        command = [

            self.ffprobe,

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default="
            "noprint_wrappers=1:"
            "nokey=1",

            str(video_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        value = (
            result.stdout
            .strip()
        )

        if not value:

            raise Exception(
                f"Could not determine video duration:\n"
                f"{video_file}"
            )

        duration = float(
            value
        )

        if duration <= 0:

            raise Exception(
                f"Video has zero duration:\n"
                f"{video_file}"
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

        file_path = Path(
            file_path
        )

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
    # ESCAPE FILTER PATH
    # ==========================================================

    def _escape_filter_path(
        self,
        file_path,
    ):

        path = str(
            Path(
                file_path
            ).resolve()
        )

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
    # PRINT FFMPEG COMMAND
    # ==========================================================

    def _print_command(
        self,
        command,
    ):

        print()
        print("=" * 80)
        print("FFMPEG COMMAND")
        print("=" * 80)

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

        print("=" * 80)
        print()

    # ==========================================================
    # CREATE ASS SUBTITLE FILE
    # ==========================================================

    def _create_ass_subtitles(
        self,
        subtitle_file,
        ass_file,
    ):
        """
        Convert SRT into ASS.

        ASS provides control over:

        - font
        - size
        - bold
        - outline
        - shadow
        - position
        - margins
        """

        subtitle_file = Path(
            subtitle_file
        )

        ass_file = Path(
            ass_file
        )

        ass_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ------------------------------------------------------
        # Read SRT
        # ------------------------------------------------------

        with open(
            subtitle_file,
            "r",
            encoding="utf-8-sig",
        ) as f:

            content = f.read()

        blocks = (
            content
            .strip()
            .split("\n\n")
        )

        # ------------------------------------------------------
        # ASS header
        # ------------------------------------------------------

        lines = [

            "[Script Info]",

            "ScriptType: v4.00+",

            "PlayResX: 1080",

            "PlayResY: 1920",

            "ScaledBorderAndShadow: yes",

            "",

            "[V4+ Styles]",

            (
                "Format: "
                "Name,"
                "Fontname,"
                "Fontsize,"
                "PrimaryColour,"
                "SecondaryColour,"
                "OutlineColour,"
                "BackColour,"
                "Bold,"
                "Italic,"
                "Underline,"
                "StrikeOut,"
                "ScaleX,"
                "ScaleY,"
                "Spacing,"
                "Angle,"
                "BorderStyle,"
                "Outline,"
                "Shadow,"
                "Alignment,"
                "MarginL,"
                "MarginR,"
                "MarginV,"
                "Encoding"
            ),

            (
                "Style: Default,"
                f"{self.SUBTITLE_FONT},"
                f"{self.SUBTITLE_FONT_SIZE},"
                f"{self.SUBTITLE_PRIMARY_COLOUR},"
                "&H00000000,"
                f"{self.SUBTITLE_OUTLINE_COLOUR},"
                f"{self.SUBTITLE_SHADOW_COLOUR},"
                f"{-1 if self.SUBTITLE_BOLD else 0},"
                "0,"
                "0,"
                "0,"
                "100,"
                "100,"
                "0,"
                "0,"
                "1,"
                f"{self.SUBTITLE_OUTLINE},"
                f"{self.SUBTITLE_SHADOW},"
                f"{self.SUBTITLE_ALIGNMENT},"
                f"{self.SUBTITLE_MARGIN_L},"
                f"{self.SUBTITLE_MARGIN_R},"
                f"{self.SUBTITLE_MARGIN_V},"
                "1"
            ),

            (
                "Style: SBG,"
                f"{self.SUBTITLE_FONT},"
                f"{self.SUBTITLE_FONT_SIZE},"
                f"{self.SUBTITLE_PRIMARY_COLOUR},"
                "&H00000000,"
                f"{self.SUBTITLE_OUTLINE_COLOUR},"
                "&H900B0703,"
                f"{-1 if self.SUBTITLE_BOLD else 0},"
                "0,"
                "0,"
                "0,"
                "100,"
                "100,"
                "1,"
                "0,"
                "1,"
                "3,"
                "3,"
                "2,"
                "100,"
                "100,"
                "330,"
                "1"
            ),

            "",

            "[Events]",

            (
                "Format: "
                "Layer,"
                "Start,"
                "End,"
                "Style,"
                "Name,"
                "MarginL,"
                "MarginR,"
                "MarginV,"
                "Effect,"
                "Text"
            ),
        ]

        # ------------------------------------------------------
        # Parse SRT
        # ------------------------------------------------------

        for block in blocks:

            block_lines = (
                block.splitlines()
            )

            if len(block_lines) < 3:

                continue

            timing_line = (
                block_lines[1]
            )

            if "-->" not in timing_line:

                continue

            start_text, end_text = (
                timing_line.split(
                    "-->",
                    1,
                )
            )

            start = (
                self._srt_to_ass_time(
                    start_text.strip()
                )
            )

            end = (
                self._srt_to_ass_time(
                    end_text.strip()
                )
            )

            text_lines = (
                block_lines[2:]
            )

            text = (
                r"\N".join(
                    line.strip()
                    for line in text_lines
                    if line.strip()
                )
            )

            if not text:

                continue

            # ASS special characters
            text = text.replace(
                "{",
                r"\{",
            )

            text = text.replace(
                "}",
                r"\}",
            )

            lines.append(
                "Dialogue: "
                f"0,"
                f"{start},"
                f"{end},"
                f"SBG,"
                f","
                f"0,"
                f"0,"
                f"0,"
                f","
                f"{text}"
            )

        # ------------------------------------------------------
        # Write ASS
        # ------------------------------------------------------

        with open(
            ass_file,
            "w",
            encoding="utf-8-sig",
            newline="\n",
        ) as f:

            f.write(
                "\n".join(
                    lines
                )
            )

        return ass_file

    # ==========================================================
    # SRT → ASS TIME
    # ==========================================================

    def _srt_to_ass_time(
        self,
        value,
    ):

        value = value.strip()

        parts = value.split(
            ":"
        )

        if len(parts) != 3:

            raise ValueError(
                f"Invalid SRT timestamp: {value}"
            )

        hours = int(
            parts[0]
        )

        minutes = int(
            parts[1]
        )

        seconds_part = parts[2]

        if "," in seconds_part:

            seconds, milliseconds = (
                seconds_part.split(
                    ",",
                    1,
                )
            )

        else:

            seconds = seconds_part
            milliseconds = "0"

        seconds = int(
            seconds
        )

        milliseconds = int(
            milliseconds.ljust(
                3,
                "0",
            )[:3]
        )

        centiseconds = int(
            round(
                milliseconds / 10
            )
        )

        if centiseconds >= 100:

            centiseconds = 0
            seconds += 1

        if seconds >= 60:

            seconds = 0
            minutes += 1

        if minutes >= 60:

            minutes = 0
            hours += 1

        return (
            f"{hours}:"
            f"{minutes:02d}:"
            f"{seconds:02d}."
            f"{centiseconds:02d}"
        )

    # ==========================================================
    # RENDER ONE SCENE
    # ==========================================================

    def render_scene(
        self,
        image_file,
        audio_file,
        subtitle_file,
        output_file,
    ):
        """
        Render one independent scene.

        composed_image.png
            +
        narration.mp3
            +
        clean Sanskrit subtitles.srt
            ↓
        scene_video.mp4

        IMPORTANT:

        Subtitle rendering intentionally uses FFmpeg drawtext
        instead of ASS/libass.

        The SRT is treated as the authoritative subtitle source.
        This avoids Devanagari shaping/font problems encountered
        with ASS rendering.
        """

        image_file = self._check_file(
            image_file,
            "Scene image",
        )

        audio_file = self._check_file(
            audio_file,
            "Scene narration",
        )

        subtitle_file = self._check_file(
            subtitle_file,
            "Scene subtitles",
        )

        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ======================================================
        # EXACT NARRATION DURATION
        # ======================================================

        duration = self._audio_duration(
            audio_file
        )

        Logger.info(
            f"Scene duration : "
            f"{duration:.2f}s"
        )

        # ======================================================
        # READ CLEAN SRT
        # ======================================================

        with open(
            subtitle_file,
            "r",
            encoding="utf-8-sig",
        ) as f:

            srt_content = f.read()

        # ------------------------------------------------------
        # Parse SRT
        # ------------------------------------------------------

        subtitle_entries = []

        blocks = (
            srt_content
            .strip()
            .split("\n\n")
        )

        for block in blocks:

            lines = block.splitlines()

            if len(lines) < 3:
                continue

            timing_line = lines[1].strip()

            if "-->" not in timing_line:
                continue

            start_text, end_text = (
                timing_line.split(
                    "-->",
                    1,
                )
            )

            start_text = start_text.strip()
            end_text = end_text.strip()

            def _srt_time_to_seconds(value):

                value = value.strip()

                hms, milliseconds = value.split(
                    ",",
                    1,
                )

                hours, minutes, seconds = (
                    hms.split(":")
                )

                return (
                    int(hours) * 3600
                    + int(minutes) * 60
                    + int(seconds)
                    + int(milliseconds) / 1000.0
                )

            try:

                start = _srt_time_to_seconds(
                    start_text
                )

                end = _srt_time_to_seconds(
                    end_text
                )

            except Exception:

                continue

            text_lines = lines[2:]

            text = "\n".join(
                line.strip()
                for line in text_lines
                if line.strip()
            )

            if not text:
                continue

            if end <= start:
                continue

            subtitle_entries.append(
                {
                    "start": start,
                    "end": end,
                    "text": text,
                }
            )

        if not subtitle_entries:

            raise Exception(
                "No valid subtitle entries found:\n"
                f"{subtitle_file}"
            )

        Logger.info(
            f"Subtitle entries : "
            f"{len(subtitle_entries)}"
        )

        # ======================================================
        # CREATE TEXT FILES FOR DRAWTEXT
        # ======================================================
        #
        # Using textfile= instead of text= is important.
        #
        # It allows UTF-8 Devanagari to pass directly to
        # FFmpeg without complicated escaping of Unicode text.
        #
        # ======================================================

        subtitle_text_folder = (
            output_file.parent
            / "_subtitle_text"
        )

        subtitle_text_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        subtitle_filters = []

        # ------------------------------------------------------
        # Font
        # ------------------------------------------------------

        font_file = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "fonts"
            / "NotoSerifDevanagari-Regular.ttf"
        )

        self._check_file(
            font_file,
            "Devanagari subtitle font",
        )

        font_path = (
            self._escape_filter_path(
                font_file
            )
        )

        # ------------------------------------------------------
        # Create one UTF-8 text file per subtitle entry
        # ------------------------------------------------------

        for index, entry in enumerate(
            subtitle_entries,
            start=1,
        ):

            text_file = (
                subtitle_text_folder
                / f"subtitle_{index:03d}.txt"
            )

            with open(
                text_file,
                "w",
                encoding="utf-8",
                newline="\n",
            ) as f:

                f.write(
                    entry["text"]
                )

            text_path = (
                self._escape_filter_path(
                    text_file
                )
            )

            start = entry["start"]
            end = entry["end"]

            # --------------------------------------------------
            # drawtext
            # --------------------------------------------------
            #
            # Lower-middle placement.
            #
            # h-420 gives approximately the same visual area
            # as the previous subtitle placement.
            #
            # --------------------------------------------------

            drawtext_filter = (

                "drawtext="

                f"fontfile='{font_path}':"

                f"textfile='{text_path}':"

                "fontsize=54:"

                "fontcolor=white:"

                "borderw=3:"

                "bordercolor=black@0.85:"

                "shadowx=2:"

                "shadowy=2:"

                "shadowcolor=black@0.75:"

                "x=(w-text_w)/2:"

                "y=h-350:"

                f"enable='between(t,{start:.3f},{end:.3f})'"
            )

            subtitle_filters.append(
                drawtext_filter
            )

        # ======================================================
        # VIDEO FILTER
        # ======================================================

        video_filter_parts = [

            (
                f"scale="
                f"{VIDEO_WIDTH}:"
                f"{VIDEO_HEIGHT}:"
                f"force_original_aspect_ratio=decrease"
            ),

            (
                f"pad="
                f"{VIDEO_WIDTH}:"
                f"{VIDEO_HEIGHT}:"
                f"(ow-iw)/2:"
                f"(oh-ih)/2"
            ),

            f"fps={FPS}",

            "format=yuv420p",

            "setsar=1",

        ]

        video_filter_parts.extend(
            subtitle_filters
        )

        video_filter = ",".join(
            video_filter_parts
        )

        # ======================================================
        # FFMPEG
        # ======================================================

        command = [

            self.ffmpeg,

            "-hide_banner",

            "-loglevel",
            "error",

            "-y",

            # --------------------------------------------------
            # Image
            # --------------------------------------------------

            "-loop",
            "1",

            "-i",
            str(image_file),

            # --------------------------------------------------
            # Narration
            # --------------------------------------------------

            "-i",
            str(audio_file),

            # --------------------------------------------------
            # Video filter
            # --------------------------------------------------

            "-vf",
            video_filter,

            # --------------------------------------------------
            # Mapping
            # --------------------------------------------------

            "-map",
            "0:v",

            "-map",
            "1:a",

            # --------------------------------------------------
            # Video
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
            # Audio
            # --------------------------------------------------

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-ar",
            "48000",

            # --------------------------------------------------
            # Exact duration
            # --------------------------------------------------

            "-t",
            f"{duration:.6f}",

            # --------------------------------------------------
            # MP4
            # --------------------------------------------------

            "-movflags",
            "+faststart",

            str(output_file),
        ]

        self._print_command(
            command
        )

        Logger.info(
            f"Rendering scene -> "
            f"{output_file}"
        )

        self._run_ffmpeg(
            command,
            description=(
                f"Rendering Scene "
                f"{Path(output_file).parent.name}"
            ),
        )

        # ======================================================
        # VERIFY
        # ======================================================

        if not output_file.exists():

            raise Exception(
                "FFmpeg completed but scene "
                "video was not created:\n"
                f"{output_file}"
            )

        if output_file.stat().st_size <= 0:

            raise Exception(
                f"Scene video is empty:\n"
                f"{output_file}"
            )

        Logger.success(
            f"Scene video saved -> "
            f"{output_file}"
        )

        return output_file

    # ==========================================================
    # MERGE SCENE VIDEOS
    # ==========================================================

        # ==========================================================
    # MERGE SCENE VIDEOS
    # ==========================================================

    def merge_scenes(
        self,
        scene_videos,
        output_folder,
        ):
        """
        Merge 4 scene videos using smooth visual crossfades.

        Visual:
            Scene 1 ──crossfade──> Scene 2 ──crossfade──> ...

        Audio:
            Scene 1 narration -> Scene 2 narration -> ...

        Background music is added only after the scene audio
        has been combined.

        This avoids the brief black frame produced by
        fade-to-black transitions.
        """

        if not scene_videos:
            raise Exception(
                "No scene videos supplied."
            )

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        final_folder = (
            output_folder
            / "final"
        )

        final_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            final_folder
            / "final_video.mp4"
        )

        # ======================================================
        # VALIDATE
        # ======================================================

        scene_videos = [
            self._check_file(
                video,
                f"Scene video {index}",
            )
            for index, video
            in enumerate(
                scene_videos,
                start=1,
            )
        ]

        if len(scene_videos) != 4:
            raise ValueError(
                "merge_scenes expects exactly "
                "4 scene videos."
            )

        # ======================================================
        # GET VIDEO DURATIONS
        # ======================================================

        def get_video_duration(
            video_file,
        ):
            command = [

                self.ffprobe,

                "-v",
                "error",

                "-show_entries",
                "format=duration",

                "-of",
                "default="
                "noprint_wrappers=1:"
                "nokey=1",

                str(video_file),
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            value = (
                result.stdout
                .strip()
            )

            if not value:
                raise Exception(
                    "Could not determine video duration:\n"
                    f"{video_file}"
                )

            duration = float(
                value
            )

            if duration <= 0:
                raise Exception(
                    "Video has zero duration:\n"
                    f"{video_file}"
                )

            return duration

        durations = [
            get_video_duration(
                video
            )
            for video in scene_videos
        ]

        # ======================================================
        # TRANSITION
        # ======================================================

        transition = float(
            TRANSITION_DURATION
        )

        if transition <= 0:
            transition = 0.01

        # Never allow transition to consume an entire scene.
        shortest_scene = min(
            durations
        )

        transition = min(
            transition,
            shortest_scene / 2.0,
        )

        Logger.info(
            "Scene transition duration: "
            f"{transition:.2f}s"
        )

        # ======================================================
        # PRINT DURATIONS
        # ======================================================

        print()
        print(
            "Scene video durations:"
        )

        for index, duration in enumerate(
            durations,
            start=1,
        ):

            print(
                f"  Scene {index}: "
                f"{duration:.3f} sec"
            )

        print()

        # ======================================================
        # BUILD INPUTS
        # ======================================================

        command = [

            self.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",

            "-y",
        ]

        for video in scene_videos:

            command.extend(
                [
                    "-i",
                    str(video),
                ]
            )

        # ======================================================
        # VIDEO CROSSFADE FILTER
        # ======================================================
        #
        # Example:
        #
        # [0:v][1:v] xfade -> [v01]
        # [v01][2:v] xfade -> [v012]
        # [v012][3:v] xfade -> [vout]
        #
        # The offset is based on the cumulative duration
        # minus the transitions already applied.
        # ======================================================

        filter_parts = []

        # First transition
        cumulative_duration = (
            durations[0]
        )

        filter_parts.append(
            (
                f"[0:v][1:v]"
                f"xfade="
                f"transition=fade:"
                f"duration={transition:.3f}:"
                f"offset={cumulative_duration - transition:.3f}"
                f"[v01]"
            )
        )

        cumulative_duration = (
            cumulative_duration
            + durations[1]
            - transition
        )

        # Second transition
        filter_parts.append(
            (
                f"[v01][2:v]"
                f"xfade="
                f"transition=fade:"
                f"duration={transition:.3f}:"
                f"offset={cumulative_duration - transition:.3f}"
                f"[v012]"
            )
        )

        cumulative_duration = (
            cumulative_duration
            + durations[2]
            - transition
        )

        # Third transition
        filter_parts.append(
            (
                f"[v012][3:v]"
                f"xfade="
                f"transition=fade:"
                f"duration={transition:.3f}:"
                f"offset={cumulative_duration - transition:.3f}"
                f"[vout]"
            )
        )

        # ======================================================
        # AUDIO CROSSFADE
        # ======================================================
        #
        # Narrations remain in scene order.
        #
        # There is a very short audio crossfade at each
        # scene boundary so the transition doesn't feel abrupt.
        #
        # This does NOT add background music yet.
        # ======================================================

        audio_transition = min(
            transition,
            0.15,
        )

        filter_parts.append(
            (
                f"[0:a][1:a]"
                f"acrossfade="
                f"d={audio_transition:.3f}:"
                f"c1=tri:"
                f"c2=tri"
                f"[a01]"
            )
        )

        filter_parts.append(
            (
                f"[a01][2:a]"
                f"acrossfade="
                f"d={audio_transition:.3f}:"
                f"c1=tri:"
                f"c2=tri"
                f"[a012]"
            )
        )

        filter_parts.append(
            (
                f"[a012][3:a]"
                f"acrossfade="
                f"d={audio_transition:.3f}:"
                f"c1=tri:"
                f"c2=tri"
                f"[aout]"
            )
        )

        filter_complex = (
            ";".join(
                filter_parts
            )
        )

        # ======================================================
        # INTERMEDIATE OUTPUT
        # ======================================================

        merged_video = (
            final_folder
            / "merged_video.mp4"
        )

        # ======================================================
        # CROSSFADE COMMAND
        # ======================================================

        merge_command = [

            *command,

            "-filter_complex",
            filter_complex,

            # Final video
            "-map",
            "[vout]",

            # Sequential narration
            "-map",
            "[aout]",

            # Video encoding
            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "18",

            "-pix_fmt",
            "yuv420p",

            # Audio
            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-ar",
            "48000",

            "-movflags",
            "+faststart",

            str(merged_video),
        ]

        self._print_command(
            merge_command
        )

        Logger.info(
            "Merging scene videos with smooth "
            "crossfade transitions..."
        )

        # subprocess.run(
        #     merge_command,
        #     check=True,
        # )

        self._run_ffmpeg(
            merge_command,
            description="Merging scene videos",
        )

        # ======================================================
        # VERIFY MERGED VIDEO
        # ======================================================

        if not merged_video.exists():

            raise Exception(
                "Merged video was not created:\n"
                f"{merged_video}"
            )

        if merged_video.stat().st_size <= 0:

            raise Exception(
                "Merged video is empty:\n"
                f"{merged_video}"
            )

        Logger.success(
            "Scene videos merged successfully."
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

            Logger.info(
                "Adding background music..."
            )

            music_volume = float(
                BACKGROUND_MUSIC_VOLUME
            )

            music_command = [

                self.ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",

                "-y",

                # Narration + video
                "-i",
                str(merged_video),

                # Loop music
                "-stream_loop",
                "-1",

                "-i",
                str(music_file),

                # --------------------------------------------------
                # Mix narration + music
                # --------------------------------------------------

                "-filter_complex",

                (
                    "[1:a]"
                    f"volume={music_volume}"
                    "[music];"

                    "[0:a][music]"
                    "amix="
                    "inputs=2:"
                    "duration=first:"
                    "dropout_transition=2"
                    "[aout]"
                ),

                # Video
                "-map",
                "0:v",

                # Mixed audio
                "-map",
                "[aout]",

                # Keep already encoded video
                "-c:v",
                "copy",

                # Encode final audio
                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-movflags",
                "+faststart",

                str(output_file),
            ]

            self._print_command(
                music_command
            )

            # subprocess.run(
            #     music_command,
            #     check=True,
            # )

            self._run_ffmpeg(
                music_command,
                description="Adding background music",
            )

        else:

            Logger.info(
                "Background music not found."
            )

            # No music.
            #
            # Move merged video to final output.
            if output_file.exists():
                output_file.unlink()

            merged_video.replace(
                output_file
            )

        # ======================================================
        # VERIFY FINAL VIDEO
        # ======================================================

        if not output_file.exists():

            raise Exception(
                "Final video was not created:\n"
                f"{output_file}"
            )

        if output_file.stat().st_size <= 0:

            raise Exception(
                "Final video is empty:\n"
                f"{output_file}"
            )

        # ======================================================
        # CLEANUP INTERMEDIATE MERGED VIDEO
        # ======================================================

        if merged_video.exists():

            try:
                merged_video.unlink()
            except OSError:
                pass

        Logger.success(
            f"Final video saved -> "
            f"{output_file}"
        )

        Logger.success(
            "Scene transitions -> "
            f"SMOOTH CROSSFADE ({transition:.2f}s)"
        )

        Logger.success(
            "Scene subtitles -> "
            "STYLED / BURNED IN"
        )

        if music_exists:

            Logger.success(
                "Background music -> ON"
            )

        else:

            Logger.info(
                "Background music -> OFF"
            )

        return output_file

    # ==========================================================
    # RENDER COMPLETE VERSE
    # ==========================================================

    def render_verse(
        self,
        scene_images,
        scene_audio_files,
        scene_subtitle_files,
        output_folder,
        scene_video_names=None,
        merge=True,
    ):
        """
        Render one complete verse.

        Required structure:

            scene1/
                composed_image.png
                narration.mp3
                subtitles.srt
                scene_video.mp4

            scene2/
                composed_image.png
                narration.mp3
                subtitles.srt
                scene_video.mp4

            scene3/
                composed_image.png
                narration.mp3
                subtitles.srt
                scene_video.mp4

            scene4/
                composed_image.png
                narration.mp3
                subtitles.srt
                scene_video.mp4

            final/
                scenes.txt
                merged_video.mp4
                final_video.mp4

        The supplied image paths are authoritative.

        Therefore the Pipeline can pass:

            output/.../scene1/composed_image.png

        directly into this method.

        VideoRenderer does NOT regenerate, compose, or replace
        those images.
        """

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ------------------------------------------------------
        # Normalize inputs
        # ------------------------------------------------------

        scene_images = [
            Path(item)
            for item in scene_images
        ]

        scene_audio_files = [
            Path(item)
            for item in scene_audio_files
        ]

        scene_subtitle_files = [
            Path(item)
            for item in scene_subtitle_files
        ]

        # ------------------------------------------------------
        # Validate count
        # ------------------------------------------------------

        if not (
            len(scene_images)
            == len(scene_audio_files)
            == len(scene_subtitle_files)
            == 4
        ):

            raise ValueError(
                "render_verse requires exactly "
                "4 scene images, 4 audio files, "
                "and 4 subtitle files."
            )

        # ------------------------------------------------------
        # Scene video names
        # ------------------------------------------------------

        if scene_video_names is None:

            scene_video_names = [

                "scene_video.mp4",

                "scene_video.mp4",

                "scene_video.mp4",

                "scene_video.mp4",
            ]

        if len(scene_video_names) != 4:

            raise ValueError(
                "scene_video_names must contain "
                "exactly 4 names."
            )

        # ------------------------------------------------------
        # Production header
        # ------------------------------------------------------

        print()
        print("=" * 80)
        print("SBG V3 — COMPLETE VERSE RENDER")
        print("=" * 80)
        print()

        print(
            f"Verse folder: {output_folder}"
        )

        print()

        scene_videos = []

        # ------------------------------------------------------
        # Render Scene 1 → Scene 4
        # ------------------------------------------------------

        for index in range(4):

            scene_number = (
                index + 1
            )

            image_file = (
                scene_images[index]
            )

            audio_file = (
                scene_audio_files[index]
            )

            subtitle_file = (
                scene_subtitle_files[index]
            )

            scene_folder = (
                output_folder
                / f"scene{scene_number}"
            )

            scene_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            # --------------------------------------------------
            # IMPORTANT:
            #
            # Always put the scene video INSIDE its scene
            # folder.
            # --------------------------------------------------

            output_file = (
                scene_folder
                / scene_video_names[index]
            )

            print()
            print("-" * 80)
            print(
                f"SCENE {scene_number} / 4"
            )
            print("-" * 80)

            print(
                f"Image:     {image_file}"
            )

            print(
                f"Audio:     {audio_file}"
            )

            print(
                f"Subtitles: {subtitle_file}"
            )

            print(
                f"Output:    {output_file}"
            )

            # --------------------------------------------------
            # Validate
            # --------------------------------------------------

            self._check_file(
                image_file,
                f"Scene {scene_number} image",
            )

            self._check_file(
                audio_file,
                f"Scene {scene_number} narration",
            )

            self._check_file(
                subtitle_file,
                f"Scene {scene_number} subtitles",
            )

            # --------------------------------------------------
            # Safety check:
            #
            # We expect the pipeline to provide the composed
            # image, not the original asset.
            # --------------------------------------------------

            image_name = (
                image_file.name.lower()
            )

            if image_name.startswith(
                "scene"
            ) and image_name.endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                )
            ):

                Logger.info(
                    "Scene image input detected."
                )

            # --------------------------------------------------
            # Render
            # --------------------------------------------------

            rendered = (
                self.render_scene(
                    image_file=image_file,
                    audio_file=audio_file,
                    subtitle_file=subtitle_file,
                    output_file=output_file,
                )
            )

            rendered = self._check_file(
                rendered,
                f"Scene {scene_number} video",
            )

            scene_videos.append(
                rendered
            )

            print(
                f"✓ Scene {scene_number} complete"
            )

        # ------------------------------------------------------
        # Duration table
        # ------------------------------------------------------

        print()
        print("=" * 80)
        print("SCENE DURATIONS")
        print("=" * 80)

        self.print_scene_durations(
            scene_audio_files
        )

        # ------------------------------------------------------
        # Merge
        # ------------------------------------------------------

        final_video = None

        if merge:

            print()
            print("=" * 80)
            print("MERGING 4 SCENES")
            print("=" * 80)
            print()

            final_video = (
                self.merge_scenes(
                    scene_videos=scene_videos,
                    output_folder=output_folder,
                )
            )

        # ------------------------------------------------------
        # Final summary
        # ------------------------------------------------------

        print()
        print("=" * 80)
        print("VERSE RENDER COMPLETE")
        print("=" * 80)
        print()

        for index, scene_video in enumerate(
            scene_videos,
            start=1,
        ):

            print(
                f"Scene {index}: "
                f"{scene_video}"
            )

        if final_video is not None:

            print()

            print(
                f"FINAL VIDEO: "
                f"{final_video}"
            )

        print()

        return {

            "scene_videos":
                scene_videos,

            "final_video":
                final_video,

            "output_folder":
                output_folder,
        }

    # ==========================================================
    # SCENE DURATION TABLE
    # ==========================================================

    def get_scene_durations(
        self,
        audio_files,
    ):

        scene_data = []

        for index, audio_file in enumerate(
            audio_files,
            start=1,
        ):

            audio_file = (
                self._check_file(
                    audio_file,
                    f"Scene {index} narration",
                )
            )

            narration_duration = (
                self._audio_duration(
                    audio_file
                )
            )

            scene_data.append(
                {
                    "scene":
                        index,

                    "narration":
                        narration_duration,

                    "image_duration":
                        narration_duration,
                }
            )

        return scene_data

    # ==========================================================
    # PRINT SCENE DURATION TABLE
    # ==========================================================

    def print_scene_durations(
        self,
        audio_files,
    ):

        scene_data = (
            self.get_scene_durations(
                audio_files
            )
        )

        print()

        print(
            f"{'Scene':<8}"
            f"{'Narration':>14}"
            f"{'Image duration':>20}"
        )

        print(
            "-" * 42
        )

        for scene in scene_data:

            print(
                f"{scene['scene']:<8}"
                f"{scene['narration']:>10.2f} sec"
                f"{scene['image_duration']:>16.2f} sec"
            )

        print()

        return scene_data