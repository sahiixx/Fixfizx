#!/bin/bash
# Fixfizx deploy script — production launcher
set -e

APP_DIR="/home/sahiix/Fixfizx/backend"
LOG_DIR="/home/sahiix/Fixfizx/logs"
PID_FILE="/tmp/fixfizx.pid"
TUNNEL_PID="/tmp/fixfizx-tunnel.pid"

export PYTHONPATH="/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend"
export OLLAMA_BASE_URL="http://localhost:11434"

mkdir -p "$LOG_DIR"

echo "========================================"
echo "  🚀 FIXFIZX DEPLOY"
echo "========================================"
echo ""
echo "  App: $APP_DIR"
echo "  Logs: $LOG_DIR"
echo "  PYTHONPATH: ${PYTHONPATH:0:60}..."
echo ""

# Start FastAPI server
echo "🚀 Starting server on port 8000..."
cd "$APP_DIR"
python3 -m uvicorn server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  >> "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"
echo "  PID: $SERVER_PID"

# Start Cloudflare tunnel
echo ""
echo "🌐 Starting Cloudflare tunnel..."
cloudflared tunnel --url http://localhost:8000 \
  >> "$LOG_DIR/tunnel.log" 2>&1 &
TUNNEL_PID=$!
echo $TUNNEL_PID > "$TUNNEL_PID"
echo "  PID: $TUNNEL_PID"

# Wait for tunnel URL
echo ""
echo "⏳ Waiting for public URL..."
sleep 5
URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG_DIR/tunnel.log" | head -1)

if [ -n "$URL" ]; then
  echo ""
  echo "========================================"
  echo "  ✅ FIXFIZX IS LIVE"
  echo "========================================"
  echo ""
  echo "  🌐 Public URL: $URL"
  echo "  📍 Local: http://localhost:8000"
  echo ""
  echo "  Endpoints:"
  echo "    GET  $URL/api/agency/status"
  echo "    POST $URL/api/agency/mission"
  echo "    POST $URL/api/agency/ghost"
  echo ""
  echo "  Ghost Systems:"
  echo "    • locksmith-ghost"
  echo "    • electrical-ghost"
  echo "    • plumbing-ghost"
  echo "    • roofing-ghost"
  echo "    • towing-ghost"
  echo ""
  echo "  Logs:"
  echo "    tail -f $LOG_DIR/server.log"
  echo "    tail -f $LOG_DIR/tunnel.log"
  echo ""
  echo "  Stop:"
  echo "    kill \$(cat $PID_FILE) && kill \$(cat $TUNNEL_PID)"
  echo ""
else
  echo "  ⚠️ Tunnel starting... check logs:"
  echo "    tail -f $LOG_DIR/tunnel.log"
fi

wait $SERVER_PID
