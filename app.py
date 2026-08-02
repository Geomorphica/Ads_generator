"""Geomorphica social-ad generator (Streamlit)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from geomorphica_ads.io_images import ALLOWED_EXTENSIONS, load_graphic_abstract
from geomorphica_ads.render import render_ad
from geomorphica_ads.text_utils import output_basename

_ROOT = Path(__file__).resolve().parent
_LOGO_HEADER = _ROOT / "logo" / "Logo_large_b.png"
_OUTPUT_DIR = _ROOT / "output"

_AUTHOR_MODE_LABELS = {
    ">3 authors": "et_al",
    "2 authors": "two",
    "single author": "single",
}


def _doi_url(volume: str | int, issue: str | int, paper_number: str | int) -> str:
    """Build https://doi.org/10.59236/geomorphica.vXiY.ZZ."""
    return (
        "https://doi.org/10.59236/geomorphica."
        f"v{str(volume).strip()}i{str(issue).strip()}.{str(paper_number).strip()}"
    )


def _post_text(all_authors: str, caption: str, doi: str) -> str:
    return (
        "🚨 New Paper Alert! 🚨\n"
        "\n"
        f"Authors: {all_authors.strip()}\n"
        "\n"
        "🏔️ Graphic Abstract:\n"
        f"{caption.strip()}\n"
        "\n"
        f"🔗 Read now: {doi}\n"
    )


def _ensure_output_dir() -> Path:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return _OUTPUT_DIR


st.set_page_config(
    page_title="Geomorphica Ad Maker",
    layout="centered",
)

