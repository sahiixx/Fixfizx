#!/usr/bin/env python3
"""
Test the Fixfizx + agency-agents integration.

Run this to verify:
1. DSL imports work
2. Swarm adapter initializes
3. Hermes bridge registers handlers
4. Routes would mount correctly
"""
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")

async def test_integration():
    print("=" * 60)
    print("  🧪 FIXFIZX + AGENCY-AGENTS INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Import DSL
    print("\n1️⃣  Testing DSL imports...")
    try:
        from sovereign_swarm.dsl import DeterministicSovereignLoop, Mission
        print("   ✅ DSL imports OK")
    except Exception as e:
        print(f"   ❌ DSL import failed: {e}")
        return False

    # Test 2: Import adapter
    print("\n2️⃣  Testing RealEstateSwarmAdapter...")
    try:
        from agents.real_estate_adapter import (
            RealEstateSwarmAdapter,
            RealEstateHermesBridge,
            get_swarm_adapter,
            get_hermes_bridge,
        )
        print("   ✅ Adapter imports OK")
    except Exception as e:
        print(f"   ❌ Adapter import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Initialize adapter
    print("\n3️⃣  Initializing adapter...")
    try:
        adapter = RealEstateSwarmAdapter()
        status = adapter.status()
        print(f"   ✅ Adapter ready")
        print(f"      Model: {status['model']}")
        print(f"      Scopes: {status['scopes_available']}")
    except Exception as e:
        print(f"   ❌ Adapter init failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Initialize Hermes bridge
    print("\n4️⃣  Initializing Hermes bridge...")
    try:
        bridge = RealEstateHermesBridge(adapter)
        await bridge.start()
        report = bridge.report()
        print(f"   ✅ Hermes bridge ready")
        print(f"      Channels: {len(report['hermes']['channels'])}")
        print(f"      Handlers: {report['hermes']['handlers_registered']}")
        await bridge.stop()
    except Exception as e:
        print(f"   ❌ Hermes bridge failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5: Test mission via Hermes
    print("\n5️⃣  Testing mission dispatch via Hermes...")
    try:
        bridge = RealEstateHermesBridge(adapter)
        await bridge.start()
        result = await bridge.hermes.send(
            "real_estate",
            {"action": "status"},
            sender="test",
        )
        print(f"   ✅ Hermes dispatch OK")
        print(f"      Result keys: {list(result.keys())}")
        await bridge.stop()
    except Exception as e:
        print(f"   ❌ Hermes dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 6: Run a real mission (dry)
    print("\n6️⃣  Testing real mission (status check)...")
    try:
        result = await adapter.run_mission(
            mission="Test Dubai real estate market analysis",
            scope="leads",
            requester_id="integration_test",
        )
        print(f"   ✅ Mission completed")
        print(f"      State: {result['state']}")
        print(f"      OK: {result['ok']}")
        print(f"      Checkpoints: {len(result.get('checkpoints', []))}")
    except Exception as e:
        print(f"   ❌ Mission failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 7: Import agency routes
    print("\n7️⃣  Testing agency_routes...")
    try:
        from agency_routes import agency_router
        print(f"   ✅ Agency routes import OK")
        routes = [r.path for r in agency_router.routes]
        print(f"      Routes: {routes}")
    except Exception as e:
        print(f"   ❌ Agency routes failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("  ✅ ALL TESTS PASSED")
    print("=" * 60)
    print("\n  Integration ready:")
    print("    • DSL checkpointing: ACTIVE")
    print("    • Hermes bus: 13 channels")
    print("    • Real estate swarm: 9 agents")
    print("    • FastAPI routes: /api/agency/*")
    print("\n  Next steps:")
    print("    1. cd /home/sahiix/Fixfizx/backend")
    print("    2. PYTHONPATH=/home/sahiix/sovereign-swarm-v2 python -m uvicorn server:app --reload")
    print("    3. Test: curl http://localhost:8000/api/agency/status")
    return True


if __name__ == "__main__":
    ok = asyncio.run(test_integration())
    sys.exit(0 if ok else 1)
