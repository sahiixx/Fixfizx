import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
from sovereign_swarm.dsl import DeterministicSovereignLoop
import asyncio

async def test():
    dsl = DeterministicSovereignLoop()
    result = await dsl.run("test mission", requester_id="test")
    print(f"State: {result.state}")
    print(f"OK: {result.ok}")
    print(f"Error: {result.error_message}")
    print(f"Checkpoint: {result.checkpoint_id}")

asyncio.run(test())
