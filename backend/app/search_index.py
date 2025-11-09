"""search_index.py

Load the FAISS index and run test queries against it. Shows how to:
1. Load model_store/faiss.index, embeddings.npy, and metadata.csv
2. Run queries through the same SentenceTransformer model
3. Get top-k results with scores

Usage (from backend/app directory):
    python search_index.py                     # run with default test queries
    python search_index.py --test ../data/test.csv  # use queries from test.csv
    python search_index.py --query "your query here" # run a single query
"""
import os
import argparse
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from utils import load_queries_from_dataset, topk_from_scores, balance_by_type

MODEL_NAME = "all-MiniLM-L6-v2"  # must match build_index.py
DEFAULT_QUERIES = [
    "Looking for Java developer assessment that takes 45 minutes",
    "Need a test for sales skills, entry level position",
    "Technical assessment for Python and SQL, one hour max",
]

def load_index(model_dir="model_store"):
    """Load the FAISS index, embeddings, and metadata."""
    index = faiss.read_index(os.path.join(model_dir, "faiss.index"))
    embeddings = np.load(os.path.join(model_dir, "embeddings.npy"))
    metadata = pd.read_csv(os.path.join(model_dir, "metadata.csv"))
    return index, embeddings, metadata

def search(query, index, metadata, model, k=5, min_score=0.2):
    """
    Search for top-k matches for the query. Returns DataFrame with results 
    and cosine similarity scores (sorted by score, descending).
    
    Args:
        min_score: minimum cosine similarity score (0-1) to include in results
    """
    # encode query same way as docs (normalize since index uses dot product)
    q_emb = model.encode([query], show_progress_bar=False, normalize_embeddings=True)[0]
    
    # get top k matches (scores are dot products ~ cosine sim since normalized)
    D, I = index.search(q_emb.reshape(1, -1).astype('float32'), k=k*2)  # get more candidates
    
    # gather metadata for matches
    results = metadata.iloc[I[0]].copy()
    results['score'] = D[0]
    
    # Filter by minimum score and sort
    results = results[results['score'] >= min_score]
    results = results.sort_values('score', ascending=False)
    
    return results.head(k)
    
    # try to balance by test_type if available
    return balance_by_type(results, k=k)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="path to test.csv with Query column")
    parser.add_argument("--query", type=str, help="single query to run")
    parser.add_argument("--model-dir", type=str, default="model_store",
                       help="directory with faiss.index, embeddings.npy, metadata.csv")
    parser.add_argument("-k", type=int, default=5, help="number of results per query")
    args = parser.parse_args()

    # load index and model
    index, embeddings, metadata = load_index(args.model_dir)
    model = SentenceTransformer(MODEL_NAME)
    
    # get queries to run
    queries = []
    if args.query:
        queries = [args.query]
    elif args.test:
        df = load_queries_from_dataset(args.test)
        queries = df["Query"].tolist()
    else:
        queries = DEFAULT_QUERIES
    
    # run queries and show results
    print(f"\nRunning {len(queries)} queries, k={args.k}\n")
    for i, q in enumerate(queries, 1):
        print(f"Query {i}: {q}")
        results = search(q, index, metadata, model, k=args.k)
        print("\nTop matches:")
        for _, r in results.iterrows():
            print(f"  {r['assessment_name']:<50} (score: {r['score']:.3f})")
            print(f"    {r['url']}")
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    main()