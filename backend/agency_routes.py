"""
Fixfizx Agency Routes — Production integration with agency-agents + ghost systems.

Provides:
- /api/agency/status — Swarm + Hermes status
- /api/agency/mission — Real estate missions
- /api/agency/ghost/* — Ghost agent management (5 systems)
"""
import os
import sys
from typing import Dict, List, Optional

sys.path.insert(0, "/home/sahiix/agency-agents")
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from agents.real_estate_bridge import get_bridge, get_hermes, RealEstateBridge, HermesBridge
from agents.ghost_controller import get_ghost_controller, GhostController

agency_router = APIRouter()


# ── Request Models ──────────────────────────────────────────────────────────

class MissionRequest(BaseModel):
    mission: str
    scope: Optional[str] = "full"
    requester_id: Optional[str] = "fixfizx_api"


class GhostRequest(BaseModel):
    system: str = "locksmith"  # locksmith, electrical, plumbing, roofing, towing
    action: str = "status"     # status, process_lead, process_all, quote
    lead: Optional[Dict] = None


class SwarmDispatchRequest(BaseModel):
    action: str = "mission"
    payload: Dict
    channel: str = "agency"


# ── Status ──────────────────────────────────────────────────────────────────

@agency_router.get("/status")
async def get_agency_status():
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
    hermes = get_hermes()
    return hermes.report()


# ── Real Estate Missions ────────────────────────────────────────────────────

@agency_router.post("/mission")
async def submit_mission(request: MissionRequest):
    bridge = get_bridge()
    try:
        result = await bridge.run_mission(
            mission=request.mission,
            scope=request.scope,
            requester_id=request.requester_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── Ghost Agent Routes ─────────────────────────────────────────────────────

@agency_router.post("/ghost")
async def ghost_dispatch(request: GhostRequest):
    """Dispatch to any ghost agent system."""
    ghosts = get_ghost_controller()
    try:
        result = await ghosts._dispatch(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@agency_router.get("/ghost/{system}/status")
async def ghost_status(system: str):
    """Get status of a specific ghost system."""
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown ghost system: {system}")
    return ghosts.agents[system].status()


@agency_router.get("/ghost/{system}/leads")
async def ghost_leads(system: str):
    """Get all leads for a ghost system."""
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown ghost system: {system}")
    agent = ghosts.agents[system]
    return {"leads": agent._load_leads()}


@agency_router.post("/ghost/{system}/quote")
async def ghost_quote(system: str, lead: Dict):
    """Generate a quote for a lead."""
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown ghost system: {system}")
    agent = ghosts.agents[system]
    return {"quote": agent._generate_quote(lead)}


@agency_router.post("/ghost/{system}/process")
async def ghost_process(system: str):
    """Process all leads for a ghost system."""
    ghosts = get_ghost_controller()
    if system not in ghosts.agents:
        raise HTTPException(status_code=404, detail=f"Unknown ghost system: {system}")
    agent = ghosts.agents[system]
    results = await agent.process_all_leads()
    return {"processed": len(results), "results": results}


# ── Swarm Dispatch ──────────────────────────────────────────────────────────

@agency_router.post("/swarm")
async def dispatch_swarm(request: SwarmDispatchRequest):
    hermes = get_hermes()
    try:
        result = await hermes.hermes.send(
            request.channel,
            request.payload,
            sender="fixfizx_api",
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── Background Tasks ────────────────────────────────────────────────────────

@agency_router.post("/mission/async")
async def submit_mission_async(
    request: MissionRequest,
    background_tasks: BackgroundTasks,
):
    bridge = get_bridge()
    async def _run():
        result = await bridge.run_mission(
            mission=request.mission,
            scope=request.scope,
            requester_id=request.requester_id,
        )
        print(f"[ASYNC MISSION COMPLETE] {result}")
    background_tasks.add_task(_run)
    return {"status": "dispatched", "mission": request.mission}
