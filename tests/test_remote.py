import json, urllib.request

BASE = "https://constitution-andale-flame-spin.trycloudflare.com"

# Test health
r = urllib.request.urlopen(f"{BASE}/health")
print("Health:", json.loads(r.read()))

# Test status
r = urllib.request.urlopen(f"{BASE}/api/agency/status")
data = json.loads(r.read())
print("\nStatus: OK")
print("Ghost systems:", list(data['ghosts']['systems'].keys()))

# Test quote
req = urllib.request.Request(
    f"{BASE}/api/agency/ghost/plumbing/quote",
    data=json.dumps({"company_name": "Test Plumbing", "contact_first": "Ahmed", "city": "Dubai", "pain_score": "3"}).encode(),
    headers={"Content-Type": "application/json"},
)
r = urllib.request.urlopen(req)
quote = json.loads(r.read())['quote']
print(f"\nQuote for {quote['company']}:")
print(f"  Setup: ${quote['setup_original']} -> ${quote['setup_discounted']}")
print(f"  Year 1: ${quote['year_1_total']:,}")

print("\n✅ ALL REMOTE TESTS PASSED")
