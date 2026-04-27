"""Fixfizx Agency Routes — Connects NOWHERE.AI to the SAHIIXX ecosystem.

Adds /api/agency/* endpoints to Fixfizx's FastAPI backend that:
- Accept missions and dispatch them to agency-agents via A2A
- Query agent status and swarm metrics
- Run safety scans on user input before processing
- Track costs per mission via BudgetController

Mount this router in server.py:
    from agency_routes import agency_router
    app.include_router(agency_router, prefix="/api/agency")
"""
import sys
import os
import time
import asyncio
from typing import Dict, List, Optional

# Add paths
sys.path.insert(0, "/mnt/c/Users/Sahil Khan/Downloads")
sys.path.insert(0, "/home/sahiix/sahiixx-bus")

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
except ImportError:
    APIRouter = None
    BaseModel = None

from sovereign_swarm import SafetyCouncil, RBACGuard, RBACPermission, BudgetController

if APIRouter is None:
    # Stub router for environments without FastAPI
    class _StubRouter:
        def get(self, path, **kwargs):
            def decorator(f): return f
            return decorator
        def post(self, path, **kwargs):
            def decorator(f): return f
            return decorator
    agency_router = _StubRouter()
else:
    agency_router = APIRouter(prefix="/agency", tags=["agency"])

# Shared instances
_safety = SafetyCouncil()
_budget = BudgetController(session_limit=100.0, daily_limit=500.0)


class MissionRequest(BaseModel):
    description: str
    preset: Optional[str] = None
    agents: Optional[List[str]] = None


class TaskRequest(BaseModel):
    agent_id: str
    task: str
    skills: Optional[List[str]] = None


class ScanRequest(BaseModel):
    text: str
    system_load: float = 0.0


if APIRouter is not None:

    @agency_router.get("/status")
    async def get_agency_status():
        """Get agency-agents and sovereign-swarm status."""
        budget = await _budget.remaining()
        return {
            "safety": _safety.report() if hasattr(_safety, 'report') else {},
            "budget": budget,
            "services": {
                "agency_agents": "http://localhost:8100",
                "friday_os": "http://localhost:8000",
                "goose_aios": "http://localhost:8001",
                "nowhere_ai": "http://localhost:8002",
            },
        }

    @agency_router.post("/mission")
    async def submit_mission(request: MissionRequest):
        """Submit a mission to agency-agents via A2A."""
        # Safety scan first
        scan = _safety.scan(request.description)
        if scan["blocked"]:
            raise HTTPException(status_code=400, detail={
                "error": "blocked_by_safety",
                "rule": scan["rule"],
                "confidence": scan["confidence"],
            })

        # Charge budget
        estimated_cost = 0.05  # $0.05 per mission
        accepted = await _budget.charge(f"mission_{int(time.time())}", estimated_cost)
        if not accepted:
            raise HTTPException(status_code=429, detail="budget_exceeded")

        # Forward to agency-agents
        try:
            from sahiixx_bus.bridge import AgencyBridge
            bridge = AgencyBridge()
            result = await bridge.submit_task(
                "orchestrator",
                request.description,
                skills=request.agents,
            )
            return {"status": "dispatched", "agency_response": result}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"agency_unavailable: {str(e)}")

    @agency_router.post("/task")
    async def submit_task(request: TaskRequest):
        """Dispatch a task to a specific agency agent."""
        scan = _safety.scan(request.task)
        if scan["blocked"]:
            raise HTTPException(status_code=400, detail={
                "error": "blocked_by_safety",
                "rule": scan["rule"],
            })

        try:
            from sahiixx_bus.bridge import AgencyBridge
            bridge = AgencyBridge()
            result = await bridge.submit_task(
                request.agent_id,
                request.task,
                skills=request.skills,
            )
            return {"status": "dispatched", "result": result}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"agency_unavailable: {str(e)}")

    @agency_router.post("/scan")
    async def safety_scan(request: ScanRequest):
        """Run a safety scan on user input."""
        result = _safety.scan(request.text, request.system_load)
        return result

    @agency_router.get("/agents")
    async def list_agents():
        """List available agency agents and their capabilities."""
        try:
            from sahiixx_bus.bridge import AgencyBridge
            bridge = AgencyBridge()
            agents = await bridge.discover_agents()
            return {"agents": agents}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"agency_unavailable: {str(e)}")

    @agency_router.post("/dubai-market-analysis")
    async def dubai_market_analysis(request: dict):
        """Analyze Dubai real estate market using agency-agents + Fixfizx data."""
        query = request.get("query", "")
        scan = _safety.scan(query)
        if scan["blocked"]:
            raise HTTPException(status_code=400, detail={"error": "blocked_by_safety", "rule": scan["rule"]})

        try:
            from sahiixx_bus.bridge import AgencyBridge, FixfizxBridge
            agency = AgencyBridge()
            fixfizx = FixfizxBridge()

            # Route market analysis to both
            agency_result = await agency.submit_task(
                "agency_realestate_0",
                f"Dubai market analysis: {query}",
                skills=["search", "lead"],
            )
            fixfizx_result = await fixfizx.dubai_market_analysis(query)

            return {
                "agency_analysis": agency_result,
                "platform_data": fixfizx_result,
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"service_unavailable: {str(e)}")