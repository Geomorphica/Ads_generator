"""Text formatting helpers for Geomorphica social ads."""

from __future__ import annotations

from collections.abc import Callable

from PIL import ImageFont


def format_author_line(
    last_name: str,
    year: str | int,
    *,
    author_mode: str = "et_al",
    second_last: str = "",
) -> str:
    """Format the author line from mode.

    - ``single`` → ``Lastname (year)``
    - ``two`` → ``Lastname1 & Lastname2 (year)``
    - ``et_al`` (default, >3 authors) → ``Lastname et al. (year)``

    Names keep the casing the user typed.
    """
    name = (last_name or "").strip() or "Author"
    year_s = str(year).strip()
    mode = (author_mode or "et_al").strip().lower()

    if mode in ("single", "one", "1"):
        return f"{name} ({year_s})"
    if mode in ("two", "2"):
        second = (second_last or "").strip() or "Author"
        return f"{name} & {second} ({year_s})"
    return f"{name} et al. ({year_s})"


def _safe_name_part(text: str) -> str:
    """Filesystem-safe token: strip, spaces→_, drop odd characters."""
    s = (text or "").strip().replace(" ", "_")
    keep = []
    for ch in s:
        if ch.isalnum() or ch in ("_", "-", "."):
            keep.append(ch)
    return "".join(keep) or "Author"


def output_basename(
    last_name: str,
    year: str | int,
    *,
    author_mode: str = "et_al",
    second_last: str = "",
) -> str:
    """Return stem like ``Shugar_2026_ads`` / ``Grom_Forte_2026_ads`` / ``Sumaiya_etal_2024_ads``."""
    a = _safe_name_part(last_name)
    y = _safe_name_part(str(year))
    mode = (author_mode or "et_al").strip().lower()
    if mode in ("single", "one", "1"):
        return f"{a}_{y}_ads"
    if mode in ("two", "2"):
        b = _safe_name_part(second_last)
        return f"{a}_{b}_{y}_ads"
    return f"{a}_etal_{y}_ads"


def format_title(title: str) -> str:
    """Apply journal-style title case.

    Capitalize major words; keep short articles / prepositions /
    coordinating conjunctions lowercase (e.g. of, the, on, and), except
    when they are the first or last word of the title or of a ``:`` subtitle.
    Hyphenated parts are cased separately. All-caps tokens (e.g. USA) are kept.
    """
    text = (title or "").strip()
    if not text:
        return text

    # Split on colons so each subtitle segment gets its own first/last rules
    segments = text.split(":")
    return ":".join(_title_case_segment(seg) for seg in segments)


def _title_case_segment(segment: str) -> str:
    """Title-case one colon-separated segment, preserving leading/trailing space."""
    if not segment.strip():
        return segment

    leading = segment[: len(segment) - len(segment.lstrip())]
    trailing = segment[len(segment.rstrip()) :]
    core = segment.strip()
    words = core.split()
    if not words:
        return segment

    last_i = len(words) - 1
    out: list[str] = []
    for i, word in enumerate(words):
        force = i == 0 or i == last_i
        out.append(_title_case_token(word, force_cap=force))
    return leading + " ".join(out) + trailing


def _title_case_token(token: str, *, force_cap: bool) -> str:
    """Title-case one whitespace-separated token (may include hyphen/punct)."""
    if "-" in token:
        parts = token.split("-")
        # First/last hyphen part: force cap if whole token is forced, or
        # always cap non-small parts; small mid-parts stay lower unless forced.
        cased: list[str] = []
        for j, part in enumerate(parts):
            part_force = force_cap or j == 0 or j == len(parts) - 1
            # Mid hyphen pieces still follow small-word rule unless forced
            if j not in (0, len(parts) - 1):
                part_force = force_cap
            cased.append(_title_case_atomic(part, force_cap=part_force))
        return "-".join(cased)
    return _title_case_atomic(token, force_cap=force_cap)


