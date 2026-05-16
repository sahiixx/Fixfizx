#!/bin/bash
# Start SAHIIXX Agency API on port 9001

fuser -k 9001/tcp 2>/dev/null
sleep 1

cd /home/sahiix/Fixfizx/backend
export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"

nohup python3 -m uvicorn standalone_api:app --host 0.0.0.0 --port 9001 > /home/sahiix/Fixfizx/logs/server.log 2>&1 &
echo $! > /tmp/api.pid
echo "Server started on PID $! port 9001"
sleep 3

if curl -s http://localhost:9001/health > /dev/null; then
  echo "✅ API responding on port 9001"
  curl -s http://localhost:9001/api/agency/status | python3 -m json.tool
else
  echo "❌ API not responding"
fi
