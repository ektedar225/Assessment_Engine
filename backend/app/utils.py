import os
import csv
import pandas as pd
from typing import List, Dict
import numpy as np

def load_catalog(csv_path: str) -> pd.DataFrame:
    """
    Load SHL catalog CSV expected to have columns:
      - assessment_name
      - url
      - description
      - test_type
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Catalog file not found: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        raise ValueError(
            f"Catalog file is empty: {csv_path}. Provide a CSV with at least 'assessment_name' and 'url' columns, or run build_index with --crawl to auto-generate entries."
        )
    expected = {"assessment_name", "url"}
    if not expected.issubset(set(df.columns)):
        raise ValueError(f"catalog.csv must contain columns: at least {expected}")
    # Ensure columns exist
    for c in ["description", "test_type"]:
        if c not in df.columns:
            df[c] = ""
    df = df.dropna(subset=["assessment_name","url"]).reset_index(drop=True)
    return df

def load_queries_from_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Load the dataset (train/test) file uploaded by user. Expect columns:
      - Query
      - Assessment_url  (train only)
    It may contain only queries (test).
    """
    df = pd.read_csv(dataset_path)
    return df

def topk_from_scores(scores: np.ndarray, k:int):
    # scores: 1D numpy array
    idx = np.argsort(-scores)[:k]
    return idx, scores[idx]

def balance_by_type(df_results: pd.DataFrame, k:int):
    """
    Given a DataFrame with a 'test_type' column and a 'score' column,
    try to balance results across test_type categories. This is a simple
    heuristic: pick top from each type in round-robin until k filled.
    """
    if 'test_type' not in df_results.columns:
        return df_results.iloc[:k]
    groups = {}
    for t, g in df_results.groupby('test_type'):
        groups[t] = g.sort_values('score', ascending=False).to_dict('records')
    out = []
    type_keys = list(groups.keys())
    i = 0
    while len(out) < k:
        if not type_keys:  # if no types left or no types to begin with
            break
        t = type_keys[i % len(type_keys)]
        if groups[t]:
            out.append(groups[t].pop(0))
        else:
            # remove exhausted type
            type_keys.remove(t)
            if not type_keys:
                break
        i += 1
    return pd.DataFrame(out)[:k]
