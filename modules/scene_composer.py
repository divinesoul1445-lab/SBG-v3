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
        shloka,
    ):
        """
        Premium Sanskrit Shloka panel.

        Uses the existing RAQM-enabled Devanagari renderer.
        """

        draw = ImageDraw.Draw(
            image,
            "RGBA",
        )

        # ==================================================
        # PANEL GEOMETRY
        # ==================================================

        panel_margin_x = int(
            self.WIDTH * 0.11
        )

        panel_width = (
            self.WIDTH
            - (panel_margin_x * 2)
        )

        panel_top = int(
            self.HEIGHT * 0.55
        )

        panel_bottom = int(
            self.HEIGHT * 0.70
        )

        radius = 32

        # ==================================================
        # COLORS
        # ==================================================

        panel_fill = (
            20,
            14,
            8,
            225,
        )

        outer_gold = (
            214,
            174,
            82,
            245,
        )

        bright_gold = (
            244,
            211,
            126,
            255,
        )

        inner_gold = (
            166,
            123,
            48,
            180,
        )

        shadow = (
            0,
            0,
            0,
            130,
        )

        # ==================================================
        # SOFT PANEL SHADOW
        # ==================================================

        shadow_offset = 8

        draw.rounded_rectangle(
            (
                panel_margin_x + shadow_offset,
                panel_top + shadow_offset,
                panel_margin_x
                + panel_width
                + shadow_offset,
                panel_bottom + shadow_offset,
            ),
            radius=radius,
            fill=shadow,
        )

        # ==================================================
        # MAIN PANEL
        # ==================================================

        draw.rounded_rectangle(
            (
                panel_margin_x,
                panel_top,
                panel_margin_x + panel_width,
                panel_bottom,
            ),
            radius=radius,
            fill=panel_fill,
            outline=outer_gold,
            width=4,
        )

        # ==================================================
        # INNER BORDER
        # ==================================================

        inner_padding = 10

        draw.rounded_rectangle(
            (
                panel_margin_x + inner_padding,
                panel_top + inner_padding,
                panel_margin_x
                + panel_width
                - inner_padding,
                panel_bottom - inner_padding,
            ),
            radius=radius - inner_padding,
            outline=inner_gold,
            width=2,
        )

        # ==================================================
        # TOP DECORATIVE LINE
        # ==================================================

        center_x = self.WIDTH // 2

        ornament_y = panel_top + 32

        line_width = 115

        draw.line(
            (
                center_x - line_width,
                ornament_y,
                center_x - 22,
                ornament_y,
            ),
            fill=inner_gold,
            width=2,
        )

        draw.line(
            (
                center_x + 22,
                ornament_y,
                center_x + line_width,
                ornament_y,
            ),
            fill=inner_gold,
            width=2,
        )

        # ==================================================
        # CENTER DIAMOND
        # ==================================================

        diamond_size = 9

        draw.polygon(
            [
                (
                    center_x,
                    ornament_y - diamond_size,
                ),
                (
                    center_x + diamond_size,
                    ornament_y,
                ),
                (
                    center_x,
                    ornament_y + diamond_size,
                ),
                (
                    center_x - diamond_size,
                    ornament_y,
                ),
            ],
            fill=bright_gold,
        )

        # ==================================================
        # SHLOKA HEADING
        # ==================================================

        heading_font = self._font(
            38,
            bold=True,
        )

        heading_y = (
            panel_top + 48
        )

        self._draw_centered_devanagari(
            draw,
            "श्लोक",
            heading_font,
            heading_y,
            bright_gold,
            shadow=True,
        )

        # ==================================================
        # SHLOKA TEXT
        # ==================================================

        shloka_font = self._font(
            34,
            bold=False,
        )

        # --------------------------------------------------
        # Normalize input
        # --------------------------------------------------

        if shloka is None:
            return

        shloka = str(
            shloka
        ).strip()

        if not shloka:
            return

        # --------------------------------------------------
        # Split into lines
        # --------------------------------------------------

        lines = [
            line.strip()
            for line in shloka.splitlines()
            if line.strip()
        ]

        # If the source is one long line, wrap it.
        if len(lines) == 1:

            words = lines[0].split()

            wrapped = []

            current = ""

            max_chars = 42

            for word in words:

                test = (
                    word
                    if not current
                    else current + " " + word
                )

                if len(test) <= max_chars:

                    current = test

                else:

                    if current:
                        wrapped.append(
                            current
                        )

                    current = word

            if current:
                wrapped.append(
                    current
                )

            lines = wrapped

        # ==================================================
        # TEXT AREA
        # ==================================================

        text_area_top = (
            panel_top + 105
        )

        text_area_bottom = (
            panel_bottom - 38
        )

        available_height = (
            text_area_bottom
            - text_area_top
        )

        # ==================================================
        # LINE SPACING
        # ==================================================

        line_spacing = 12

        bbox = draw.textbbox(
            (0, 0),
            "अ",
            font=shloka_font,
            anchor="lt",
            direction="ltr",
            language="hi",
        )

        line_height = (
            bbox[3] - bbox[1]
        )

        total_height = (
            len(lines) * line_height
            + (len(lines) - 1)
            * line_spacing
        )

        # ==================================================
        # AUTO-SCALE IF NEEDED
        # ==================================================

        if total_height > available_height:

            shloka_font = self._font(
                29,
                bold=False,
            )

            bbox = draw.textbbox(
                (0, 0),
                "अ",
                font=shloka_font,
                anchor="lt",
                direction="ltr",
                language="hi",
            )

            line_height = (
                bbox[3] - bbox[1]
            )

            total_height = (
                len(lines) * line_height
                + (len(lines) - 1)
                * line_spacing
            )

        # ==================================================
        # CENTER TEXT BLOCK VERTICALLY
        # ==================================================

        start_y = (
            text_area_top
            + (
                available_height
                - total_height
            ) // 2
        )

        # ==================================================
        # DRAW EACH LINE
        # ==================================================

        for line in lines:

            bbox = draw.textbbox(
                (0, 0),
                line,
                font=shloka_font,
                anchor="lt",
                direction="ltr",
                language="hi",
            )

            line_width = (
                bbox[2] - bbox[0]
            )

            x = (
                self.WIDTH
                - line_width
            ) // 2

            # ----------------------------------------------
            # Shadow
            # ----------------------------------------------

            draw.text(
                (
                    x + 2,
                    start_y + 3,
                ),
                line,
                font=shloka_font,
                fill=(
                    0,
                    0,
                    0,
                    210,
                ),
                anchor="lt",
                direction="ltr",
                language="hi",
            )

            # ----------------------------------------------
            # Sanskrit
            # ----------------------------------------------

            draw.text(
                (
                    x,
                    start_y,
                ),
                line,
                font=shloka_font,
                fill=(
                    248,
                    240,
                    218,
                    255,
                ),
                anchor="lt",
                direction="ltr",
                language="hi",
            )

            start_y += (
                line_height
                + line_spacing
            )

        # ==================================================
        # BOTTOM ORNAMENT
        # ==================================================

        ornament_y = (
            panel_bottom - 24
        )

        line_width = 85

        draw.line(
            (
                center_x - line_width,
                ornament_y,
                center_x - 16,
                ornament_y,
            ),
            fill=inner_gold,
            width=2,
        )

        draw.line(
            (
                center_x + 16,
                ornament_y,
                center_x + line_width,
                ornament_y,
            ),
            fill=inner_gold,
            width=2,
        )

        diamond_size = 6

        draw.polygon(
            [
                (
                    center_x,
                    ornament_y - diamond_size,
                ),
                (
                    center_x + diamond_size,
                    ornament_y,
                ),
                (
                    center_x,
                    ornament_y + diamond_size,
                ),
                (
                    center_x - diamond_size,
                    ornament_y,
                ),
            ],
            fill=bright_gold,
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
        show_shloka: bool = True,
    ) -> Path:

        image_file = Path(
            image_file
        )

        output_file = Path(
            output_file
        )

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

        # =====================================================
        # DRAW
        # =====================================================

        if image is None:
            raise ValueError(
                f"Scene {scene_number}: image is None before drawing."
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

        footer_font = self._font(
            36,
            bold=True,
        )
        # =====================================================
        # DECORATIVE LINE
        # =====================================================

        line_width = 230

        line_x1 = (
            self.WIDTH
            - line_width
        ) // 2

        line_x2 = (
            line_x1
            + line_width
        )

        self._draw_decorative_divider(
            draw,
            center_x=self.WIDTH // 2,
            y=self.DECORATIVE_LINE_Y + 20,
            width=400,
            )
        

        # =====================================================
        # SHLOKA
        # =====================================================

        if show_shloka and shloka:

            image = (
                self._draw_shloka_panel(
                    image,
                    shloka,
                )
            )

            if image is None:
                raise ValueError(
                    f"Scene {scene_number}: image is None before drawing."
                )

            draw = ImageDraw.Draw(
                image
            )



        # =====================================================
        # BOTTOM DEVOTIONAL MARK
        #
        # Positioned ABOVE the subtitle safe zone.
        # =====================================================

        bottom_font = self._font(
            self.BOTTOM_SIZE
        )

        bottom_text = "॥ हरिः ॐ ॥"

        bbox = draw.textbbox(
            (
                0,
                0,
            ),
            bottom_text,
            font=bottom_font,
        )

        bottom_width = (
            bbox[2]
            - bbox[0]
        )

        bottom_x = (
            self.WIDTH
            - bottom_width
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
            f"✓ Composed scene image:"
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