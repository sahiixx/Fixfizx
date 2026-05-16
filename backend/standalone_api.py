#!/usr/bin/env python3
"""
Standalone Agency API — Serves agency-agents + ghost systems.

No Fixfizx dependencies. Pure sovereign-swarm-v2 + agency-agents + campaigns.
"""
import sys
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/campaigns")

import asyncio
from typing import Dict, List, Optional

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.real_estate_bridge import get_bridge, get_hermes
from agents.ghost_controller import get_ghost_controller

app = FastAPI(
    title="SAHIIXX Agency API",
    description="Real estate swarm + ghost agents",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agency_router = APIRouter(prefix="/api/agency", tags=["agency"])


# ── Models ─────────────────────────────────────────────────────────────────

class MissionRequest(BaseModel):
    mission: str
    scope: Optional[str] = "full"
    requester_id: Optional[str] = "api"


class GhostRequest(BaseModel):
    system: str = "locksmith"
    action: str = "status"
    lead: Optional[Dict] = None


class SwarmDispatchRequest(BaseModel):
    action: str = "mission"
    payload: Dict
    channel: str = "agency"


# ── Status ───────────────────────────────────────────────────────────────────

@agency_router.get("/status")
async def get_status():
    bridge = get_bridge()
    hermes = get_hermes()
    ghosts = get_ghost_controller()
    return {
        "swarm": bridge.status(),
        "hermes": hermes.report(),
        "ghosts": ghosts.status(),
        "integration": "production",
    }


@agency_router.get("/hermes")
async def get_hermes_status():
    return get_hermes().report()


# ── Real Estate ──────────────────────────────────────────────────────────────

@agency_router.post("/mission")
async def submit_mission(request: MissionRequest):
    bridge = get_bridge()
    try:
        return await bridge.run_mission(
            mission=request.mission,
            scope=request.scope,
            requester_id=request.requester_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── Ghost Agents ─────────────────────────────────────────────────────────────

@agency_router.post("/ghost")
async def ghost_dispatch(request: GhostRequest):
    ghosts = get_ghost_controller()
    try:
        return await ghosts._dispatch(request.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@agency_router.get("/ghost/{system}/status")
async def ghost_status(system: str):
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown: {system}")
    return ghosts.agents[system].status()


@agency_router.get("/ghost/{system}/leads")
async def ghost_leads(system: str):
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown: {system}")
    return {"leads": ghosts.agents[system]._load_leads()}


@agency_router.post("/ghost/{system}/quote")
async def ghost_quote(system: str, lead: Dict):
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown: {system}")
    return {"quote": ghosts.agents[system]._generate_quote(lead)}


@agency_router.post("/ghost/{system}/process")
async def ghost_process(system: str):
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown: {system}")
    results = await ghosts.agents[system].process_all_leads()
    return {"processed": len(results), "results": results}


# ── Swarm ────────────────────────────────────────────────────────────────────

@agency_router.post("/swarm")
async def dispatch_swarm(request: SwarmDispatchRequest):
    hermes = get_hermes()
    try:
        return await hermes.hermes.send(
            request.channel,
            request.payload,
            sender="api",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/")
async def root():
    return {
        "name": "SAHIIXX Agency API",
        "version": "2.0.0",
        "endpoints": [
            "/api/agency/status",
            "/api/agency/mission",
            "/api/agency/ghost",
            "/api/agency/ghost/{system}/status",
            "/api/agency/ghost/{system}/quote",
            "/api/agency/ghost/{system}/process",
        ],
        "systems": ["locksmith", "electrical", "plumbing", "roofing", "towing"],
    }


app.include_router(agency_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
