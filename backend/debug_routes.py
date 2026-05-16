import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")

from standalone_api import app

print("Routes:")
for route in app.routes:
    print(f"  {route.path}")
