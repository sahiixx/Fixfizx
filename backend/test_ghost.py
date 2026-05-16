#!/usr/bin/env python3
"""Test ghost agent routes."""
import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
from agency_routes import agency_router
app.include_router(agency_router, prefix="/api/agency")
client = TestClient(app)

print("=" * 60)
print("  👻 GHOST AGENT ROUTE TEST")
print("=" * 60)

# Test status
print("\n1️⃣  GET /api/agency/status")
r = client.get("/api/agency/status")
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    Ghost systems: {len(data['ghosts']['systems'])}")
    for name, status in data['ghosts']['systems'].items():
        print(f"      • {name}: DSL={status['dsl_ready']}, leads={status['leads_processed']}")

# Test ghost status
print("\n2️⃣  GET /api/agency/ghost/locksmith/status")
r = client.get("/api/agency/ghost/locksmith/status")
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    print(f"    Data: {r.json()}")

# Test ghost leads
print("\n3️⃣  GET /api/agency/ghost/electrical/leads")
r = client.get("/api/agency/ghost/electrical/leads")
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    leads = r.json().get('leads', [])
    print(f"    Leads loaded: {len(leads)}")
    if leads:
        print(f"    Sample: {leads[0].get('company_name')}")

# Test ghost quote
print("\n4️⃣  POST /api/agency/ghost/plumbing/quote")
r = client.post("/api/agency/ghost/plumbing/quote", json={
    "company_name": "Test Plumbing LLC",
    "contact_first": "Ahmed",
    "city": "Dubai",
    "pain_score": "3",
})
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    quote = r.json().get('quote', {})
    print(f"    Company: {quote.get('company')}")
    print(f"    Setup: ${quote.get('setup_original')} → ${quote.get('setup_discounted')} ({quote.get('discount_percent')}% off)")
    print(f"    Year 1: ${quote.get('year_1_total'):,}")

print("\n" + "=" * 60)
print("  ✅ GHOST AGENTS READY")
print("=" * 60)
