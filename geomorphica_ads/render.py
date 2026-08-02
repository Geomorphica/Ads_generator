"""Compose Geomorphica social-media ad images."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .text_utils import (
    fit_wrapped_title,
    format_author_line,
    format_title,
    format_vol_issue,
    wrap_text,
)

# Layout constants (pixels)
CANVAS_WIDTH = 1080
MIN_HEIGHT = 1000
MAX_HEIGHT = 1500
BRAND_BLUE = (27, 76, 148, 255)  # #1b4c94
WHITE = (255, 255, 255, 255)

SIDE_MARGIN = 36  # text column left/right inset (half of prior 72)
MIDDLE_BORDER = 8  # filled side borders on middle band (2× prior 4)
TOP_PAD = 28
BOTTOM_PAD = 16
GAP_AUTHOR_TITLE = 8
GAP_AFTER_TITLE = 20
MIDDLE_V_PAD = 20
LOGO_MAX_WIDTH = 520  # 2/3 of prior 780; bottom band shrinks with logo
AUTHOR_FONT_SIZE = 50
TITLE_FONT_SIZE = 36
VOL_FONT_SIZE = 22
LINE_SPACING = 1.25
TITLE_SIZE_DELTA = 4

_ROOT = Path(__file__).resolve().parent.parent
_ASSETS = _ROOT / "assets"
_FONTS = _ASSETS / "fonts"
_LOGO_DIR = _ROOT / "logo"
_LOGO_WHITE = _LOGO_DIR / "Logo_large_w.png"
_LOGO_BLACK = _LOGO_DIR / "Logo_large_b.png"


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = _FONTS / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing font file: {path}. Bundle Roboto under assets/fonts/."
        )
    return ImageFont.truetype(str(path), size=size)


def _text_column_width() -> int:
    return CANVAS_WIDTH - 2 * SIDE_MARGIN


def _measure_wrapped(
    lines: list[str],
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int]:
    """Return (max_line_width, total_block_height)."""
    if not lines:
        return 0, 0
    widths = [int(font.getlength(line)) for line in lines]
    line_h = int(font.size * LINE_SPACING)
    return max(widths), line_h * len(lines)


def _fit_graphic(
    ga: Image.Image,
    max_w: int,
    max_h: int,
) -> Image.Image:
    """Scale GA to fit inside max_w × max_h, preserving aspect ratio."""
    if ga.width == 0 or ga.height == 0:
        return ga
    scale = min(max_w / ga.width, max_h / ga.height)
    new_w = max(1, int(ga.width * scale))
    new_h = max(1, int(ga.height * scale))
    return ga.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _palette(dark_theme: bool) -> dict[str, tuple[int, int, int, int] | Path]:
    """Colors and logo path for default vs dark (blue↔white swap)."""
    if dark_theme:
        return {
            "band": WHITE,
            "middle": BRAND_BLUE,
            "text": BRAND_BLUE,
            "border": WHITE,
            "logo": _LOGO_BLACK,
        }
    return {
        "band": BRAND_BLUE,
        "middle": WHITE,
        "text": WHITE,
        "border": BRAND_BLUE,
        "logo": _LOGO_WHITE,
    }


def render_ad(
    graphic: Image.Image,
    author_last: str,
    year: str | int,
    title: str,
    volume: str | int,
    issue: str | int,
    *,
    author_mode: str = "et_al",
    second_last: str = "",
    dark_theme: bool = False,
    return_image: bool = False,
) -> bytes | Image.Image:
    """Build the social ad PNG.

    Parameters
    ----------
    graphic :
        Graphic abstract as a Pillow image (RGBA preferred).
    author_last, year, title, volume, issue :
        Paper metadata fields.
    author_mode :
        ``single``, ``two``, or ``et_al`` (>3 authors, default).
    second_last :
        Second author last name when ``author_mode`` is ``two``.
    dark_theme :
        If True, swap blue↔white on bands/middle/borders/text and use
        the black wordmark.
    return_image :
        If True, return a Pillow Image instead of PNG bytes.
    """
    colors = _palette(dark_theme)
    band_color = colors["band"]
    middle_color = colors["middle"]
    text_color = colors["text"]
    border_color = colors["border"]
    logo_path = colors["logo"]

    author_font = _font("Roboto-Bold.ttf", AUTHOR_FONT_SIZE)
    vol_font = _font("Roboto-Bold.ttf", VOL_FONT_SIZE)

    col_w = _text_column_width()
    author_line = format_author_line(
        author_last,
        year,
        author_mode=author_mode,
        second_last=second_last,
    )
    title_line = format_title(title)
    vol_line = format_vol_issue(volume, issue)

    author_lines = wrap_text(author_line, author_font, col_w)
    title_font, title_lines, _ = fit_wrapped_title(
        title_line,
        col_w,
        lambda size: _font("Roboto-Light.ttf", size),
        TITLE_FONT_SIZE,
        TITLE_SIZE_DELTA,
    )

    _, author_h = _measure_wrapped(author_lines, author_font)
    _, title_h = _measure_wrapped(title_lines, title_font)

    content_h = (
        author_h
        + (GAP_AUTHOR_TITLE if title_lines else 0)
        + title_h
    )
    # Flexible top band: pad around content; vertically center the text block
    top_band_h = max(content_h + TOP_PAD * 2 + GAP_AFTER_TITLE // 2, content_h + 40)

    # Bottom band: logo only (VOL overlays logo top-right)
    logo = Image.open(logo_path).convert("RGBA")
    logo_scale = LOGO_MAX_WIDTH / logo.width
    logo_w = int(logo.width * logo_scale)
    logo_h = int(logo.height * logo_scale)
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

    bottom_band_h = BOTTOM_PAD + logo_h + BOTTOM_PAD

    # Remaining height budget for middle (figure) area
    fixed_chrome = top_band_h + bottom_band_h
    if graphic.mode != "RGBA":
        graphic = graphic.convert("RGBA")

    ideal_scale = col_w / graphic.width
    ideal_ga_h = int(graphic.height * ideal_scale)
    ideal_middle = MIDDLE_V_PAD * 2 + ideal_ga_h
    ideal_total = fixed_chrome + ideal_middle

    if ideal_total < MIN_HEIGHT:
        total_h = MIN_HEIGHT
    elif ideal_total > MAX_HEIGHT:
        total_h = MAX_HEIGHT
    else:
        total_h = ideal_total

    middle_h = total_h - fixed_chrome
    max_ga_h = max(40, middle_h - MIDDLE_V_PAD * 2)
    ga_fitted = _fit_graphic(graphic, col_w, max_ga_h)

    canvas = Image.new("RGBA", (CANVAS_WIDTH, total_h), middle_color)
    draw = ImageDraw.Draw(canvas)

    # --- Top band ---
    draw.rectangle((0, 0, CANVAS_WIDTH, top_band_h), fill=band_color)

    # Vertically center author+title block in the top band
    block_top = (top_band_h - content_h) // 2
    y = block_top
    for line in author_lines:
        draw.text((SIDE_MARGIN, y), line, font=author_font, fill=text_color)
        y += int(author_font.size * LINE_SPACING)
    if title_lines:
        y = block_top + author_h + GAP_AUTHOR_TITLE
        for line in title_lines:
            draw.text((SIDE_MARGIN, y), line, font=title_font, fill=text_color)
            y += int(title_font.size * LINE_SPACING)

    # --- Middle: GA centered in text column ---
    middle_top = top_band_h
    # Middle fill already set as canvas background; redraw band edges if needed
    draw.rectangle(
        (0, middle_top, CANVAS_WIDTH, middle_top + middle_h),
        fill=middle_color,
    )
    ga_x = SIDE_MARGIN + (col_w - ga_fitted.width) // 2
    ga_y = middle_top + (middle_h - ga_fitted.height) // 2
    canvas.alpha_composite(ga_fitted, (ga_x, ga_y))

    # Thin left/right borders on middle band
    draw.rectangle(
        (0, middle_top, MIDDLE_BORDER, middle_top + middle_h),
        fill=border_color,
    )
    draw.rectangle(
        (
            CANVAS_WIDTH - MIDDLE_BORDER,
            middle_top,
            CANVAS_WIDTH,
            middle_top + middle_h,
        ),
        fill=border_color,
    )

    # --- Bottom band ---
    bottom_top = total_h - bottom_band_h
    draw.rectangle((0, bottom_top, CANVAS_WIDTH, total_h), fill=band_color)

    logo_x = (CANVAS_WIDTH - logo_w) // 2
    logo_y = bottom_top + (bottom_band_h - logo_h) // 2
    canvas.alpha_composite(logo, (logo_x, logo_y))

    # VOL text: top-right of logo, overlaid on the wordmark
    vol_w = int(vol_font.getlength(vol_line))
    vol_x = logo_x + logo_w - vol_w
    vol_y = logo_y
    draw.text((vol_x, vol_y), vol_line, font=vol_font, fill=text_color)

    if return_image:
        return canvas.convert("RGB")

    buf = BytesIO()
    canvas.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()
