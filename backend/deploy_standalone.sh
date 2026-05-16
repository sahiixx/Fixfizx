#!/bin/bash
# Deploy standalone agency API

cd /home/sahiix/Fixfizx/backend
export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"

mkdir -p /home/sahiix/Fixfizx/logs

# Kill existing
pkill -f "uvicorn standalone_api" 2>/dev/null
sleep 1

# Start API
echo "🚀 Starting SAHIIXX Agency API on port 8001..."
python3 -m uvicorn standalone_api:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 1 \
  > /home/sahiix/Fixfizx/logs/standalone_api.log 2>&1 &
API_PID=$!
echo $API_PID > /tmp/standalone_api.pid
echo "  PID: $API_PID"

# Start tunnel
echo ""
echo "🌐 Starting Cloudflare tunnel..."
cloudflared tunnel --url http://localhost:8001 \
  > /home/sahiix/Fixfizx/logs/tunnel_api.log 2>&1 &
TUNNEL_PID=$!
echo $TUNNEL_PID > /tmp/tunnel_api.pid
echo "  PID: $TUNNEL_PID"

# Wait for URL
sleep 5
URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /home/sahiix/Fixfizx/logs/tunnel_api.log | head -1)

if [ -n "$URL" ]; then
  echo ""
  echo "========================================"
  echo "  ✅ SAHIIXX AGENCY API IS LIVE"
  echo "========================================"
  echo ""
  echo "  🌐 Public URL: $URL"
  echo "  📍 Local: http://localhost:8001"
  echo ""
  echo "  Endpoints:"
  echo "    GET  $URL/health"
  echo "    GET  $URL/api/agency/status"
  echo "    POST $URL/api/agency/mission"
  echo "    POST $URL/api/agency/ghost"
  echo "    GET  $URL/api/agency/ghost/{system}/status"
  echo "    POST $URL/api/agency/ghost/{system}/quote"
  echo "    POST $URL/api/agency/ghost/{system}/process"
  echo ""
  echo "  Ghost Systems:"
  echo "    • locksmith-ghost"
  echo "    • electrical-ghost"
  echo "    • plumbing-ghost"
  echo "    • roofing-ghost"
  echo "    • towing-ghost"
  echo ""
  echo "  Logs:"
  echo "    tail -f /home/sahiix/Fixfizx/logs/standalone_api.log"
  echo "    tail -f /home/sahiix/Fixfizx/logs/tunnel_api.log"
  echo ""
  echo "  Stop:"
  echo "    kill \$(cat /tmp/standalone_api.pid) \&\& kill \$(cat /tmp/tunnel_api.pid)"
  echo ""
else
  echo "  ⚠️ Tunnel starting... check: tail -f /home/sahiix/Fixfizx/logs/tunnel_api.log"
fi

wait $API_PID