st.image(str(_LOGO_HEADER), width="stretch")
st.markdown(
    "<p style='text-align:center;font-weight:700;font-size:1.25rem;"
    "margin:0.25rem 0 0.15rem 0;'>social media ads generator</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='margin-top:0;text-align:center;font-size:0.85rem;font-weight:300;"
    "font-style:italic;color:#888;'>Created by Larry Syu-Heng Lai, "
    "August 2026</p>",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
Fill in the paper details, upload one figure, then generate a downloadable ad.

- **Authors:** >3 (default) → `Lastname et al. (year)`; 2 → `Name1 & Name2 (year)`;
  single → `Lastname (year)`.
- Names stay as typed. Title uses normal journal title case.
- Drag or browse one figure ({", ".join(sorted(ALLOWED_EXTENSIONS))}; GIF = first frame).
- **Dark theme** flips blue ↔ white on the ad only.
- Use **Generate ad figure** for the image, then **Generate ad texts** below for the social post + DOI (DOI uses volume/issue from the figure form).
- Files are also saved under `output/` (e.g. `Shugar_2026_ads.png` / `.txt`).
"""
)

dark_theme = st.toggle("Dark theme", value=False)

# Outside the form so the second-author field enables immediately
author_mode_label = st.radio(
    "Authors",
    options=list(_AUTHOR_MODE_LABELS.keys()),
    index=0,  # default >3 authors
    horizontal=True,
)
author_mode = _AUTHOR_MODE_LABELS[author_mode_label]
two_authors = author_mode == "two"

# Outside the form so drag-and-drop works reliably
uploaded = st.file_uploader(
    "Graphic abstract (one file)",
    type=[ext.lstrip(".") for ext in sorted(ALLOWED_EXTENSIONS)],
    accept_multiple_files=False,
)
st.caption("Drag and drop a file here, or browse. PNG, JPEG, WebP, or GIF (GIF = first frame).")

with st.form("ad_form"):
    if two_authors:
        a1, a2 = st.columns(2)
        with a1:
            author_last = st.text_input(
                "First author last name",
                placeholder="Shugar",
            )
        with a2:
            second_last = st.text_input(
                "Second author's last name",
                placeholder="Forte",
            )
    else:
        author_last = st.text_input(
            "First author last name",
            placeholder="Shugar",
        )
        second_last = ""

    ycol, vcol, icol = st.columns(3)
    with ycol:
        year = st.text_input("Year", placeholder="2024")
    with vcol:
        volume = st.text_input("Volume", placeholder="2")
    with icol:
        issue = st.text_input("Issue", placeholder="1")

    title = st.text_area(
        "Paper title",
        height=140,
        placeholder="The Geospatial Revolution in Geomorphological Research",
    )

    submitted = st.form_submit_button("Generate ad figure", type="primary")

if submitted:
    missing = []
    if not (author_last or "").strip():
        missing.append("first author last name")
    if two_authors and not (second_last or "").strip():
        missing.append("second author's last name")
    if not (year or "").strip():
        missing.append("year")
    if not (volume or "").strip():
        missing.append("volume")
    if not (issue or "").strip():
        missing.append("issue")
    if not (title or "").strip():
        missing.append("title")
    if uploaded is None:
        missing.append("graphic abstract")

    if missing:
        st.error("Please fill in: " + ", ".join(missing) + ".")
    else:
        try:
            graphic = load_graphic_abstract(uploaded, filename=uploaded.name)
            png_bytes = render_ad(
                graphic,
                author_last=author_last,
                year=year,
                title=title,
                volume=volume,
                issue=issue,
                author_mode=author_mode,
                second_last=second_last if two_authors else "",
                dark_theme=dark_theme,
            )
        except Exception as exc:  # noqa: BLE001 — show to user
            st.error(f"Could not build the ad: {exc}")
        else:
            stem = output_basename(
                author_last,
                year,
                author_mode=author_mode,
                second_last=second_last if two_authors else "",
            )
            out_dir = _ensure_output_dir()
            png_path = out_dir / f"{stem}.png"
            png_path.write_bytes(png_bytes)

            st.session_state["ad_ready"] = {
                "png": png_bytes,
                "year": str(year).strip(),
                "volume": str(volume).strip(),
                "issue": str(issue).strip(),
                "author_mode": author_mode,
                "author_last": (author_last or "").strip(),
                "second_last": (second_last or "").strip() if two_authors else "",
                "stem": stem,
                "file_name": f"{stem}.png",
                "png_path": str(png_path),
            }
            st.success(f"Ad figure ready. Saved `{png_path.name}` in `output/`.")

# Keep preview after widget reruns
ad = st.session_state.get("ad_ready")
if ad:
    st.image(ad["png"], caption="Preview", width="stretch")
    st.download_button(
        label="Download PNG",
        data=ad["png"],
        file_name=ad["file_name"],
        mime="image/png",
    )

# Post Text Generator — always visible
st.markdown("---")
st.markdown(
    "<p style='font-weight:700;font-size:1.15rem;margin-bottom:0.4rem;'>"
    "Post Text Generator</p>",
    unsafe_allow_html=True,
)

with st.form("post_text_form"):
    paper_number = st.text_input(
        "Paper Number",
        placeholder="44",
    )
    ga_caption = st.text_area(
        "Graphic abstract caption",
        height=160,
        placeholder="Paste the graphic abstract caption here.",
    )
    all_authors = st.text_area(
        "All authors' names",
        height=100,
        placeholder="Jane Doe, John Smith, …",
    )
    st.markdown(
        "<p style='color:#c62828;font-size:0.9rem;margin-top:-0.4rem;'>"
        "Manually tag author social-media handles on each platform "
        "(this text does not add @handles for you).</p>",
        unsafe_allow_html=True,
    )
    st.caption("DOI uses Volume and Issue from the ad figure section above.")

    post_submitted = st.form_submit_button("Generate ad texts", type="primary")

if post_submitted:
    ad_meta = st.session_state.get("ad_ready") or {}
    vol = (ad_meta.get("volume") or "").strip()
    iss = (ad_meta.get("issue") or "").strip()

    missing_post = []
    if not (paper_number or "").strip():
        missing_post.append("paper number")
    if not (ga_caption or "").strip():
        missing_post.append("graphic abstract caption")
    if not (all_authors or "").strip():
        missing_post.append("all authors' names")
    if not vol or not iss:
        missing_post.append("volume and issue (generate an ad figure first)")

    if missing_post:
        st.error("Please fill in: " + ", ".join(missing_post) + ".")
        st.session_state.pop("post_text_ready", None)
    else:
        doi = _doi_url(vol, iss, paper_number)
        text = _post_text(all_authors, ga_caption, doi)
        stem = ad_meta.get("stem") or output_basename(
            ad_meta.get("author_last", "author"),
            ad_meta.get("year", "year"),
            author_mode=ad_meta.get("author_mode", "et_al"),
            second_last=ad_meta.get("second_last", ""),
        )
        out_dir = _ensure_output_dir()
        txt_path = out_dir / f"{stem}.txt"
        txt_path.write_text(text, encoding="utf-8")

        st.session_state["post_text_ready"] = {
            "text": text,
            "file_name": txt_path.name,
            "txt_path": str(txt_path),
        }
        st.success(f"Post text ready. Saved `{txt_path.name}` in `output/`.")

post_ready = st.session_state.get("post_text_ready")
if post_ready:
    st.text_area(
        "Generated post text (copy from here)",
        value=post_ready["text"],
        height=260,
    )
    st.download_button(
        label="Download post text (.txt)",
        data=post_ready["text"].encode("utf-8"),
        file_name=post_ready["file_name"],
        mime="text/plain; charset=utf-8",
    )
