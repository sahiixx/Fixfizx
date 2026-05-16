import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")

from agents.real_estate_bridge import get_bridge, get_hermes
print("Bridge import OK")
bridge = get_bridge()
print(f"Bridge status: {bridge.status()}")
