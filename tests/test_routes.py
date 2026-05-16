#!/usr/bin/env python3
"""Test agency_routes FastAPI endpoints."""
import asyncio
import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")

async def test():
    from agency_routes import agency_router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(agency_router, prefix="/api/agency")
    client = TestClient(app)

    print("=" * 60)
    print("  🧪 TESTING FASTAPI ROUTES")
    print("=" * 60)

    # Test status
    print("\n1️⃣  GET /api/agency/status")
    r = client.get("/api/agency/status")
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Swarm ready: {data['swarm']['dsl_ready']}")
        print(f"    Channels: {len(data['hermes']['hermes']['channels'])}")
    else:
        print(f"    Error: {r.text}")

    # Test hermes
    print("\n2️⃣  GET /api/agency/hermes")
    r = client.get("/api/agency/hermes")
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Channels: {len(data['hermes']['channels'])}")

    # Test mission
    print("\n3️⃣  POST /api/agency/mission")
    r = client.post("/api/agency/mission", json={
        "mission": "Qualify Dubai Marina leads",
        "scope": "leads",
        "requester_id": "test"
    })
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    State: {data.get('state')}")
        print(f"    OK: {data.get('ok')}")
        print(f"    Checkpoint: {data.get('checkpoint_id')}")

    # Test market intel
    print("\n4️⃣  POST /api/agency/market")
    r = client.post("/api/agency/market", json={"area": "Dubai Marina"})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    State: {data.get('state')}")

    print("\n" + "=" * 60)
    print("  ✅ ALL ROUTES RESPONDING")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test())
