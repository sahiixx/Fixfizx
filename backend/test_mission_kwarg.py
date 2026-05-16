import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
from sovereign_swarm.dsl import DeterministicSovereignLoop, Mission
import asyncio

async def test():
    dsl = DeterministicSovereignLoop()
    m = Mission(goal="test", requester_id="test")
    result = await dsl.run(mission=m)
    print(f"State: {result.state}")
    print(f"OK: {result.ok}")
    print(f"Error: {result.error_message}")

asyncio.run(test())
