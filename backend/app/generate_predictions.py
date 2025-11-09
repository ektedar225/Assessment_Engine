"""
generate_predictions.py

Generates a CSV in the required submission format:
Query,Assessment_url
Query 1,Recommendation 1 (URL)
Query 1,Recommendation 2 (URL)
...
"""
import argparse
import pandas as pd
import requests
import json

API_URL = "http://localhost:8000/recommend"

def generate(input_csv, output_csv, k=5):
    df = pd.read_csv(input_csv)
    if 'Query' not in df.columns:
        raise ValueError("Input CSV must have a 'Query' column")
    rows = []
    for q in df['Query'].astype(str).tolist():
        payload = {"query": q, "k": k}
        r = requests.post(API_URL, json=payload, timeout=30)
        if r.status_code != 200:
            print("Warning: request failed for query:", q, r.status_code, r.text)
            continue
        data = r.json()
        recs = data.get("recommendations", [])
        for rec in recs:
            rows.append({"Query": q, "Assessment_url": rec.get("url","")})
    out_df = pd.DataFrame(rows)
    out_df.to_csv(output_csv, index=False)
    print("Wrote predictions to", output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="../../data/Gen_AI_Dataset.csv", help="test CSV with Query column")
    parser.add_argument("--output", type=str, default="../../data/predictions.csv", help="output csv as required in Appendix 3")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    generate(args.input, args.output, k=args.k)
