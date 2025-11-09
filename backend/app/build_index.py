"""
build_index.py

- Option A: Create vector index from a local catalog.csv (recommended if you already scraped).
- Option B: Basic crawler to fetch product pages under SHL product catalog (best-effort).
Outputs:
 - model_store/embeddings.npy
 - model_store/faiss.index
 - model_store/metadata.csv
"""
import os
import argparse
import pandas as pd
import numpy as np
# Compatibility shim: newer versions of huggingface_hub renamed `cached_download` -> `hf_hub_download`.
# Some versions of `sentence_transformers` still import `cached_download`. If the installed
# `huggingface_hub` lacks `cached_download`, alias it to `hf_hub_download` so the import succeeds.
try:
    import huggingface_hub as _hf_hub
    if not hasattr(_hf_hub, "cached_download") and hasattr(_hf_hub, "hf_hub_download"):
        _hf_hub.cached_download = _hf_hub.hf_hub_download
except Exception:
    # If huggingface_hub isn't available or aliasing fails, we'll let the original import raise an error
    pass

from sentence_transformers import SentenceTransformer
import faiss
from utils import load_catalog
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast; good default

def crawl_shl_catalog(out_csv="catalog.csv", base_url="https://www.shl.com/solutions/products/product-catalog/"):
    """
    Very simple crawler that tries to get links under the product catalog main page.
    NOTE: This is a best-effort helper. For robustness, manually collect catalog rows or
    export the catalog to CSV and use Option A.
    """
    resp = requests.get(base_url, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"Unable to fetch {base_url}: {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    # try to extract hrefs that look like product pages
    anchors = soup.find_all("a", href=True)
    product_links = set()
    for a in anchors:
        href = a['href']
        if "/solutions/products/product-catalog/" in href and href != base_url:
            product_links.add(href if href.startswith("http") else "https://www.shl.com" + href)
    rows = []
    for link in product_links:
        try:
            r = requests.get(link, timeout=10)
            s = BeautifulSoup(r.text, "html.parser")
            title = s.find("h1").get_text(strip=True) if s.find("h1") else a.get_text(strip=True)
            desc = ""
            p = s.find("p")
            if p:
                desc = p.get_text(strip=True)
            # We attempt to find Test Type text in page - fallback empty
            test_type = ""
            rows.append({"assessment_name": title, "url": link, "description": desc, "test_type": test_type})
        except Exception:
            continue
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {len(df)} rows to {out_csv}")
    return out_csv

def build_index(catalog_csv, out_dir="model_store", model_name=MODEL_NAME, use_crawl=False):
    os.makedirs(out_dir, exist_ok=True)
    if use_crawl:
        catalog_csv = crawl_shl_catalog(out_csv=catalog_csv)
    df = load_catalog(catalog_csv)
    texts = (df["assessment_name"].fillna("") + ". " + df["description"].fillna("")).tolist()
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    # build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine by normalizing
    index.add(embeddings.astype('float32'))
    faiss.write_index(index, os.path.join(out_dir, "faiss.index"))
    np.save(os.path.join(out_dir, "embeddings.npy"), embeddings)
    df.to_csv(os.path.join(out_dir, "metadata.csv"), index=False)
    print("Index built and saved to", out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=str, default="../../data/catalog.csv", help="path to catalog.csv")
    parser.add_argument("--out", type=str, default="model_store", help="output folder")
    parser.add_argument("--crawl", action="store_true", help="try crawling SHL catalog (best-effort)")
    args = parser.parse_args()
    build_index(args.catalog, out_dir=args.out, use_crawl=args.crawl)
