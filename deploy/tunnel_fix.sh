#!/bin/bash
# Tunnel with custom DNS
export CLOUDFLARE_DNS="1.1.1.1"
rm -f /tmp/tunnel_9001.log
cloudflared tunnel --url http://localhost:9001 > /tmp/tunnel_9001.log 2>&1 &
echo "PID: $!"
sleep 30
URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/tunnel_9001.log | head -1)
echo "URL: $URL"
if [ -n "$URL" ]; then
  echo "✅ TUNNEL ACTIVE: $URL"
  curl -s "$URL/" | python3 -m json.tool
else
  echo "❌ No URL found"
  cat /tmp/tunnel_9001.log | tail -5
fi
