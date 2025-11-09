Backend README - SHL Assessment Recommender

1. Prepare catalog:
   - Put a file at data/catalog.csv with columns: assessment_name,url,description,test_type.
   - If you want to attempt crawling, run:
       python build_index.py --catalog ../../data/catalog.csv --out model_store --crawl
     Note: crawling is best-effort; manual creation of catalog.csv is more stable.

2. Build index:
    cd backend/app
    python build_index.py --catalog ../../data/catalog.csv --out model_store

   This will create backend/app/model_store with:
     - faiss.index
     - metadata.csv
     - embeddings.npy

3. Run API:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   Endpoints:
     GET /health  -> {"status":"ok"}
     POST /recommend
       body: {"query": "...", "k": 5}
       returns: {"query": "...", "recommendations": [{"assessment_name": "...", "url":"...", "test_type":"", "score":0.9}, ...]}

4. Generate predictions CSV for submission:
    Ensure API running locally, then:
    python generate_predictions.py --input ../../data/Gen_AI_Dataset.csv --output ../../data/predictions.csv --k 5

5. Docker:
   Use the provided Dockerfile to build and run the API in a container.

6. Notes:
   - Embeddings use sentence-transformers (no external paid API required).
   - You can swap to OpenAI embeddings by changing the embedding section in main.py and build_index.py.
