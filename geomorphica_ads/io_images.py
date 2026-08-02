"""Load uploaded graphic abstracts into Pillow images."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PIL import Image

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def load_graphic_abstract(
    source: str | Path | BinaryIO | bytes,
    filename: str | None = None,
) -> Image.Image:
    """Open an image as RGBA.

    GIF: use the first frame only. Accepts a path, file-like object, or bytes.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        _check_extension(path.suffix)
        img = Image.open(path)
    elif isinstance(source, bytes):
        if filename:
            _check_extension(Path(filename).suffix)
        img = Image.open(BytesIO(source))
    else:
        # file-like (e.g. Streamlit UploadedFile)
        if filename:
            _check_extension(Path(filename).suffix)
        elif hasattr(source, "name"):
            _check_extension(Path(str(source.name)).suffix)
        img = Image.open(source)

    # Animated GIF / multi-frame: stay on frame 0
    try:
        img.seek(0)
    except EOFError:
        pass

    return img.convert("RGBA")


def _check_extension(suffix: str) -> None:
    ext = suffix.lower()
    if ext and ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(
            f"Unsupported file type '{ext}'. Please upload one of: {allowed}."
        )