def _title_case_atomic(token: str, *, force_cap: bool) -> str:
    """Title-case a single atomic word, keeping leading/trailing punctuation."""
    if not token:
        return token

    start = 0
    end = len(token)
    while start < end and not token[start].isalnum():
        start += 1
    while end > start and not token[end - 1].isalnum():
        end -= 1
    if start >= end:
        return token

    prefix, core, suffix = token[:start], token[start:end], token[end:]
    if not core:
        return token

    # Preserve acronyms / all-caps short forms (USA, GIS, …)
    if len(core) > 1 and core.isupper():
        return prefix + core + suffix

    lower = core.lower()
    if not force_cap and lower in _TITLE_SMALL_WORDS:
        return prefix + lower + suffix

    # Capitalize first alphanumeric; lower the rest (ASCII-friendly)
    chars = list(lower)
    for k, ch in enumerate(chars):
        if ch.isalpha():
            chars[k] = ch.upper()
            break
    return prefix + "".join(chars) + suffix


# Short function words left lowercase mid-title (APA-style journal titles:
# capitalize major words and longer prepositions like During / Between).
_TITLE_SMALL_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "but",
        "or",
        "nor",
        "for",
        "so",
        "yet",
        "as",
        "at",
        "by",
        "in",
        "of",
        "on",
        "to",
        "up",
        "via",
        "per",
        "vs",
        "vs.",
        "v",
        "v.",
        "from",
        "into",
        "onto",
        "with",
        "over",
        "off",
        "out",
        "than",
        "if",
        "that",
    }
)


def format_vol_issue(volume: str | int, issue: str | int) -> str:
    """Return e.g. ``VOL 2 | NO 1``."""
    return f"VOL {str(volume).strip()} | NO {str(issue).strip()}"


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    """Wrap ``text`` into lines that fit ``max_width`` pixels."""
    text = (text or "").strip()
    if not text:
        return []

    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.getlength(trial) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        # Hard-break a single oversized word
        if font.getlength(word) <= max_width:
            current = word
        else:
            chunk = ""
            for ch in word:
                trial_ch = chunk + ch
                if chunk and font.getlength(trial_ch) > max_width:
                    lines.append(chunk)
                    chunk = ch
                else:
                    chunk = trial_ch
            current = chunk

    if current:
        lines.append(current)
    return lines


def has_single_word_orphan(lines: list[str]) -> bool:
    """True if any wrapped line is exactly one word (and there is more than one line)."""
    if len(lines) <= 1:
        return False
    return any(len(line.split()) == 1 for line in lines)


def fit_wrapped_title(
    text: str,
    max_width: int,
    font_loader: Callable[[int], ImageFont.FreeTypeFont],
    base_size: int,
    size_delta: int = 4,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Wrap title, nudging font size so no single-word orphan line remains.

    Tries ``base_size``, then ``base_size±1…±size_delta`` (preferring sizes
    closer to base; when tied, prefer larger). Falls back to the base wrap
    if no size in range clears orphans.

    Returns ``(font, lines, chosen_size)``.
    """
    text = (text or "").strip()
    if not text:
        font = font_loader(base_size)
        return font, [], base_size

    # Prefer base, then larger, then smaller at each step away from base
    candidates: list[int] = [base_size]
    for d in range(1, size_delta + 1):
        candidates.append(base_size + d)
        candidates.append(base_size - d)

    base_font = font_loader(base_size)
    base_lines = wrap_text(text, base_font, max_width)
    best: tuple[ImageFont.FreeTypeFont, list[str], int] | None = None

    for size in candidates:
        if size < 12:
            continue
        font = font_loader(size)
        lines = wrap_text(text, font, max_width)
        if not lines:
            continue
        if not has_single_word_orphan(lines):
            return font, lines, size
        if best is None and size == base_size:
            best = (font, lines, size)

    if best is not None:
        return best
    return base_font, base_lines, base_size
