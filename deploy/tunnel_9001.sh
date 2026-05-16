#!/bin/bash
# Persistent Cloudflare tunnel for port 9001
cd /tmp
exec cloudflared tunnel --url http://localhost:9001 > /tmp/tunnel_9001.log 2>&1
