# modules/shloka_highlighter.py

from __future__ import annotations

import json
import math
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_FONT = r"C:\SBG\SBG-v3\assets\fonts\NotoSansDevanagari-Regular.ttf"

# Normal Shloka
NORMAL_COLOR = (245, 225, 170, 255)

# Currently spoken word - TURQUOISE
HIGHLIGHT_COLOR = (64, 224, 208, 255)

# Previously spoken words
SPOKEN_COLOR = (220, 195, 145, 210)

# Text shadow
SHADOW_COLOR = (0, 0, 0, 190)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class WordPosition:
    word: str
    index: int
    x: int
    y: int
    width: int
    height: int


# ============================================================
# SHLOKA HIGHLIGHTER
# ============================================================

class ShlokaHighlighter:

    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        font_path: str = DEFAULT_FONT,
        font_size: int = 64,
        fps: int = 30,
        line_spacing: int = 20,
        word_spacing: int = 28,
        max_line_width: int = 940,
        vertical_position: float = 0.48,
    ):

        self.width = width
        self.height = height
        self.font_path = font_path
        self.font_size = font_size
        self.fps = fps
        self.line_spacing = line_spacing
        self.word_spacing = word_spacing
        self.max_line_width = max_line_width
        self.vertical_position = vertical_position

        self.font = self._load_font()

    # ========================================================
    # FONT
    # ========================================================

    def _load_font(self):

        possible_fonts = [
            self.font_path,
            r"C:\Windows\Fonts\NotoSansDevanagari-Regular.ttf",
            r"C:\Windows\Fonts\NotoSansDevanagariUI-Regular.ttf",
            r"C:\Windows\Fonts\Mangal.ttf",
        ]

        for font in possible_fonts:

            if font and os.path.exists(font):

                print(
                    f"[ShlokaHighlighter] Using font: {font}"
                )

                return ImageFont.truetype(
                    font,
                    self.font_size,
                )

        raise FileNotFoundError(
            "Devanagari font not found.\n"
            "Install Noto Sans Devanagari or "
            "provide a valid font_path."
        )

    # ========================================================
    # LOAD NARRATION JSON
    # ========================================================

    @staticmethod
    def load_narration_json(
        narration_json: str,
    ) -> dict:

        if not os.path.exists(narration_json):

            raise FileNotFoundError(
                f"Narration JSON not found:\n"
                f"{narration_json}"
            )

        with open(
            narration_json,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        if "words" not in data:

            raise ValueError(
                "Narration JSON does not contain "
                "'words'."
            )

        return data

    # ========================================================
    # NORMALIZE DEVANAGARI TEXT
    # ========================================================

    @staticmethod
    def normalize_word(text: str) -> str:

        if not text:
            return ""

        text = text.strip()

        # Remove punctuation for matching purposes
        punctuation = (
            "।॥,;:!?\"'“”‘’()[]{}"
        )

        for char in punctuation:
            text = text.replace(
                char,
                "",
            )

        return text.strip()

    # ========================================================
    # SPLIT SHLOKA
    # ========================================================

    @staticmethod
    def split_shloka(
        shloka: str,
    ) -> List[str]:

        shloka = shloka.replace(
            "\n",
            " ",
        )

        # Punctuation is not treated as a visual word.
        shloka = re.sub(
            r"[।॥]",
            " ",
            shloka,
        )

        words = re.split(
            r"\s+",
            shloka.strip(),
        )

        return [
            word.strip()
            for word in words
            if word.strip()
        ]

    # ========================================================
    # BUILD REAL WORD TIMINGS FROM narration.json
    # ========================================================

    def build_word_timings_from_json(
        self,
        shloka: str,
        narration_data: dict,
    ) -> List[WordTiming]:

        shloka_words = self.split_shloka(
            shloka
        )

        narration_words = narration_data[
            "words"
        ]

        print(
            "\n[ShlokaHighlighter] "
            "Building real Shloka timings..."
        )

        print(
            f"Shloka words: "
            f"{len(shloka_words)}"
        )

        print(
            f"Narration timing entries: "
            f"{len(narration_words)}"
        )

        result: List[WordTiming] = []

        shloka_index = 0

        # ----------------------------------------------------
        # Process each narration timing entry
        # ----------------------------------------------------

        for entry in narration_words:

            raw_text = entry.get(
                "text",
                "",
            )

            start = float(
                entry["start"]
            )

            end = float(
                entry["end"]
            )

            # Remove punctuation and split grouped words
            entry_words = self.split_shloka(
                raw_text
            )

            if not entry_words:
                continue

            # ------------------------------------------------
            # Try to match this entry against the Shloka
            # ------------------------------------------------

            matched_words = []

            for word in entry_words:

                normalized = self.normalize_word(
                    word
                )

                if (
                    shloka_index
                    < len(shloka_words)
                ):

                    expected = self.normalize_word(
                        shloka_words[
                            shloka_index
                        ]
                    )

                    if normalized == expected:

                        matched_words.append(
                            shloka_words[
                                shloka_index
                            ]
                        )

                        shloka_index += 1

                    else:

                        # Try searching ahead.
                        found = False

                        for look_ahead in range(
                            shloka_index,
                            min(
                                shloka_index + 5,
                                len(shloka_words),
                            ),
                        ):

                            candidate = (
                                self.normalize_word(
                                    shloka_words[
                                        look_ahead
                                    ]
                                )
                            )

                            if normalized == candidate:

                                print(
                                    "[ShlokaHighlighter] "
                                    f"Recovered alignment: "
                                    f"{word} → "
                                    f"{shloka_words[look_ahead]}"
                                )

                                shloka_index = (
                                    look_ahead + 1
                                )

                                matched_words.append(
                                    shloka_words[
                                        look_ahead
                                    ]
                                )

                                found = True
                                break

                        if not found:

                            print(
                                "[ShlokaHighlighter] "
                                f"Skipping narration word: "
                                f"{word}"
                            )

                else:
                    break

            if not matched_words:
                continue

            # ------------------------------------------------
            # Split combined timing
            # ------------------------------------------------

            if len(matched_words) == 1:

                result.append(
                    WordTiming(
                        word=matched_words[0],
                        start=start,
                        end=end,
                    )
                )

            else:

                # --------------------------------------------
                # Proportional timing allocation
                #
                # Longer Sanskrit words receive slightly
                # more of the combined timing.
                # --------------------------------------------

                lengths = [
                    max(
                        1,
                        len(
                            self.normalize_word(
                                word
                            )
                        ),
                    )
                    for word in matched_words
                ]

                total_length = sum(
                    lengths
                )

                current_time = start

                total_duration = (
                    end - start
                )

                for i, word in enumerate(
                    matched_words
                ):

                    portion = (
                        lengths[i]
                        / total_length
                    )

                    word_duration = (
                        total_duration
                        * portion
                    )

                    word_start = (
                        current_time
                    )

                    word_end = (
                        current_time
                        + word_duration
                    )

                    result.append(
                        WordTiming(
                            word=word,
                            start=word_start,
                            end=word_end,
                        )
                    )

                    current_time = word_end

        # ----------------------------------------------------
        # Diagnostics
        # ----------------------------------------------------

        print(
            "\n[ShlokaHighlighter] "
            "Final Shloka timings:"
        )

        for timing in result:

            print(
                f"  {timing.word:20s} "
                f"{timing.start:7.3f} → "
                f"{timing.end:7.3f}"
            )

        if len(result) != len(
            shloka_words
        ):

            print(
                "\n[ShlokaHighlighter] WARNING:"
            )

            print(
                f"Expected {len(shloka_words)} "
                f"Shloka words."
            )

            print(
                f"Matched {len(result)}."
            )

        return result

    # ========================================================
    # MEASUREMENT
    # ========================================================

    def _measure(
        self,
        draw: ImageDraw.ImageDraw,
        word: str,
    ):

        bbox = draw.textbbox(
            (0, 0),
            word,
            font=self.font,
        )

        return (
            bbox[2] - bbox[0],
            bbox[3] - bbox[1],
        )

    # ========================================================
    # MULTI-LINE LAYOUT
    # ========================================================

    def _build_layout(
        self,
        draw: ImageDraw.ImageDraw,
        words: List[str],
    ) -> List[WordPosition]:

        lines = []
        current_line = []
        current_width = 0

        for index, word in enumerate(
            words
        ):

            word_width, word_height = (
                self._measure(
                    draw,
                    word,
                )
            )

            required_width = (
                word_width
            )

            if current_line:

                required_width += (
                    self.word_spacing
                )

            required_width += (
                current_width
            )

            if (
                current_line
                and required_width
                > self.max_line_width
            ):

                lines.append(
                    current_line
                )

                current_line = []
                current_width = 0

            if current_line:

                current_width += (
                    self.word_spacing
                )

            current_line.append(
                (
                    index,
                    word,
                    word_width,
                    word_height,
                )
            )

            current_width += word_width

        if current_line:

            lines.append(
                current_line
            )

        # ----------------------------------------------------
        # Calculate line heights
        # ----------------------------------------------------

        line_heights = []

        for line in lines:

            line_heights.append(
                max(
                    item[3]
                    for item in line
                )
            )

        total_height = (
            sum(line_heights)
            + self.line_spacing
            * (len(lines) - 1)
        )

        start_y = int(
            self.height
            * self.vertical_position
            - total_height / 2
        )

        positions = []

        current_y = start_y

        for line_number, line in enumerate(
            lines
        ):

            line_width = sum(
                item[2]
                for item in line
            )

            line_width += (
                self.word_spacing
                * (len(line) - 1)
            )

            start_x = int(
                (
                    self.width
                    - line_width
                )
                / 2
            )

            current_x = start_x

            line_height = (
                line_heights[
                    line_number
                ]
            )

            for (
                index,
                word,
                word_width,
                word_height,
            ) in line:

                positions.append(
                    WordPosition(
                        word=word,
                        index=index,
                        x=current_x,
                        y=current_y,
                        width=word_width,
                        height=word_height,
                    )
                )

                current_x += (
                    word_width
                    + self.word_spacing
                )

            current_y += (
                line_height
                + self.line_spacing
            )

        return positions

    # ========================================================
    # CURRENT WORD
    # ========================================================

    @staticmethod
    def _get_current_word(
        time: float,
        timings: List[WordTiming],
    ) -> Optional[int]:

        for index, timing in enumerate(
            timings
        ):

            if (
                timing.start
                <= time
                < timing.end
            ):

                return index

        return None

    # ========================================================
    # DRAW FRAME
    # ========================================================

    def _draw_frame(
        self,
        image: Image.Image,
        positions: List[WordPosition],
        current_index: Optional[int],
    ):

        draw = ImageDraw.Draw(
            image
        )

        for position in positions:

            index = position.index

            if current_index is None:

                color = NORMAL_COLOR

            elif index == current_index:

                color = HIGHLIGHT_COLOR

            elif index < current_index:

                color = SPOKEN_COLOR

            else:

                color = NORMAL_COLOR

            # ------------------------------------------------
            # Shadow
            # ------------------------------------------------

            draw.text(
                (
                    position.x + 4,
                    position.y + 4,
                ),
                position.word,
                font=self.font,
                fill=SHADOW_COLOR,
            )

            # ------------------------------------------------
            # Sanskrit word
            # ------------------------------------------------

            draw.text(
                (
                    position.x,
                    position.y,
                ),
                position.word,
                font=self.font,
                fill=color,
            )

    # ========================================================
    # GENERATE FRAMES
    # ========================================================

    def generate_frames(
        self,
        shloka: str,
        word_timings: List[WordTiming],
        frames_dir: str,
        duration: Optional[float] = None,
    ) -> float:

        os.makedirs(
            frames_dir,
            exist_ok=True,
        )

        words = self.split_shloka(
            shloka
        )

        if not words:

            raise ValueError(
                "Shloka contains no words."
            )

        if not word_timings:

            raise ValueError(
                "No word timings supplied."
            )

        # ----------------------------------------------------
        # Create layout
        # ----------------------------------------------------

        temp_image = Image.new(
            "RGBA",
            (
                self.width,
                self.height,
            ),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            temp_image
        )

        positions = self._build_layout(
            draw,
            words,
        )

        # ----------------------------------------------------
        # Determine duration
        # ----------------------------------------------------

        timing_duration = max(
            timing.end
            for timing in word_timings
        )

        if duration is None:

            duration = timing_duration

        else:

            duration = max(
                duration,
                timing_duration,
            )

        total_frames = int(
            math.ceil(
                duration * self.fps
            )
        )

        print(
            "\n[ShlokaHighlighter]"
        )

        print(
            f"Words: {len(words)}"
        )

        print(
            f"Duration: {duration:.2f}s"
        )

        print(
            f"Frames: {total_frames}"
        )

        # ----------------------------------------------------
        # Generate PNG frames
        # ----------------------------------------------------

        for frame_number in range(
            total_frames
        ):

            current_time = (
                frame_number
                / self.fps
            )

            current_index = (
                self._get_current_word(
                    current_time,
                    word_timings,
                )
            )

            image = Image.new(
                "RGBA",
                (
                    self.width,
                    self.height,
                ),
                (0, 0, 0, 0),
            )

            self._draw_frame(
                image,
                positions,
                current_index,
            )

            frame_path = os.path.join(
                frames_dir,
                f"frame_{frame_number:06d}.png",
            )

            image.save(
                frame_path,
                format="PNG",
            
            )

        return duration

    # ========================================================
    # FFMPEG
    # ========================================================

    @staticmethod
    def _find_ffmpeg():

        project_ffmpeg = os.path.join(
            "tools",
            "ffmpeg",
            "bin",
            "ffmpeg.exe",
        )

        if os.path.exists(
            project_ffmpeg
        ):

            return project_ffmpeg

        return "ffmpeg"

    # ========================================================
    # PNG → TRANSPARENT WEBM
    # ========================================================

    def _frames_to_webm(
        self,
        frames_dir: str,
        output_path: str,
        duration: float,
    ):

        os.makedirs(
            os.path.dirname(
                output_path
            ) or ".",
            exist_ok=True,
        )

        ffmpeg = self._find_ffmpeg()

        input_pattern = os.path.join(
            frames_dir,
            "frame_%06d.png",
        )

        command = [
            ffmpeg,
            "-y",

            # ------------------------------------------------
            # PNG sequence
            # ------------------------------------------------

            "-framerate",
            str(self.fps),

            "-i",
            input_pattern,

            # ------------------------------------------------
            # Preserve RGBA from PNG
            # ------------------------------------------------

            "-vf",
            "format=rgba",

            # ------------------------------------------------
            # Exact duration
            # ------------------------------------------------

            "-t",
            f"{duration:.6f}",

            # ------------------------------------------------
            # VP9
            # ------------------------------------------------

            "-c:v",
            "libvpx-vp9",

            # ------------------------------------------------
            # REAL VP9 ALPHA
            # ------------------------------------------------

            "-pix_fmt",
            "yuva420p",

            "-auto-alt-ref",
            "0",

            # Explicitly tell WebM/VP9 this stream contains alpha
            "-metadata:s:v:0",
            "alpha_mode=1",

            # ------------------------------------------------
            # Quality
            # ------------------------------------------------

            "-lossless",
            "1",

            "-an",

            output_path,
        ]

        print()
        print(
            "[ShlokaHighlighter] "
            "Encoding TRANSPARENT WebM..."
        )

        print(
            "FFmpeg command:"
        )

        print(
            " ".join(
                f'"{item}"'
                if " " in str(item)
                else str(item)
                for item in command
            )
        )

        print()

        subprocess.run(
            command,
            check=True,
        )

        # ----------------------------------------------------
        # Verify output
        # ----------------------------------------------------

        output_file = Path(
            output_path
        )

        if not output_file.exists():

            raise FileNotFoundError(
                "Transparent WebM was not created:\n"
                f"{output_file}"
            )

        if output_file.stat().st_size <= 0:

            raise RuntimeError(
                "Transparent WebM is empty:\n"
                f"{output_file}"
            )

        print(
            "[ShlokaHighlighter] "
            f"WebM created: {output_file}"
        )

        print(
            "[ShlokaHighlighter] "
            f"Size: {output_file.stat().st_size:,} bytes"
        )

    # ========================================================
    # CREATE FROM narration.json
    # ========================================================

    def create_from_narration_json(
        self,
        shloka: str,
        narration_json: str,
        output_path: str,
        temp_dir: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> str:

        narration_data = (
            self.load_narration_json(
                narration_json
            )
        )

        word_timings = (
            self.build_word_timings_from_json(
                shloka=shloka,
                narration_data=narration_data,
            )
        )

        if not word_timings:

            raise RuntimeError(
                "Could not match any Shloka "
                "words to narration.json."
            )

        if temp_dir is None:

            temp_dir = os.path.join(
                os.path.dirname(
                    output_path
                ) or ".",
                "_shloka_frames",
            )

        actual_duration = (
            self.generate_frames(
                shloka=shloka,
                word_timings=word_timings,
                frames_dir=temp_dir,
                duration=duration,
            )
        )

        self._frames_to_webm(
            frames_dir=temp_dir,
            output_path=output_path,
            duration=actual_duration,
        )

        print(
            "\n[ShlokaHighlighter] "
            "SUCCESS"
        )

        print(
            f"Overlay: {output_path}"
        )

        return output_path


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def create_shloka_overlay_from_narration(
    shloka: str,
    narration_json: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    font_path: str = DEFAULT_FONT,
    font_size: int = 64,
    fps: int = 30,
) -> str:

    highlighter = ShlokaHighlighter(
        width=width,
        height=height,
        font_path=font_path,
        font_size=font_size,
        fps=fps,
    )

    return highlighter.create_from_narration_json(
        shloka=shloka,
        narration_json=narration_json,
        output_path=output_path,
    )


# ============================================================
# CHAPTER 1 VERSE 1 TEST
# ============================================================

if __name__ == "__main__":

    verse_1 = (
        "धृतराष्ट्र उवाच । "
        "धर्मक्षेत्रे कुरुक्षेत्रे "
        "समवेता युयुत्सवः । "
        "मामकाः पाण्डवाश्चैव "
        "किमकुर्वत सञ्जय ॥"
    )

    narration_json = (
        "output/shloka/narration.json"
    )

    output_overlay = (
        "output/shloka/"
        "chapter1_verse1.webm"
    )

    create_shloka_overlay_from_narration(
        shloka=verse_1,
        narration_json=narration_json,
        output_path=output_overlay,
    )