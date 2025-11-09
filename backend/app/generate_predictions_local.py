"""
generate_predictions_local.py

Generates the submission CSV (Appendix 3 format) directly from the FAISS index
without calling the API. This is useful for offline prediction generation for the
unlabeled test set prior to submission.

Usage (from backend/app):
    python generate_predictions_local.py --input ../../data/test.csv --output ../../data/predictions.csv -k 5
"""
import argparse
import pandas as pd
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

MODEL_NAME = "all-MiniLM-L6-v2"

def load_index(model_dir="model_store"):
    idx = faiss.read_index(os.path.join(model_dir, "faiss.index"))
    embs = np.load(os.path.join(model_dir, "embeddings.npy"))
    meta = pd.read_csv(os.path.join(model_dir, "metadata.csv"))
    return idx, embs, meta

def search_topk(query, index, metadata, model, k=5, min_score=0.2):
    q_emb = model.encode([query], show_progress_bar=False, normalize_embeddings=True)[0]
    D, I = index.search(q_emb.reshape(1, -1).astype('float32'), k*2)
    rows = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        if score < min_score:
            continue
        row = metadata.iloc[idx]
        rows.append({
            "assessment_name": str(row.get("assessment_name","")),
            "url": str(row.get("url","")),
            "score": float(score)
        })
        if len(rows) >= k:
            break
    return rows

def generate(input_csv, output_csv, k=5):
    index, embs, metadata = load_index()
    model = SentenceTransformer(MODEL_NAME)
    df = pd.read_csv(input_csv)
    if 'Query' not in df.columns:
        raise ValueError("Input CSV must have a 'Query' column")
    out_rows = []
    for q in df['Query'].astype(str).tolist():
        recs = search_topk(q, index, metadata, model, k=k)
        if not recs:
            # if no results due to score threshold, fall back to taking top k regardless
            D, I = index.search(model.encode([q], normalize_embeddings=True).astype('float32'), k)
            for idx in I[0]:
                if idx < 0:
                    continue
                out_rows.append({"Query": q, "Assessment_url": metadata.iloc[idx]['url']})
        else:
            for r in recs:
                out_rows.append({"Query": q, "Assessment_url": r['url']})
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(output_csv, index=False)
    print(f"Wrote {len(out_rows)} rows to {output_csv}")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=str, default='../../data/test.csv')
    p.add_argument('--output', type=str, default='../../data/predictions.csv')
    p.add_argument('-k', type=int, default=5)
    args = p.parse_args()
    generate(args.input, args.output, k=args.k)
