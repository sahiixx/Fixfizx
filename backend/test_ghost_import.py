import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")

from agents.ghost_controller import get_ghost_controller
print("Ghost controller import OK")
ghosts = get_ghost_controller()
print(f"Ghosts: {list(ghosts.agents.keys())}")
