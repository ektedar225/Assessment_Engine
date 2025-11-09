"""generate_catalog_from_train.py

Create `shl-recommender/data/catalog.csv` from the training dataset.

Reads `../../data/train.csv`, extracts unique `Assessment_url` values and
attempts to fetch the page title to use as `assessment_name`. Falls back to
using the URL as the name when network/title extraction fails.

Usage: run this from `backend/app` (it uses paths relative to this folder):
    python generate_catalog_from_train.py
"""
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


TRAIN_PATH = os.path.join("..", "..", "data", "train.csv")
OUT_PATH = os.path.join("..", "..", "data", "catalog.csv")


def fetch_title(url: str) -> str:
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            s = BeautifulSoup(r.text, "html.parser")
            h1 = s.find("h1")
            if h1 and h1.get_text(strip=True):
                return h1.get_text(strip=True)
            title = s.title.string if s.title and s.title.string else None
            if title:
                return title.strip()
    except Exception:
        pass
    return url


def main():
    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError(f"train.csv not found at {TRAIN_PATH}")
    df = pd.read_csv(TRAIN_PATH)
    if "Assessment_url" not in df.columns:
        raise ValueError("train.csv must contain an 'Assessment_url' column")
    urls = df["Assessment_url"].dropna().unique().tolist()
    rows = []
    for u in urls:
        name = fetch_title(u)
        rows.append({"assessment_name": name, "url": u, "description": "", "test_type": ""})
    out_df = pd.DataFrame(rows)
    out_dir = os.path.dirname(OUT_PATH)
    os.makedirs(out_dir, exist_ok=True)
    out_df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(out_df)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
