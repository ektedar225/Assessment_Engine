from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import os
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from .utils import load_catalog, topk_from_scores, balance_by_type

app = FastAPI(title="SHL Assessment Recommender API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite's default port
        "https://shl-recommender.vercel.app",  # Vercel deployment
        "http://localhost:3000",  # Next.js default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_STORE = os.path.join(os.path.dirname(__file__), "model_store")
FAISS_PATH = os.path.join(MODEL_STORE, "faiss.index")
METADATA_PATH = os.path.join(MODEL_STORE, "metadata.csv")
EMB_PATH = os.path.join(MODEL_STORE, "embeddings.npy")

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDER = SentenceTransformer(EMBED_MODEL_NAME)
INDEX = None
METADATA = None
EMBEDDINGS = None

class RecommendRequest(BaseModel):
    query: str
    k: Optional[int] = 5

class AssessmentOut(BaseModel):
    assessment_name: str
    url: str
    test_type: Optional[str] = ""
    score: float

class RecommendResponse(BaseModel):
    query: str
    recommendations: List[AssessmentOut]

@app.on_event("startup")
def startup_load_index():
    global INDEX, METADATA, EMBEDDINGS
    if not os.path.exists(FAISS_PATH) or not os.path.exists(METADATA_PATH):
        raise RuntimeError("Model store missing. Run build_index.py first to create model_store (faiss.index + metadata.csv).")
    INDEX = faiss.read_index(FAISS_PATH)
    METADATA = pd.read_csv(METADATA_PATH)
    if os.path.exists(EMB_PATH):
        EMBEDDINGS = np.load(EMB_PATH)
    else:
        EMBEDDINGS = None
    # No return — startup will fail fast if missing

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    q = req.query.strip()
    k = max(1, min(10, req.k or 5))
    if not q:
        raise HTTPException(status_code=400, detail="Query must be non-empty")
    # embed query
    q_emb = EMBEDDER.encode(q, convert_to_numpy=True, normalize_embeddings=True).astype('float32')
    # search
    D, I = INDEX.search(np.expand_dims(q_emb, axis=0), k*3)  # request more to allow balancing
    idxs = I[0]
    scores = D[0]
    # prepare results dataframe
    results = []
    for i, sc in zip(idxs, scores):
        if i < 0:
            continue
        row = METADATA.iloc[i].to_dict()
        row['score'] = float(sc)
        results.append(row)
    if not results:
        raise HTTPException(status_code=500, detail="No results found")
    df_res = pd.DataFrame(results)
    # try to balance by test_type (simple heuristic) while keeping score ordering
    df_balanced = balance_by_type(df_res, k=k)
    # if balancing returns fewer, fall back to straight top-k by score
    if len(df_balanced) < k:
        df_res_sorted = df_res.sort_values('score', ascending=False).head(k)
    else:
        df_res_sorted = df_balanced
    # build response
    recs = []
    for _, r in df_res_sorted.iterrows():
        recs.append({
            "assessment_name": str(r.get("assessment_name","")),
            "url": str(r.get("url","")),
            "test_type": str(r.get("test_type","")),
            "score": float(r.get("score",0.0))
        })
    return {"query": q, "recommendations": recs}
