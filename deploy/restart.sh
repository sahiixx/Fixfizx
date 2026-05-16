#!/bin/bash
# Restart API server on port 8001

fuser -k 8001/tcp 2>/dev/null
sleep 2

cd /home/sahiix/Fixfizx/backend
export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"

nohup python3 -m uvicorn standalone_api:app --host 0.0.0.0 --port 8001 > /home/sahiix/Fixfizx/logs/server.log 2>&1 &
echo $! > /tmp/api.pid
echo "Server started on PID $!"
sleep 3

if curl -s http://localhost:8001/health > /dev/null; then
  echo "✅ API responding"
  curl -s http://localhost:8001/ | python3 -m json.tool
else
  echo "❌ API not responding"
fi
