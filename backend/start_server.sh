#!/bin/bash
cd /home/sahiix/Fixfizx/backend
export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 > /home/sahiix/Fixfizx/logs/server.log 2>&1 &
echo $! > /tmp/fixfizx.pid
