import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")

from standalone_api import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 60)
print("  🧪 STANDALONE API TEST")
print("=" * 60)

# Health
r = client.get("/health")
print(f"\n1️⃣  GET /health: {r.status_code}")
print(f"    {r.json()}")

# Root
r = client.get("/")
print(f"\n2️⃣  GET /: {r.status_code}")
data = r.json()
print(f"    Name: {data['name']}")
print(f"    Systems: {data['systems']}")

# Agency status
r = client.get("/api/agency/status")
print(f"\n3️⃣  GET /api/agency/status: {r.status_code}")
data = r.json()
print(f"    Ghost systems: {len(data['ghosts']['systems'])}")
for name, s in data['ghosts']['systems'].items():
    print(f"      • {name}: DSL={s['dsl_ready']}")

# Ghost status
r = client.get("/api/agency/ghost/locksmith/status")
print(f"\n4️⃣  GET /api/agency/ghost/locksmith/status: {r.status_code}")
print(f"    {r.json()}")

# Ghost quote
r = client.post("/api/agency/ghost/plumbing/quote", json={
    "company_name": "Test Plumbing",
    "contact_first": "Ahmed",
    "city": "Dubai",
    "pain_score": "3",
})
print(f"\n5️⃣  POST /api/agency/ghost/plumbing/quote: {r.status_code}")
quote = r.json()["quote"]
print(f"    Setup: ${quote['setup_original']} → ${quote['setup_discounted']}")
print(f"    Year 1: ${quote['year_1_total']:,}")

# Mission
r = client.post("/api/agency/mission", json={
    "mission": "Qualify Dubai Marina leads",
    "scope": "leads",
})
print(f"\n6️⃣  POST /api/agency/mission: {r.status_code}")
data = r.json()
print(f"    State: {data['state']}")
print(f"    OK: {data['ok']}")
print(f"    Checkpoint: {data.get('checkpoint_id', 'N/A')[:40]}...")

print("\n" + "=" * 60)
print("  ✅ STANDALONE API READY")
print("=" * 60)
print("\n  Start with:")
print("    python3 standalone_api.py")
print("  Or:")
print("    uvicorn standalone_api:app --host 0.0.0.0 --port 8001")
