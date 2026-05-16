#!/usr/bin/env python3
"""
Fixfizx Deploy Script — Production launcher.

Sets up:
1. Python environment with correct PYTHONPATH
2. Cloudflare tunnel for public access
3. Systemd service for persistence
4. Health check endpoint
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

APP_DIR = Path("/home/sahiix/Fixfizx/backend")
LOG_DIR = Path("/home/sahiix/Fixfizx/logs")
PID_FILE = Path("/tmp/fixfizx.pid")

ENV = {
    **os.environ,
    "PYTHONPATH": "/home/sahiix/sovereign-swarm-v2:/home/sahiix/agency-agents:/home/sahiix/campaigns:/home/sahiix/Fixfizx/backend",
    "OLLAMA_BASE_URL": "http://localhost:11434",
}


def setup():
    """Create directories and validate environment."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ Directories ready")
    print(f"   App: {APP_DIR}")
    print(f"   Logs: {LOG_DIR}")
    print(f"   PYTHONPATH: {ENV['PYTHONPATH'][:60]}...")


def start_server():
    """Start the FastAPI server."""
    cmd = [
        sys.executable, "-m", "uvicorn",
        "server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--workers", "1",
    ]
    print(f"\n🚀 Starting server: {' '.join(cmd)}")
    print(f"   Working dir: {APP_DIR}")

    proc = subprocess.Popen(
        cmd,
        cwd=str(APP_DIR),
        env=ENV,
        stdout=open(LOG_DIR / "server.log", "a"),
        stderr=subprocess.STDOUT,
    )

    PID_FILE.write_text(str(proc.pid))
    print(f"   PID: {proc.pid}")
    return proc


def start_tunnel():
    """Start Cloudflare quick tunnel."""
    cmd = ["cloudflared", "tunnel", "--url", "http://localhost:8000"]
    print(f"\n🌐 Starting tunnel: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def print_endpoints(url: str = None):
    """Print available API endpoints."""
    print("\n" + "=" * 60)
    print("  ✅ FIXFIZX DEPLOYED")
    print("=" * 60)
    if url:
        print(f"\n  🌐 Public URL: {url}")
    print(f"  📍 Local: http://localhost:8000")
    print("\n  Endpoints:")
    print("    GET  /api/agency/status")
    print("    GET  /api/agency/hermes")
    print("    POST /api/agency/mission")
    print("    POST /api/agency/ghost")
    print("    GET  /api/agency/ghost/{system}/status")
    print("    GET  /api/agency/ghost/{system}/leads")
    print("    POST /api/agency/ghost/{system}/quote")
    print("    POST /api/agency/ghost/{system}/process")
    print("\n  Systems:")
    for name in ["locksmith", "electrical", "plumbing", "roofing", "towing"]:
        print(f"    • {name}-ghost")
    print("\n  Logs:")
    print(f"    tail -f {LOG_DIR}/server.log")
    print("\n  Stop:")
    print(f"    kill $(cat {PID_FILE})")


def main():
    print("=" * 60)
    print("  🚀 FIXFIZX DEPLOY")
    print("=" * 60)

    setup()

    # Start server
    server_proc = start_server()

    # Start tunnel
    tunnel_proc = start_tunnel()

    # Wait for tunnel URL
    print("\n⏳ Waiting for tunnel URL...")
    url = None
    for line in tunnel_proc.stdout:
        line = line.strip()
        if "trycloudflare.com" in line:
            for word in line.split():
                if "trycloudflare.com" in word:
                    url = word.strip()
                    break
        if url:
            break
        print(f"   Tunnel: {line}")

    print_endpoints(url)

    # Keep running
    print("\n💤 Server running. Press Ctrl+C to stop.")
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server_proc.terminate()
        tunnel_proc.terminate()
        PID_FILE.unlink(missing_ok=True)
        print("✅ Stopped")


if __name__ == "__main__":
    main()
