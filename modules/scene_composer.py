"""
Scene Composer
==============

SBG V3

Creates the polished visual artwork for each scene.

Input:
    Fixed scene image

Output:
    1080x1920 composed PNG

The source image is never regenerated.

Visual layers:
    1. Fixed background image
    2. Cinematic readability gradient
    3. Bhagavad Gita branding
    4. Chapter / verse label
    5. Sanskrit shloka panel
    6. Scene indicator
    7. Bottom devotional mark

The lower portion of the frame is intentionally kept
relatively clean so video subtitles can be added later.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
)



class SceneComposer:

    # =========================================================
    # VIDEO SIZE
    # =========================================================

    WIDTH = 1080
    HEIGHT = 1920

    # =========================================================
    # COLORS
    # =========================================================

    GOLD = (
        212,
        166,
        70,
        255,
    )

    LIGHT_GOLD = (
        245,
        211,
        130,
        255,
    )

    IVORY = (
        255,
        248,
        225,
        255,
    )

    WHITE = (
        255,
        255,
        255,
        255,
    )

    DARK = (
        20,
        10,
        3,
        210,
    )
    # =========================================================
    # SCENE IMAGE POSITIONING
    # =========================================================

    IMAGE_FOCUS = {
        1: 0.50,
        2: 0.50,
        3: 0.50,
        4: 0.50,
    }

    SCENE_IMAGE_MODE = {
    1: "crop",
    2: "crop",
    3: "fit",
    4: "crop",
    }
    
    # =========================================================
    # FONT SIZES
    # =========================================================

    BRAND_SIZE = 42

    CHAPTER_SIZE = 45

    SHLOKA_SIZE = 54

    SHLOKA_HEADING_SIZE = 30

    SCENE_SIZE = 25

    BOTTOM_SIZE = 28

    # =========================================================
    # LAYOUT
    # =========================================================

    BRAND_Y = 65

    CHAPTER_Y = 150

    DECORATIVE_LINE_Y = 195

    SHLOKA_PANEL_Y = 260

    SHLOKA_PANEL_WIDTH = 930

    # ---------------------------------------------------------
    # IMPORTANT:
    #
    # Keep subtitles away from the shloka.
    # The subtitle renderer will occupy the lower portion.
    # ---------------------------------------------------------

    SAFE_SUBTITLE_TOP = 1480

    BOTTOM_MARK_Y = 1785

    # =========================================================
    # INIT
    # =========================================================

    def __init__(
        self,
        fonts_folder: Optional[Path] = None,
    ):

        if fonts_folder is None:

            fonts_folder = (
                Path(__file__).resolve().parent.parent
                / "assets"
                / "fonts"
            )

        self.fonts_folder = Path(
            fonts_folder
        )

        # -----------------------------------------------------
        # Regular Devanagari
        # -----------------------------------------------------

        self.devanagari_font = (
            self._find_font(
                [
                    "NotoSerifDevanagari-Regular.ttf",
                    "NotoSansDevanagari-Regular.ttf",
                ]
            )
        )

        # -----------------------------------------------------
        # Bold Devanagari
        # -----------------------------------------------------

        self.devanagari_bold_font = (
            self._find_font(
                [
                    "NotoSerifDevanagari-Bold.ttf",
                    "NotoSerifDevanagari-Regular.ttf",
                ]
            )
        )

        # -----------------------------------------------------
        # Windows fallback
        # -----------------------------------------------------

        windows_fonts = Path(
            r"C:\Windows\Fonts"
        )

        if self.devanagari_font is None:

            self.devanagari_font = (
                self._find_font_in_folder(
                    windows_fonts,
                    [
                        "NotoSerifDevanagari-Regular.ttf",
                        "NotoSansDevanagari-Regular.ttf",
                        "Mangal.ttf",
                    ],
                )
            )

        if self.devanagari_bold_font is None:

            self.devanagari_bold_font = (
                self._find_font_in_folder(
                    windows_fonts,
                    [
                        "NotoSerifDevanagari-Bold.ttf",
                        "NotoSansDevanagari-Bold.ttf",
                        "Mangal.ttf",
                    ],
                )
            )

        if self.devanagari_font is None:

            raise FileNotFoundError(
                "\n"
                "Devanagari font not found.\n\n"
                "Place the following font in:\n"
                f"{self.fonts_folder}\n\n"
                "Recommended:\n"
                "NotoSerifDevanagari-Regular.ttf\n"
                "NotoSerifDevanagari-Bold.ttf\n"
            )

        if self.devanagari_bold_font is None:

            self.devanagari_bold_font = (
                self.devanagari_font
            )


    # =========================================================
    # SHLÖKA PANEL
    # =========================================================

    def _draw_shloka_panel(
        self,
        image,
        shloka: str,
    ):
        """
        Draw the Sanskrit shloka in a readable cinematic panel.

        The panel is positioned directly below the header/divider
        area so Scene 1 has a clear visual hierarchy:

            श्रीमद्भगवद्गीता
            अध्याय X • श्लोक Y
                    ───
            [ SHLOKA PANEL ]
                    ...
            ॥ हरिः ॐ ॥

        Uses the project's Noto Serif Devanagari font.
        """

        if image is None:
            return None

        shloka = (
            ""
            if shloka is None
            else str(shloka).strip()
        )

        if not shloka:
            return image

        # =====================================================
        # FONT
        # =====================================================

        font_file = Path(
            r"C:\SBG\SBG-v3\assets\fonts\NotoSerifDevanagari-Regular.ttf"
        )

        if not font_file.exists():
            raise FileNotFoundError(
                "Devanagari font not found:\n"
                f"{font_file}"
            )

        font_size = 43

        font = ImageFont.truetype(
            str(font_file),
            font_size,
        )

        # =====================================================
        # DRAW OBJECT
        # =====================================================

        draw = ImageDraw.Draw(
            image,
            "RGBA",
        )

        # =====================================================
        # PANEL GEOMETRY
        #
        # IMPORTANT:
        # Start below the existing decorative divider.
        # =====================================================

        panel_width = int(
            self.WIDTH * 0.88
        )

        panel_x = (
            self.WIDTH - panel_width
        ) // 2

        # Move panel upward.
        #
        # For 1080x1920 this starts around y=650,
        # leaving the header area clean.
        panel_top = int(
            self.HEIGHT * 0.55
        )

        # Initial panel height.
        panel_height = int(
            self.HEIGHT * 0.24
        )

        panel_bottom = (
            panel_top
            + panel_height
        )

        # =====================================================
        # WRAP SHLOKA
        # =====================================================

        words = shloka.split()

        lines = []
        current_line = ""

        max_text_width = (
            panel_width - 90
        )

        for word in words:

            if not current_line:
                test_line = word
            else:
                test_line = (
                    current_line
                    + " "
                    + word
                )

            bbox = draw.textbbox(
                (0, 0),
                test_line,
                font=font,
            )

            text_width = (
                bbox[2] - bbox[0]
            )

            if text_width <= max_text_width:

                current_line = test_line

            else:

                if current_line:
                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        # =====================================================
        # LINE SPACING
        # =====================================================

        line_spacing = 18

        line_heights = []

        for line in lines:

            bbox = draw.textbbox(
                (0, 0),
                line,
                font=font,
            )

            line_heights.append(
                bbox[3] - bbox[1]
            )

        text_height = (
            sum(line_heights)
            + (
                line_spacing
                * max(
                    0,
                    len(lines) - 1,
                )
            )
        )

        # =====================================================
        # PANEL HEIGHT
        # =====================================================

        required_height = (
            text_height + 70
        )

        if required_height > panel_height:

            panel_height = (
                required_height
            )

            panel_bottom = (
                panel_top
                + panel_height
            )

        # =====================================================
        # PANEL BACKGROUND
        # =====================================================

        draw.rounded_rectangle(
            (
                panel_x,
                panel_top,
                panel_x + panel_width,
                panel_bottom,
            ),
            radius=32,
            fill=(
                15,
                8,
                3,
                165,
            ),
            outline=(
                245,
                211,
                130,
                150,
            ),
            width=2,
        )

        # =====================================================
        # INNER BORDER
        # =====================================================

        inset = 10

        draw.rounded_rectangle(
            (
                panel_x + inset,
                panel_top + inset,
                panel_x
                + panel_width
                - inset,
                panel_bottom
                - inset,
            ),
            radius=26,
            outline=(
                245,
                211,
                130,
                55,
            ),
            width=1,
        )

        # =====================================================
        # TEXT POSITION
        # =====================================================

        current_y = (
            panel_top
            + (
                panel_height
                - text_height
            )
            // 2
        )

        # =====================================================
        # DRAW SHLOKA
        # =====================================================

        for index, line in enumerate(
            lines
        ):

            bbox = draw.textbbox(
                (0, 0),
                line,
                font=font,
            )

            text_width = (
                bbox[2] - bbox[0]
            )

            x = (
                self.WIDTH
                - text_width
            ) // 2

            # -------------------------------------------------
            # Shadow
            # -------------------------------------------------

            draw.text(
                (
                    x + 2,
                    current_y + 3,
                ),
                line,
                font=font,
                fill=(
                    0,
                    0,
                    0,
                    190,
                ),
            )

            # -------------------------------------------------
            # Main text
            # -------------------------------------------------

            draw.text(
                (
                    x,
                    current_y,
                ),
                line,
                font=font,
                fill=(
                    255,
                    238,
                    190,
                    255,
                ),
                stroke_width=1,
                stroke_fill=(
                    45,
                    20,
                    5,
                    220,
                ),
            )

            current_y += (
                line_heights[index]
                + line_spacing
            )

        return image
    
    # =========================================================
    # ORNAMENT HELPER
    # =========================================================

    def _draw_corner_ornament(
        self,
        draw,
        x,
        y,
        color,
        flip_x=False,
        flip_y=False,
        ):
        """
        Draw a decorative corner ornament.

        Uses positive bounding boxes for PIL ImageDraw.arc()
        so mirrored corners never produce invalid coordinates.
        """

        size = 60

        # -----------------------------------------------------
        # Determine actual corner direction
        # -----------------------------------------------------

        if not flip_x and not flip_y:
            # Top-left
            x0 = x
            y0 = y
            start_angle = 0
            end_angle = 90

        elif flip_x and not flip_y:
            # Top-right
            x0 = x - size
            y0 = y
            start_angle = 90
            end_angle = 180

        elif not flip_x and flip_y:
            # Bottom-left
            x0 = x
            y0 = y - size
            start_angle = 270
            end_angle = 360

        else:
            # Bottom-right
            x0 = x - size
            y0 = y - size
            start_angle = 180
            end_angle = 270

        x1 = x0 + size
        y1 = y0 + size

        # -----------------------------------------------------
        # Main curved ornament
        # -----------------------------------------------------

        draw.arc(
            (
                x0,
                y0,
                x1,
                y1,
            ),
            start=start_angle,
            end=end_angle,
            fill=color,
            width=3,
        )

        # -----------------------------------------------------
        # Inner curve
        # -----------------------------------------------------

        inner_size = 38

        if not flip_x and not flip_y:
            ix0 = x + 8
            iy0 = y + 8
            istart = 0
            iend = 90

        elif flip_x and not flip_y:
            ix0 = x - 8 - inner_size
            iy0 = y + 8
            istart = 90
            iend = 180

        elif not flip_x and flip_y:
            ix0 = x + 8
            iy0 = y - 8 - inner_size
            istart = 270
            iend = 360

        else:
            ix0 = x - 8 - inner_size
            iy0 = y - 8 - inner_size
            istart = 180
            iend = 270

        draw.arc(
            (
                ix0,
                iy0,
                ix0 + inner_size,
                iy0 + inner_size,
            ),
            start=istart,
            end=iend,
            fill=color,
            width=2,
        )

        # -----------------------------------------------------
        # Decorative dot
        # -----------------------------------------------------

        dot_size = 8

        if not flip_x and not flip_y:

            dx = x + 34
            dy = y + 34

        elif flip_x and not flip_y:

            dx = x - 42
            dy = y + 34

        elif not flip_x and flip_y:

            dx = x + 34
            dy = y - 42

        else:

            dx = x - 42
            dy = y - 42

        draw.ellipse(
            (
                dx,
                dy,
                dx + dot_size,
                dy + dot_size,
            ),
            fill=color,
        )
    
    # =========================================================
    # WRAPPER DEVANAGARI
    # =========================================================

    def _wrap_devanagari(
        self,
        text,
        font,
        max_width,
        draw,
    ):

        words = text.split()

        lines = []
        current = ""

        for word in words:

            test = (
                word
                if not current
                else current + " " + word
            )

            bbox = draw.textbbox(
                (0, 0),
                test,
                font=font,
            )

            width = (
                bbox[2] - bbox[0]
            )

            if width <= max_width:

                current = test

            else:

                if current:
                    lines.append(
                        current
                    )

                current = word

        if current:
            lines.append(
                current
            )

        return lines


    # =========================================================
    # DRAW DECORATIVE DIVIDER
    # =========================================================

    def _draw_decorative_divider(
        self,
        draw,
        center_x: int,
        y: int,
        width: int = 400,
    ):
        """
        Premium ornamental divider for the Chapter / Verse section.

        Designed to visually match the Shloka panel:
        - layered gold lines
        - central diamond ornament
        - small side diamonds
        - subtle glow
        - symmetrical composition
        """

        # ==================================================
        # COLORS
        # ==================================================

        bright_gold = (
            244,
            211,
            126,
            255,
        )

        light_gold = (
            232,
            190,
            94,
            240,
        )

        dark_gold = (
            155,
            111,
            42,
            180,
        )

        glow_gold = (
            244,
            211,
            126,
            55,
        )

        # ==================================================
        # DIMENSIONS
        # ==================================================

        half_width = width // 2

        main_line_width = 2
        secondary_line_width = 1

        # Central ornament
        center_diamond = 9

        # Side ornaments
        side_diamond = 4

        # Distance from center ornament
        ornament_gap = 24

        # ==================================================
        # SUBTLE GLOW
        # ==================================================

        glow_half_width = half_width + 10

        draw.line(
            (
                center_x - glow_half_width,
                y,
                center_x + glow_half_width,
                y,
            ),
            fill=glow_gold,
            width=5,
        )

        # ==================================================
        # MAIN LEFT LINE
        # ==================================================

        left_start = (
            center_x
            - half_width
        )

        left_end = (
            center_x
            - ornament_gap
        )

        draw.line(
            (
                left_start,
                y,
                left_end,
                y,
            ),
            fill=light_gold,
            width=main_line_width,
        )

        # ==================================================
        # MAIN RIGHT LINE
        # ==================================================

        right_start = (
            center_x
            + ornament_gap
        )

        right_end = (
            center_x
            + half_width
        )

        draw.line(
            (
                right_start,
                y,
                right_end,
                y,
            ),
            fill=light_gold,
            width=main_line_width,
        )

        # ==================================================
        # SECONDARY INNER LINES
        # ==================================================

        inner_offset = 5

        draw.line(
            (
                left_start + 20,
                y + inner_offset,
                left_end - 8,
                y + inner_offset,
            ),
            fill=dark_gold,
            width=secondary_line_width,
        )

        draw.line(
            (
                right_start + 8,
                y + inner_offset,
                right_end - 20,
                y + inner_offset,
            ),
            fill=dark_gold,
            width=secondary_line_width,
        )

        # ==================================================
        # CENTER DIAMOND
        # ==================================================

        draw.polygon(
            [
                (
                    center_x,
                    y - center_diamond,
                ),
                (
                    center_x + center_diamond,
                    y,
                ),
                (
                    center_x,
                    y + center_diamond,
                ),
                (
                    center_x - center_diamond,
                    y,
                ),
            ],
            fill=bright_gold,
        )

        # ==================================================
        # CENTER DIAMOND INNER DETAIL
        # ==================================================

        inner_diamond = 4

        draw.polygon(
            [
                (
                    center_x,
                    y - inner_diamond,
                ),
                (
                    center_x + inner_diamond,
                    y,
                ),
                (
                    center_x,
                    y + inner_diamond,
                ),
                (
                    center_x - inner_diamond,
                    y,
                ),
            ],
            fill=(
                255,
                232,
                160,
                255,
            ),
        )

        # ==================================================
        # LEFT SIDE DIAMOND
        # ==================================================

        left_ornament_x = (
            center_x
            - ornament_gap
        )

        draw.polygon(
            [
                (
                    left_ornament_x,
                    y - side_diamond,
                ),
                (
                    left_ornament_x + side_diamond,
                    y,
                ),
                (
                    left_ornament_x,
                    y + side_diamond,
                ),
                (
                    left_ornament_x - side_diamond,
                    y,
                ),
            ],
            fill=bright_gold,
        )

        # ==================================================
        # RIGHT SIDE DIAMOND
        # ==================================================

        right_ornament_x = (
            center_x
            + ornament_gap
        )

        draw.polygon(
            [
                (
                    right_ornament_x,
                    y - side_diamond,
                ),
                (
                    right_ornament_x + side_diamond,
                    y,
                ),
                (
                    right_ornament_x,
                    y + side_diamond,
                ),
                (
                    right_ornament_x - side_diamond,
                    y,
                ),
            ],
            fill=bright_gold,
        )

        # ==================================================
        # SMALL OUTER DOTS
        # ==================================================

        dot_radius = 2

        dot_gap = 48

        left_dot_x = (
            center_x
            - dot_gap
        )

        right_dot_x = (
            center_x
            + dot_gap
        )

        draw.ellipse(
            (
                left_dot_x - dot_radius,
                y - dot_radius,
                left_dot_x + dot_radius,
                y + dot_radius,
            ),
            fill=bright_gold,
        )

        draw.ellipse(
            (
                right_dot_x - dot_radius,
                y - dot_radius,
                right_dot_x + dot_radius,
                y + dot_radius,
            ),
            fill=bright_gold,
        )

    # =========================================================
    # FONT HELPERS
    # =========================================================

    def _find_font(
        self,
        filenames,
    ):

        return self._find_font_in_folder(
            self.fonts_folder,
            filenames,
        )

    def _find_font_in_folder(
        self,
        folder: Path,
        filenames,
    ):

        folder = Path(folder)

        if not folder.exists():
            return None

        for filename in filenames:

            path = folder / filename

            if path.exists():

                return path

        return None

    # =========================================================
    # NEW DEVNAGARI FONT
    # =========================================================

    def _draw_centered_devanagari(
        self,
        draw,
        text: str,
        font,
        y: int,
        fill,
        shadow=True,
        shadow_offset=3,
    ):
        """
        Proper Devanagari/Sanskrit renderer.

        Uses Pillow RAQM layout engine, which provides
        HarfBuzz shaping and FriBiDi support.
        """

        if not text:
            return

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
            anchor="lt",
            direction="ltr",
            language="hi",
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        text_x = (
            self.WIDTH - text_width
        ) // 2

        if shadow:

            draw.text(
                (
                    text_x + shadow_offset,
                    y + shadow_offset,
                ),
                text,
                font=font,
                fill=(
                    0,
                    0,
                    0,
                    220,
                ),
                anchor="lt",
                direction="ltr",
                language="hi",
            )

        draw.text(
            (
                text_x,
                y,
            ),
            text,
            font=font,
            fill=fill,
            anchor="lt",
            direction="ltr",
            language="hi",
        )



    # =========================================================
    # LOAD FONT
    # =========================================================

    def _font(
        self,
        size: int,
        bold: bool = False,
    ) -> ImageFont.FreeTypeFont:

        path = (
            self.devanagari_bold_font
            if bold
            else self.devanagari_font
        )

        return ImageFont.truetype(
            str(path),
            size,
            layout_engine=ImageFont.Layout.RAQM,
        )

    # =========================================================
    # FIT IMAGE
    # =========================================================

    def _fit_image(
        self,
        image: Image.Image,
        scene_number: int = 1,
    ) -> Image.Image:

        image = image.convert("RGB")

        mode = self.SCENE_IMAGE_MODE.get(
            scene_number,
            "crop",
        )

        target_ratio = (
            self.WIDTH / self.HEIGHT
        )

        image_ratio = (
            image.width / image.height
        )

        # =====================================================
        # FIT MODE
        # =====================================================
        #
        # Preserve the COMPLETE original image.
        #
        # Used for Scene 3 because both Arjuna and Krishna
        # need to remain visible.
        #
        # =====================================================

        if mode == "fit":

            # Create blurred background
            background = image.copy()

            # Scale background to completely fill
            # the 1080x1920 canvas.
            background_ratio = (
                self.WIDTH / self.HEIGHT
            )

            if background.width / background.height > background_ratio:

                bg_height = self.HEIGHT

                bg_width = int(
                    bg_height
                    * background.width
                    / background.height
                )

            else:

                bg_width = self.WIDTH

                bg_height = int(
                    bg_width
                    * background.height
                    / background.width
                )

            background = background.resize(
                (
                    bg_width,
                    bg_height,
                ),
                Image.Resampling.LANCZOS,
            )

            # Center crop background
            left = max(
                0,
                (bg_width - self.WIDTH) // 2,
            )

            top = max(
                0,
                (bg_height - self.HEIGHT) // 2,
            )

            background = background.crop(
                (
                    left,
                    top,
                    left + self.WIDTH,
                    top + self.HEIGHT,
                )
            )

            # Blur background
            from PIL import ImageFilter

            background = background.filter(
                ImageFilter.GaussianBlur(
                    radius=30
                )
            )

            # Slightly darken background
            from PIL import ImageEnhance

            background = ImageEnhance.Brightness(
                background
            ).enhance(0.45)

            # =================================================
            # Foreground - preserve COMPLETE image
            # =================================================

            foreground = image.copy()

            foreground.thumbnail(
                (
                    self.WIDTH,
                    self.HEIGHT,
                ),
                Image.Resampling.LANCZOS,
            )

            # Center foreground
            x = (
                self.WIDTH
                - foreground.width
            ) // 2

            y = (
                self.HEIGHT
                - foreground.height
            ) // 2

            background.paste(
                foreground,
                (
                    x,
                    y,
                ),
            )

            return background

        # =====================================================
        # CROP MODE
        # =====================================================

        if image_ratio > target_ratio:

            new_width = int(
                image.height
                * target_ratio
            )

            max_left = (
                image.width
                - new_width
            )

            focus = self.IMAGE_FOCUS.get(
                scene_number,
                0.50,
            )

            left = int(
                max_left
                * focus
            )

            image = image.crop(
                (
                    left,
                    0,
                    left + new_width,
                    image.height,
                )
            )

        elif image_ratio < target_ratio:

            new_height = int(
                image.width
                / target_ratio
            )

            max_top = (
                image.height
                - new_height
            )

            top = int(
                max_top
                * 0.50
            )

            image = image.crop(
                (
                    0,
                    top,
                    image.width,
                    top + new_height,
                )
            )

        # Final resize
        image = image.resize(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            Image.Resampling.LANCZOS,
        )

        return image



    # =========================================================
    # CINEMATIC GRADIENT
    # =========================================================

    def _add_gradient(
        self,
        image: Image.Image,
    ) -> Image.Image:

        overlay = Image.new(
            "RGBA",
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            (
                0,
                0,
                0,
                0,
            ),
        )

        draw = ImageDraw.Draw(
            overlay
        )

        # -----------------------------------------------------
        # Top gradient
        # -----------------------------------------------------

        top_height = 900

        for y in range(
            top_height
        ):

            progress = (
                y
                / top_height
            )

            strength = int(
                125
                * (1 - progress)
            )

            draw.line(
                (
                    0,
                    y,
                    self.WIDTH,
                    y,
                ),
                fill=(
                    0,
                    0,
                    0,
                    strength,
                ),
            )

        # -----------------------------------------------------
        # Bottom gradient
        #
        # Stronger because subtitles will be placed here.
        # -----------------------------------------------------

        bottom_start = 1250

        for y in range(
            bottom_start,
            self.HEIGHT,
        ):

            progress = (
                y - bottom_start
            ) / (
                self.HEIGHT
                - bottom_start
            )

            strength = int(
                175
                * progress
            )

            draw.line(
                (
                    0,
                    y,
                    self.WIDTH,
                    y,
                ),
                fill=(
                    0,
                    0,
                    0,
                    strength,
                ),
            )

        return Image.alpha_composite(
            image.convert("RGBA"),
            overlay,
        )

    # =========================================================
    # CENTER TEXT
    # =========================================================

    def _draw_centered_text(
        self,
        draw,
        text,
        font,
        y,
        fill,
        stroke_width=2,
        stroke_fill=(35, 20, 5, 230),
    ):

        bbox = draw.textbbox(
            (
                0,
                0,
            ),
            text,
            font=font,
        )

        width = (
            bbox[2]
            - bbox[0]
        )

        x = (
            self.WIDTH
            - width
        ) // 2

        draw.text(
            (
                x,
                y,
            ),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )


    # =========================================================
    # MAIN COMPOSE
    # =========================================================

    def compose(
        self,
        image_file: Path,
        output_file: Path,
        shloka: str,
        chapter: int,
        verse: int,
        scene_number: int,
        show_shloka: bool | None = None,
    ) -> Path:
        """
        Compose one scene image.

        SBG V3 layout:

            Scene 1
                - Brand
                - Chapter / Verse
                - Decorative divider
                - Full Shloka panel
                - Bottom devotional mark

            Scenes 2-4
                - Brand
                - Chapter / Verse
                - Decorative divider
                - NO shloka panel
                - Bottom devotional mark

        If show_shloka is not explicitly supplied:
            Scene 1 -> shloka shown
            Scene 2-4 -> shloka hidden
        """

        image_file = Path(image_file)
        output_file = Path(output_file)

        # -----------------------------------------------------
        # Validate image
        # -----------------------------------------------------

        if not image_file.exists():
            raise FileNotFoundError(
                f"Scene image not found:\n"
                f"{image_file}"
            )

        # -----------------------------------------------------
        # Validate shloka
        # -----------------------------------------------------

        shloka = (
            ""
            if shloka is None
            else str(shloka).strip()
        )

        # -----------------------------------------------------
        # Automatically determine shloka visibility
        # -----------------------------------------------------

        if show_shloka is None:
            show_shloka = (
                scene_number == 1
            )

        # -----------------------------------------------------
        # Output folder
        # -----------------------------------------------------

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # =====================================================
        # LOAD
        # =====================================================

        image = Image.open(
            image_file
        )

        # =====================================================
        # RESIZE
        # =====================================================

        image = self._fit_image(
            image,
            scene_number=scene_number,
        )

        # =====================================================
        # CINEMATIC GRADIENT
        # =====================================================

        image = self._add_gradient(
            image
        )

        if image is None:
            raise ValueError(
                f"Scene {scene_number}: "
                f"image is None before drawing."
            )

        draw = ImageDraw.Draw(
            image
        )

        # =====================================================
        # BRAND
        # =====================================================

        brand_font = self._font(
            58,
            bold=True,
        )

        self._draw_centered_devanagari(
            draw,
            "श्रीमद्भगवद्गीता",
            brand_font,
            self.BRAND_Y,
            self.LIGHT_GOLD,
        )

        # =====================================================
        # CHAPTER / VERSE
        # =====================================================

        chapter_font = self._font(
            42,
            bold=True,
        )

        self._draw_centered_devanagari(
            draw,
            f"अध्याय {chapter}  •  श्लोक {verse}",
            chapter_font,
            self.CHAPTER_Y,
            self.LIGHT_GOLD,
        )

        # =====================================================
        # DECORATIVE DIVIDER
        # =====================================================

        self._draw_decorative_divider(
            draw,
            center_x=self.WIDTH // 2,
            y=self.DECORATIVE_LINE_Y + 20,
            width=400,
        )

        # =====================================================
        # SHLOKA
        #
        # IMPORTANT:
        # Only Scene 1 gets the full shloka panel by default.
        # =====================================================

        # show_shloka = False

        if show_shloka and shloka:

            image = self._draw_shloka_panel(
                image,
                shloka,
            )

            if image is None:
                raise ValueError(
                    f"Scene {scene_number}: "
                    f"image is None after shloka panel."
                )

            draw = ImageDraw.Draw(
                image
            )

        # =====================================================
        # BOTTOM DEVOTIONAL MARK
        # =====================================================

        bottom_font = self._font(
            self.BOTTOM_SIZE
        )

        bottom_text = "॥ हरिः ॐ ॥"

        bbox = draw.textbbox(
            (0, 0),
            bottom_text,
            font=bottom_font,
        )

        bottom_width = (
            bbox[2] - bbox[0]
        )

        bottom_x = (
            self.WIDTH - bottom_width
        ) // 2

        draw.text(
            (
                bottom_x,
                self.BOTTOM_MARK_Y,
            ),
            bottom_text,
            font=bottom_font,
            fill=(
                245,
                211,
                130,
                210,
            ),
            stroke_width=2,
            stroke_fill=(
                30,
                15,
                5,
                200,
            ),
        )

        # =====================================================
        # SAVE
        # =====================================================

        image = image.convert(
            "RGB"
        )

        image.save(
            output_file,
            format="PNG",
        )

        print(
            "✓ Composed scene image:"
        )

        print(
            f"  {output_file}"
        )

        return output_file
    

    # =========================================================
    # COMPOSE ALL FOUR SCENES
    # =========================================================

    def compose_scenes(
        self,
        scene_images,
        output_folder: Path,
        shloka: str,
        chapter: int,
        verse: int,
    ):

        output_folder = Path(
            output_folder
        )

        if len(scene_images) != 4:

            raise ValueError(
                "Exactly 4 scene images are required."
            )

        results = []

        for index, image_file in enumerate(
            scene_images,
            start=1,
        ):

            image_file = Path(
                image_file
            )

            scene_folder = (
                output_folder
                / f"scene{index}"
            )

            scene_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_file = (
                scene_folder
                / f"scene{index}_composed.png"
            )

            result = self.compose(
                image_file=image_file,
                output_file=output_file,
                shloka=shloka,
                chapter=chapter,
                verse=verse,
                scene_number=index,
            )

            results.append(
                result
            )

        return results