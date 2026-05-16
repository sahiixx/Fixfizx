#!/bin/bash
# Persistent tunnel
exec cloudflared tunnel --url http://localhost:9001 > /tmp/tunnel_9001.log 2>&1
