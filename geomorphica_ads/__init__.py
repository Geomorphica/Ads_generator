"""Geomorphica social-ad image builder."""

__all__ = ["render_ad"]


def __getattr__(name: str):
    if name == "render_ad":
        from .render import render_ad

        return render_ad
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
