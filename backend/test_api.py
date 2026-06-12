import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== Test / ===")
r = client.get("/")
print(f"Status: {r.status_code}")
print(f"Location: {r.headers.get('location')}")

print()
print("=== Test /api/v1/metadata ===")
r = client.get("/api/v1/metadata")
print(f"Status: {r.status_code}")
print(f"Body: {r.json() if r.status_code == 200 else r.text}")

print()
print("=== Test /api/v1/devices ===")
r = client.get("/api/v1/devices", params={"page": 1, "page_size": 10})
print(f"Status: {r.status_code}")
print(f"Body: {r.json() if r.status_code == 200 else r.text[:500]}")

print()
print("=== Test create device (with invalid IMEI) ===")
r = client.post("/api/v1/devices", json={
    "brand": "苹果",
    "model": "iPhone 15",
    "imei": "123456789012345",
})
print(f"Status: {r.status_code}")
print(f"Body: {r.json()}")
