import requests
resp = requests.post("http://127.0.0.1:7861/api/predict", json={
    "data": ["??"],
    "fn_index": 0,
    "session_hash": "test123",
    "event_id": "evt1",
    "event_data": None
})
print("Status:", resp.status_code)
print("Response:", resp.text[:500])
