# modules/videos.py

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Optional


class VideoRenderer:
    """
    SBG V3 - Scene Video Renderer

    Scene 2 test version.

    Inputs:
        PNG/JPG/WEBP scene image
        Scene narration audio
        Scene subtitles
        Optional Shloka karaoke overlay

    Output:
        output/videos/scene_video.mp4

    Background music is NOT added here.
    """

    def __init__(
        self,
        ffmpeg_path: Optional[str] = None,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ):

        self.width = width
        self.height = height
        self.fps = fps

        self.ffmpeg = (
            ffmpeg_path
            if ffmpeg_path
            else self._find_ffmpeg()
        )

    # ============================================================
    # FIND FFMPEG
    # ============================================================

    @staticmethod
    def _find_ffmpeg() -> str:

        project_ffmpeg = os.path.join(
            "tools",
            "ffmpeg",
            "bin",
            "ffmpeg.exe",
        )

        if os.path.exists(project_ffmpeg):
            return project_ffmpeg

        return "ffmpeg"

    # ============================================================
    # CHECK FILE
    # ============================================================

    @staticmethod
    def _check_file(
        path: Optional[str],
        description: str,
    ):

        if not path:
            return

        if not os.path.isfile(path):

            raise FileNotFoundError(
                f"\n{description} not found:\n"
                f"{path}\n"
            )

    # ============================================================
    # CHECK IMAGE
    # ============================================================

    @staticmethod
    def _check_image(
        image_file: str,
    ):

        extension = (
            Path(image_file)
            .suffix
            .lower()
        )

        supported = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }

        if extension not in supported:

            raise ValueError(
                "\nUnsupported image format: "
                f"{extension}\n"
                "Supported formats: "
                ".png, .jpg, .jpeg, .webp"
            )

    # ============================================================
    # RUN FFMPEG
    # ============================================================

    @staticmethod
    def _run(
        command: list[str],
    ):

        print("\n" + "=" * 70)
        print("[VideoRenderer] FFmpeg command")
        print("=" * 70)

        print(
            " ".join(
                f'"{item}"'
                if " " in item
                else item
                for item in command
            )
        )

        print("=" * 70)

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:

            print("\nFFMPEG ERROR\n")
            print(result.stderr)

            raise RuntimeError(
                "FFmpeg rendering failed."
            )

        return result

    # ============================================================
    # GET AUDIO DURATION
    # ============================================================

    def get_duration(
        self,
        audio_file: str,
    ) -> float:

        self._check_file(
            audio_file,
            "Audio file",
        )

        command = [
            self.ffmpeg,
            "-i",
            audio_file,
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        match = re.search(
            r"Duration:\s*"
            r"(\d+):(\d+):(\d+(?:\.\d+)?)",
            result.stderr,
        )

        if not match:

            raise RuntimeError(
                "Could not determine audio duration:\n"
                f"{audio_file}"
            )

        hours = int(
            match.group(1)
        )

        minutes = int(
            match.group(2)
        )

        seconds = float(
            match.group(3)
        )

        duration = (
            hours * 3600
            + minutes * 60
            + seconds
        )

        return duration

    # ============================================================
    # SUBTITLE FILTER
    # ============================================================

    def _subtitle_filter(
        self,
        subtitle_file: Optional[str],
    ) -> Optional[str]:

        if not subtitle_file:
            return None

        subtitle_file = os.path.abspath(
            subtitle_file
        )

        if not os.path.isfile(
            subtitle_file
        ):
            raise FileNotFoundError(
                f"Subtitle file not found:\n"
                f"{subtitle_file}"
            )

        # Convert Windows path for FFmpeg
        subtitle_path = (
            subtitle_file
            .replace("\\", "/")
        )

        # Escape colon in drive letter
        subtitle_path = (
            subtitle_path
            .replace(":", r"\:")
        )

        return (
            f"subtitles='{subtitle_path}'"
            ":force_style="
            "'FontName=Noto Sans,"
            "FontSize=22,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,"
            "BorderStyle=1,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            "MarginV=180'"
        )

    # ============================================================
    # RENDER SCENE 2
    # ============================================================

    def render_scene_2(
        self,
        image_file: str,
        audio_file: str,
        subtitle_file: Optional[str] = None,
        shloka_overlay: Optional[str] = None,
        output_file: str = "output/videos/scene_video.mp4",
    ) -> str:

        print("\n")
        print("=" * 70)
        print("SBG V3 - SCENE 2 VIDEO")
        print("=" * 70)

        # --------------------------------------------------------
        # Validate image
        # --------------------------------------------------------

        self._check_file(
            image_file,
            "Scene 2 image",
        )

        self._check_image(
            image_file
        )

        print(
            f"[VideoRenderer] Scene 2 image:"
            f"\n{image_file}"
        )

        # --------------------------------------------------------
        # Validate audio
        # --------------------------------------------------------

        self._check_file(
            audio_file,
            "Scene 2 narration audio",
        )

        print(
            f"[VideoRenderer] Scene 2 audio:"
            f"\n{audio_file}"
        )

        # --------------------------------------------------------
        # Validate subtitles
        # --------------------------------------------------------

        if subtitle_file:

            self._check_file(
                subtitle_file,
                "Scene 2 subtitle",
            )

            print(
                f"[VideoRenderer] Scene 2 subtitles:"
                f"\n{subtitle_file}"
            )

        # --------------------------------------------------------
        # Validate Shloka overlay
        # --------------------------------------------------------

        if shloka_overlay:

            self._check_file(
                shloka_overlay,
                "Scene 2 Shloka overlay",
            )

            print(
                f"[VideoRenderer] Scene 2 Shloka:"
                f"\n{shloka_overlay}"
            )

        # --------------------------------------------------------
        # Get narration duration
        # --------------------------------------------------------

        duration = self.get_duration(
            audio_file
        )

        print(
            f"[VideoRenderer] Audio duration:"
            f" {duration:.3f}s"
        )

        # --------------------------------------------------------
        # Output
        # --------------------------------------------------------

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # INPUTS
        #
        # Input 0 = PNG image
        # Input 1 = narration audio
        # Input 2 = Shloka overlay
        # --------------------------------------------------------

        command = [
            self.ffmpeg,
            "-y",

            # Scene 2 PNG
            "-loop",
            "1",

            "-framerate",
            str(self.fps),

            "-i",
            image_file,

            # Scene 2 narration
            "-i",
            audio_file,
        ]

        has_shloka = (
            shloka_overlay is not None
        )

        if has_shloka:

            command.extend(
                [
                    # Shloka WebM
                    "-i",
                    shloka_overlay,
                ]
            )

        # --------------------------------------------------------
        # FILTER GRAPH
        # --------------------------------------------------------

        filters = []

        # ========================================================
        # BASE IMAGE
        # ========================================================

        filters.append(
            "[0:v]"
            f"scale={self.width}:{self.height}:"
            "force_original_aspect_ratio=increase,"
            f"crop={self.width}:{self.height},"
            "setsar=1"
            "[base]"
        )

        current = "[base]"

        # ========================================================
        # SHLOKA OVERLAY
        # ========================================================

        if has_shloka:

            filters.append(
                "[2:v]"
                f"scale={self.width}:{self.height}:"
                "force_original_aspect_ratio=disable,"
                "format=rgba"
                "[shloka]"
            )

            filters.append(
                f"{current}"
                "[shloka]"
                "overlay=0:0:"
                "format=auto"
                "[with_shloka]"
            )

            current = "[with_shloka]"

        # ========================================================
        # SUBTITLES
        # ========================================================

        subtitle_filter = (
            self._subtitle_filter(
                subtitle_file
            )
        )

        if subtitle_filter:

            filters.append(
                f"{current}"
                f"{subtitle_filter}"
                "[final]"
            )

            current = "[final]"

        # ========================================================
        # FILTER COMPLEX
        # ========================================================

        filter_complex = ";".join(
            filters
        )

        # ========================================================
        # OUTPUT
        # ========================================================

        command.extend(
            [
                "-filter_complex",
                filter_complex,

                # Video
                "-map",
                current,

                # Narration audio
                "-map",
                "1:a",

                # Exact narration duration
                "-t",
                str(duration),

                # H.264
                "-c:v",
                "libx264",

                "-preset",
                "medium",

                "-crf",
                "20",

                "-pix_fmt",
                "yuv420p",

                "-r",
                str(self.fps),

                # AAC narration
                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                # Avoid extending beyond narration
                "-shortest",

                output_file,
            ]
        )

        # --------------------------------------------------------
        # RUN
        # --------------------------------------------------------

        self._run(
            command
        )

        print("\n")
        print("=" * 70)
        print("SCENE 2 VIDEO CREATED")
        print("=" * 70)
        print(
            f"Output:\n{output_file}"
        )
        print("=" * 70)

        return output_file


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def render_scene_2(
    image_file: str,
    audio_file: str,
    subtitle_file: Optional[str] = None,
    shloka_overlay: Optional[str] = None,
) -> str:

    renderer = VideoRenderer()

    return renderer.render_scene_2(
        image_file=image_file,
        audio_file=audio_file,
        subtitle_file=subtitle_file,
        shloka_overlay=shloka_overlay,
        output_file=(
            "output/videos/scene_video.mp4"
        ),
    )
