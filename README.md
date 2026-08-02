# Geomorphica Ads Generator

A small Streamlit web app that builds **social-media ad images (PNG)** and **post text** for [Geomorphica](https://geomorphica.org) papers.

You enter the paper details, upload a graphic abstract, generate a branded ad, then optionally build a short social post with a DOI link.

Made by Larry Syu-Heng Lai, August 2026.

**GitHub:** [Geomorphica/Ads_generator](https://github.com/Geomorphica/Ads_generator)

**License:** MIT (see [`LICENSE`](LICENSE))

### Open the Colab notebook

Use this notebook to launch the app in the browser (it downloads the code from this repo and installs packages):

[`geomorphica_ad-gen_launch.ipynb`](https://github.com/Geomorphica/Ads_generator/blob/main/geomorphica_ad-gen_launch.ipynb)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Geomorphica/Ads_generator/blob/main/geomorphica_ad-gen_launch.ipynb)

Click the badge → **Runtime → Run all** → open the Cloudflare link the notebook prints.

---

## What you get

- Ad figure: blue/white Geomorphica chrome, logo, author line, title, graphic abstract
- Author modes: **>3 authors** (`Lastname et al. (year)`), **2 authors** (`A & B (year)`), **single** (`Lastname (year)`)
- Dark theme toggle (ad colors only)
- Post Text Generator: caption + all authors + DOI  
  `https://doi.org/10.59236/geomorphica.v{volume}i{issue}.{paperNumber}`
- Saved names (also downloadable in the app), e.g.  
  `Shugar_2026_ads.png` / `.txt`, `Grom_Forte_2026_ads.png`, `Sumaiya_etal_2024_ads.png`

---

## Run on Google Colab

**Idea:** keep only the notebook on Google Drive (easy to open). Colab then **clones the app from GitHub** and installs packages. You do **not** need to copy `app.py`, fonts, or logos onto Drive.

1. Put [`geomorphica_ad-gen_launch.ipynb`](geomorphica_ad-gen_launch.ipynb) somewhere on Drive (or open it from this GitHub repo in Colab).
2. Open it with **Google Colaboratory**.
3. **Runtime → Run all**.
4. The notebook clones https://github.com/Geomorphica/Ads_generator.git and installs Streamlit / Pillow / `requirements.txt`.
5. Wait for a clickable `https://….trycloudflare.com` link (free Cloudflare tunnel; no IP password).
6. Use the app, then **Download** the PNG and post text in the app before you stop the runtime  
   (files on Colab are temporary and disappear when the session ends).

Keep the last notebook cell running while you use the app.

---

## Run locally

Needs Python and a conda env named `work` (or any env with the packages installed).

```bash
git clone https://github.com/Geomorphica/Ads_generator.git
cd Ads_generator
conda activate work
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL (often `http://localhost:8501`). Stop with `Ctrl+C`.

### How to use the form

1. Choose authors: **>3** (default), **2**, or **single**.
2. Enter last name(s). The second-name field appears only for **2 authors**.
3. Enter year, volume, and issue.
4. Enter the paper title (journal-style title case is applied automatically).
5. Upload one graphic abstract (drag and drop or browse).
6. Optional: **Dark theme**.
7. Click **Generate ad figure**, then **Download PNG**.
8. Below: **Post Text Generator** — paper number, caption, all authors → **Generate ad texts** → download `.txt`.  
   DOI uses volume and issue from the figure form. Tag social handles yourself on each platform.

| Authors | Ad line |
|---------|---------|
| >3 | `Lastname et al. (year)` |
| 2 | `Lastname1 & Lastname2 (year)` |
| single | `Lastname (year)` |

Names stay as typed. Uploads: PNG, JPEG, WebP, GIF (first frame only). Output about **1080 px** wide, height about **1000–1500 px**.

---

## Repo layout (what belongs on GitHub)

```text
Ads_generator/
  app.py
  requirements.txt
  README.md
  geomorphica_ad-gen_launch.ipynb
  geomorphica_ads/          # Python package
  logo/                     # Logo_large_w.png, Logo_large_b.png
  assets/fonts/             # Roboto Bold + Light (required)
  .streamlit/               # optional theme
  output/.gitkeep           # folder placeholder; ignore generated files
  LICENSE
```

Not required for the public app: local `scripts/`, `examples/`, generated `output/*.png` / `*.txt`.

---

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/).
2. Connect [Geomorphica/Ads_generator](https://github.com/Geomorphica/Ads_generator).
3. Main file: `app.py`.
4. Deploy and open the URL.
