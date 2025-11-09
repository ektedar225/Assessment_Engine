SHL Assessment Recommender — Approach (concise)

1. Problem framing
------------------
We build a retrieval-based recommendation system that maps a natural language query
or job description to the most relevant SHL "individual test solutions" from the
product catalog. The system uses dense semantic retrieval with a SentenceTransformer
embedding model and FAISS for efficient nearest-neighbour search. We filter out
pre-packaged job solutions and focus only on individual assessments.

2. Data pipeline
----------------
- Crawl the SHL product catalog and extract metadata: assessment_name, url,
  test_type (K/P), duration (minutes) and textual description.
- Save canonical catalog as `catalog.csv` and build model artifacts in `model_store/`:
  `faiss.index`, `embeddings.npy`, `metadata.csv`.
- Provided labeled train set (10 queries) used to tune thresholds and balancing
  heuristics. Unlabeled test set (9 queries) used for final predictions.

3. Retrieval & ranking
----------------------
- Encoder: `all-MiniLM-L6-v2` (SentenceTransformers). Documents and queries
  encoded with normalization so dot product in FAISS approximates cosine similarity.
- Index: FAISS flat index (cpu). For each query we retrieve top-N candidates and
  apply a score threshold to remove weak matches.
- Balancing: to satisfy the requirement for mixed domains (behavioral vs
  technical), we implement a simple heuristic that enforces inclusion of multiple
  `test_type` values when query contains multi-domain keywords.

4. Improvements and experiments (what to include in submission)
-------------------------------------------------------------
- Baseline: straightforward vector retrieval with no reranker. Evaluate Mean Recall@10.
- Improvements tried: lower/higher score thresholds; expand candidate pool before
  final selection; enforce test_type balance; use a lightweight cross-encoder reranker
  (optional) to reorder top candidates. Report dev recall before/after each change.

5. Engineering notes
--------------------
- Backend: FastAPI app (`main.py`) exposes `/health` and `/recommend` endpoints.
- Frontend: Vite + React app calls `/recommend` and shows tabular results.
- Repro scripts: `generate_catalog_from_train.py`, `build_index.py`,
  `generate_predictions_local.py` (creates the final CSV without needing the API).

6. How I validated
-------------------
- Ran `search_index.py` against the provided `test.csv` to inspect outputs.
- Generated `predictions.csv` using `generate_predictions_local.py` to match
  the required submission format.

Notes: This document summarizes the approach and choices. The two-page PDF
version can be created from this Markdown with minor formatting if required.
