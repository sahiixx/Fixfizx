import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")

from server import app

print("Server imports OK")
print("Routes:")
for r in app.routes:
    path = str(r.path)
    if "/agency" in path or "/ghost" in path:
        print(f"  {path}")
