"""test_api.py

Runs a small smoke test for the backend API. It first tries to use FastAPI's
TestClient (no server required). If that fails (version mismatches), it falls
back to making HTTP requests to http://127.0.0.1:8000 so you can run uvicorn
separately and still test the endpoints.
"""
import traceback
try:
    from fastapi.testclient import TestClient
    import main

    client = TestClient(main.app)
    r = client.get('/health')
    print('GET /health ->', r.status_code, r.json())
    resp = client.post('/recommend', json={'query': 'Need a Java developer who can collaborate with stakeholders', 'k': 3})
    print('POST /recommend ->', resp.status_code)
    try:
        js = resp.json()
        print('Response keys:', list(js.keys()))
        recs = js.get('recommendations', [])
        print('Number of recs:', len(recs))
        if recs:
            print('First rec sample:', recs[0])
    except Exception:
        print('Failed to decode JSON from response')
except Exception as e:
    print('TestClient approach failed:', str(e))
    traceback.print_exc()
    print('\nFalling back to HTTP requests to http://127.0.0.1:8000')
    import requests
    try:
        r = requests.get('http://127.0.0.1:8000/health', timeout=5)
        print('GET /health ->', r.status_code, r.json())
    except Exception as e2:
        print('Could not reach server on 127.0.0.1:8000 — start it with:')
        print('  uvicorn main:app --host 127.0.0.1 --port 8000')
        print('Error:', e2)
        raise SystemExit(1)

    try:
        resp = requests.post('http://127.0.0.1:8000/recommend', json={'query': 'Need a Java developer who can collaborate with stakeholders', 'k': 3}, timeout=20)
        print('POST /recommend ->', resp.status_code)
        js = resp.json()
        print('Response keys:', list(js.keys()))
        recs = js.get('recommendations', [])
        print('Number of recs:', len(recs))
        if recs:
            print('First rec sample:', recs[0])
    except Exception as e3:
        print('POST /recommend failed:', e3)
