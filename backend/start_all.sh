#!/bin/bash
# Start everything

export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"

mkdir -p /home/sahiix/Fixfizx/logs

# Kill existing
pkill -f "uvicorn standalone_api" 2>/dev/null
pkill -f "cloudflared tunnel.*8001" 2>/dev/null
sleep 2

echo "========================================"
echo "  🚀 SAHIIXX AGENCY API LAUNCH"
echo "========================================"
echo ""

# Start server
echo "1️⃣  Starting API server..."
cd /home/sahiix/Fixfizx/backend
nohup python3 -m uvicorn standalone_api:app --host 0.0.0.0 --port 8001 > /home/sahiix/Fixfizx/logs/server.log 2>&1 &
echo "    PID: $!"

sleep 3

# Test local
echo ""
echo "2️⃣  Testing local API..."
if curl -s http://localhost:8001/health > /dev/null; then
  echo "    ✅ API responding"
else
  echo "    ❌ API not responding"
fi

# Start tunnel
echo ""
echo "3️⃣  Starting Cloudflare tunnel..."
nohup cloudflared tunnel --url http://localhost:8001 > /home/sahiix/Fixfizx/logs/tunnel.log 2>&1 &
echo "    PID: $!"

sleep 15

# Get URL
URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /home/sahiix/Fixfizx/logs/tunnel.log | head -1)

if [ -n "$URL" ]; then
  echo ""
  echo "========================================"
  echo "  ✅ API IS LIVE"
  echo "========================================"
  echo ""
  echo "  🌐 $URL"
  echo ""
  echo "  Test it:"
  echo "    curl $URL/health"
  echo "    curl $URL/api/agency/status"
  echo ""
  echo "  Save this URL: $URL"
  echo ""
else
  echo ""
  echo "  ⚠️ Tunnel still starting..."
  echo "    Check: tail -f /home/sahiix/Fixfizx/logs/tunnel.log"
fi

wait
