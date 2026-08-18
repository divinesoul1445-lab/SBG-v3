# modules/videos.py

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


class VideoRenderer:
    """
    SBG V3 Scene Video Renderer

    Architecture:

        Fixed Image
             +
        Scene Narration Audio
             +
        Scene Subtitles
             +
        Optional Shloka Karaoke Overlay
             ↓
        Independent Scene Video

    Background music is intentionally NOT added here.
    It should only be added during the final render.
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
    # FFmpeg
    # ============================================================

    @staticmethod
    def _find_ffmpeg() -> str:

        possible_paths = [
            os.path.join(
                "tools",
                "ffmpeg",
                "bin",
                "ffmpeg.exe",
            ),

            os.path.join(
                "tools",
                "ffmpeg",
                "ffmpeg.exe",
            ),

            "ffmpeg",
        ]

        for path in possible_paths:

            if path == "ffmpeg":
                return path

            if os.path.exists(path):
                return path

        return "ffmpeg"

    # ============================================================
    # Utilities
    # ============================================================

    @staticmethod
    def _check_file(
        path: Optional[str],
        description: str,
    ):

        if not path:
            return

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{description} not found:\n{path}"
            )

    @staticmethod
    def _run(
        command: list[str],
    ):

        print("\n[VideoRenderer]")
        print("Running FFmpeg:")

        print(
            " ".join(
                f'"{x}"' if " " in x else x
                for x in command
            )
        )

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:

            print("\nFFmpeg ERROR:\n")
            print(result.stderr)

            raise RuntimeError(
                "FFmpeg video rendering failed."
            )

        return result

    # ============================================================
    # Get audio duration
    # ============================================================

    def get_duration(
        self,
        file_path: str,
    ) -> float:

        self._check_file(
            file_path,
            "Audio file",
        )

        command = [
            self.ffmpeg,
            "-i",
            file_path,
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stderr = result.stderr

        import re

        match = re.search(
            r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)",
            stderr,
        )

        if not match:
            raise RuntimeError(
                f"Could not determine duration:\n{file_path}"
            )

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))

        return (
            hours * 3600
            + minutes * 60
            + seconds
        )

    # ============================================================
    # Prepare subtitle filter
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

        # FFmpeg Windows paths need escaping
        subtitle_path = subtitle_file.replace(
            "\\",
            "/",
        )

        subtitle_path = subtitle_path.replace(
            ":",
            "\\:",
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
    # Create basic scene video
    # ============================================================

    def render_scene(
        self,
        image_file: str,
        audio_file: str,
        output_file: str,
        subtitle_file: Optional[str] = None,
        shloka_overlay: Optional[str] = None,
        duration: Optional[float] = None,
        ) -> str:

        print("\n" + "=" * 60)
        print("[VideoRenderer] Rendering SBG V3 scene")
        print("=" * 60)

        # --------------------------------------------------------
        # Validate image
        # --------------------------------------------------------

        self._check_file(
            image_file,
            "Scene image",
        )

        image_ext = Path(image_file).suffix.lower()

        supported_images = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }

        if image_ext not in supported_images:

            raise ValueError(
                f"Unsupported image format: {image_ext}\n"
                f"Supported formats: "
                f"{', '.join(sorted(supported_images))}"
            )

        print(
            f"[VideoRenderer] Image: {image_file}"
        )

        print(
            f"[VideoRenderer] Image format: "
            f"{image_ext}"
        )

        # --------------------------------------------------------
        # Validate audio
        # --------------------------------------------------------

        self._check_file(
            audio_file,
            "Scene audio",
        )

        # --------------------------------------------------------
        # Optional subtitle
        # --------------------------------------------------------

        self._check_file(
            subtitle_file,
            "Subtitle file",
        )

        # --------------------------------------------------------
        # Optional Shloka overlay
        # --------------------------------------------------------

        self._check_file(
            shloka_overlay,
            "Shloka overlay",
        )

        # --------------------------------------------------------
        # Duration
        # --------------------------------------------------------

        if duration is None:

            duration = self.get_duration(
                audio_file
            )

        print(
            f"[VideoRenderer] Duration: "
            f"{duration:.2f}s"
        )

        # --------------------------------------------------------
        # Output directory
        # --------------------------------------------------------

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # FFmpeg inputs
        # --------------------------------------------------------

        command = [
            self.ffmpeg,
            "-y",

            # Fixed image
            "-loop",
            "1",

            "-i",
            image_file,

            # Narration
            "-i",
            audio_file,
        ]

        # --------------------------------------------------------
        # Shloka overlay
        # --------------------------------------------------------

        has_overlay = bool(
            shloka_overlay
        )

        if has_overlay:

            command.extend(
                [
                    "-i",
                    shloka_overlay,
                ]
            )

        # --------------------------------------------------------
        # Filters
        # --------------------------------------------------------

        filters = []

        filters.append(
            "[0:v]"
            f"scale={self.width}:{self.height}:"
            "force_original_aspect_ratio=increase,"
            f"crop={self.width}:{self.height},"
            "setsar=1"
            "[base]"
        )

        current_video = "[base]"

        # --------------------------------------------------------
        # Shloka overlay
        # --------------------------------------------------------

        if has_overlay:

            filters.append(
                "[2:v]"
                f"scale={self.width}:{self.height}:"
                "force_original_aspect_ratio=disable"
                "[shloka]"
            )

            filters.append(
                f"{current_video}"
                "[shloka]"
                "overlay=0:0:format=auto"
                "[with_shloka]"
            )

            current_video = "[with_shloka]"

        # --------------------------------------------------------
        # Subtitles
        # --------------------------------------------------------

        subtitle_filter = self._subtitle_filter(
            subtitle_file
        )

        if subtitle_filter:

            filters.append(
                f"{current_video}"
                f"{subtitle_filter}"
                "[finalvideo]"
            )

            current_video = "[finalvideo]"

        # --------------------------------------------------------
        # FFmpeg filter graph
        # --------------------------------------------------------

        filter_complex = ";".join(
            filters
        )

        command.extend(
            [
                "-filter_complex",
                filter_complex,

                "-map",
                current_video,

                "-map",
                "1:a",

                "-t",
                str(duration),

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

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-shortest",

                output_file,
            ]
        )

        self._run(
            command
        )

        print(
            f"\n[VideoRenderer] Scene created:"
            f"\n{output_file}"
        )

        return output_file

    # ============================================================
    # Scene without subtitles / overlay
    # ============================================================

    def render_basic_scene(
        self,
        image_file: str,
        audio_file: str,
        output_file: str,
        duration: Optional[float] = None,
    ) -> str:

        return self.render_scene(
            image_file=image_file,
            audio_file=audio_file,
            output_file=output_file,
            subtitle_file=None,
            shloka_overlay=None,
            duration=duration,
        )

    # ============================================================
    # Scene with Shloka karaoke
    # ============================================================

    def render_shloka_scene(
        self,
        image_file: str,
        audio_file: str,
        shloka_overlay: str,
        output_file: str,
        subtitle_file: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> str:

        return self.render_scene(
            image_file=image_file,
            audio_file=audio_file,
            output_file=output_file,
            subtitle_file=subtitle_file,
            shloka_overlay=shloka_overlay,
            duration=duration,
        )


# ================================================================
# Convenience function
# ================================================================

def render_scene_video(
    image_file: str,
    audio_file: str,
    output_file: str,
    subtitle_file: Optional[str] = None,
    shloka_overlay: Optional[str] = None,
    duration: Optional[float] = None,
) -> str:

    renderer = VideoRenderer()

    return renderer.render_scene(
        image_file=image_file,
        audio_file=audio_file,
        output_file=output_file,
        subtitle_file=subtitle_file,
        shloka_overlay=shloka_overlay,
        duration=duration,
    )


# ================================================================
# Test
# ================================================================

if __name__ == "__main__":

    renderer = VideoRenderer()

    renderer.render_scene(
        image_file="assets/images/test.jpg",
        audio_file="output/audio/test.mp3",
        subtitle_file="output/subtitles/test.srt",
        shloka_overlay="output/shloka_overlay.webm",
        output_file="output/videos/test_scene.mp4",
    )