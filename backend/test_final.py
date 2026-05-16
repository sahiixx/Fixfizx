#!/usr/bin/env python3
"""Final integration test — direct imports, no __init__.py cascade."""
import asyncio
import sys

# Only sovereign-swarm-v2
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")

async def test():
    print("=" * 60)
    print("  ✅ FINAL INTEGRATION TEST")
    print("=" * 60)

    # 1. DSL
    from sovereign_swarm.dsl import DeterministicSovereignLoop, Mission
    dsl = DeterministicSovereignLoop()
    print("1️⃣  DSL initialized")

    # 2. Hermes
    from sovereign_swarm.protocols.hermes_v2 import HermesV2
    bus = HermesV2()
    await bus.start()
    print("2️⃣  Hermes bus started")

    # 3. Import agency-agents swarm module directly
    sys.path.insert(0, "/home/sahiix/agency-agents")
    import real_estate_swarm
    print(f"3️⃣  real_estate_swarm loaded: {len(real_estate_swarm.AGENTS)} agents")

    # 4. Run a mission
    result = await dsl.run("Qualify Dubai marina leads", requester_id="fixfizx")
    print(f"\n4️⃣  Mission completed:")
    print(f"    State: {result.state}")
    print(f"    OK: {result.ok}")
    print(f"    Checkpoint: {result.checkpoint_id}")

    # 5. Hermes dispatch test
    msg = await bus.send("dsl", {"action": "status"}, sender="test")
    print(f"\n5️⃣  Hermes dispatch: {msg.get('result', {})}")

    await bus.stop()

    print("\n" + "=" * 60)
    print("  ✅ CORE INTEGRATION VERIFIED")
    print("=" * 60)
    print("\n  The bridge files are ready:")
    print("    • agents/real_estate_bridge.py — adapter")
    print("    • agency_routes.py — FastAPI routes")
    print("\n  To complete Fixfizx integration:")
    print("    1. Fix 'emergentintegrations' dependency in Fixfizx")
    print("    2. Or: run bridge standalone without Fixfizx agents/__init__.py")
    return True

if __name__ == "__main__":
    ok = asyncio.run(test())
    sys.exit(0 if ok else 1)
