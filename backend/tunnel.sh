#!/bin/bash
# Start Cloudflare tunnel for port 9001

# Kill existing
pkill -f "cloudflared.*9001" 2>/dev/null
sleep 2

# Start fresh
nohup cloudflared tunnel --url http://localhost:9001 > /tmp/tunnel_9001.log 2>&1 &
echo "PID: $!"
sleep 15

URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/tunnel_9001.log | head -1)
echo "URL: $URL"

if [ -n "$URL" ]; then
  echo ""
  echo "========================================"
  echo "  🌐 TUNNEL ACTIVE"
  echo "========================================"
  echo ""
  echo "  $URL"
  echo ""
  echo "  Test:"
  echo "    curl $URL/"
  echo "    curl $URL/api/agency/status"
  echo ""
fi

wait
