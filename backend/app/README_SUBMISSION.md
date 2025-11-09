Submission checklist and quick run instructions

Files added in this patch:
- `generate_predictions_local.py` — produce `predictions.csv` directly from FAISS index
- `approach.md` — concise approach document for submission
- `requirements.txt` — pinned Python packages used by backend/scripts

Quick steps to reproduce predictions.csv (from `backend/app`):

1. Ensure you have Python 3.10+ and a virtual environment.

2. Install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. If model_store isn't present, build it:

```powershell
# generate catalog (if not present)
python generate_catalog_from_train.py
python build_index.py
```

4. Generate predictions (from the test set):

```powershell
python generate_predictions_local.py --input ../../data/test.csv --output ../../data/predictions.csv -k 5
```

5. Verify `predictions.csv` exists and follows required format (columns `Query,Assessment_url`).

API verification (if running backend):

Health:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

Recommend example:
```powershell
$body = @{ query = "Need a Java developer who can collaborate with stakeholders"; k = 5 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/recommend" -Method POST -Body $body -ContentType "application/json"
```

Notes:
- The local generator reads from `model_store/faiss.index`, `embeddings.npy`, and `metadata.csv`.
- If you prefer to generate predictions via the API, use `generate_predictions.py` (it posts to `http://localhost:8000/recommend`).
