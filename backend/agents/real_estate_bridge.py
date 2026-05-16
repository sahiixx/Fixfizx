"""
Real Estate Bridge — Standalone adapter for Fixfizx + agency-agents.

No Fixfizx dependencies. Pure sovereign-swarm-v2 + agency-agents.
Can be imported into any FastAPI app.
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add agency-agents to path
AGENCY_ROOT = Path("/home/sahiix/agency-agents")
sys.path.insert(0, str(AGENCY_ROOT))
sys.path.insert(0, str(AGENCY_ROOT / "deepagents/libs/deepagents"))

# Add sovereign-swarm-v2 to path
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
from sovereign_swarm.dsl import DeterministicSovereignLoop, Mission
from sovereign_swarm.protocols.hermes_v2 import HermesV2


class RealEstateBridge:
    """Bridge between Fixfizx and agency-agents real estate swarm."""

    SCOPES = {
        "leads": "Stage 1 only — Lead Qualification + Market Intelligence",
        "matching": "Stage 2 only — Property Matching + Outreach",
        "deals": "Stage 3 only — Deal Negotiation + RERA Compliance",
        "pipeline": "Stage 4 only — CRM + Investor Pitch + Post-Sale",
        "pitch": "Stage 4 — Investor pitch deck data",
        "full": "All stages — intake to close",
    }

    def __init__(self, model: str = "llama3.1", base_url: str = None):
        self.model = model
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.dsl = DeterministicSovereignLoop()
        self._lock = asyncio.Lock()

    async def run_mission(
        self,
        mission: str,
        scope: str = "full",
        requester_id: str = "fixfizx",
    ) -> Dict[str, Any]:
        """Run a real estate mission with DSL checkpointing."""

        result = await self.dsl.run(
            raw_goal=f"Real estate: {mission} [{scope}]",
            requester_id=requester_id,
        )

        return {
            "ok": result.ok,
            "state": result.state,
            "mission": mission,
            "scope": scope,
            "checkpoint_id": result.checkpoint_id,
            "elapsed_sec": result.elapsed_sec,
            "data": result.data,
            "error": result.error_message if not result.ok else None,
        }

    async def run_lead_qualification(self, leads: List[Dict]) -> Dict[str, Any]:
        """Run lead qualification on a batch."""
        mission = f"Qualify {len(leads)} leads"
        return await self.run_mission(mission, scope="leads")

    async def run_property_matching(self, criteria: Dict) -> Dict[str, Any]:
        """Match properties for criteria."""
        mission = f"Match properties for: {json.dumps(criteria)}"
        return await self.run_mission(mission, scope="matching")

    async def run_market_intelligence(self, area: str = "Dubai") -> Dict[str, Any]:
        """Generate market intelligence."""
        mission = f"Analyze {area} real estate market"
        return await self.run_mission(mission, scope="leads")

    def status(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "dsl_ready": self.dsl is not None,
            "scopes_available": list(self.SCOPES.keys()),
        }


class HermesBridge:
    """Connects RealEstateBridge to HermesV2 bus."""

    def __init__(self, bridge: RealEstateBridge, hermes: HermesV2 = None):
        self.bridge = bridge
        self.hermes = hermes or HermesV2()
        self._register_handlers()

    def _register_handlers(self):
        self.hermes.register("agency", self._handle_agency)
        self.hermes.register("swarm", self._handle_agency)

    async def _handle_real_estate(self, payload: Dict) -> Dict:
        action = payload.get("action", "mission")
        mission = payload.get("mission", payload.get("goal", "default"))
        scope = payload.get("scope", "full")
        requester = payload.get("requester_id", "hermes")

        if action == "mission":
            return await self.bridge.run_mission(mission, scope, requester)
        elif action == "lead_qual":
            return await self.bridge.run_lead_qualification(payload.get("leads", []))
        elif action == "match":
            return await self.bridge.run_property_matching(payload.get("criteria", {}))
        elif action == "market":
            return await self.bridge.run_market_intelligence(payload.get("area", "Dubai"))
        elif action == "status":
            return self.bridge.status()
        return {"error": f"Unknown action: {action}"}

    async def _handle_agency(self, payload: Dict) -> Dict:
        return await self._handle_real_estate(payload)

    async def start(self):
        await self.hermes.start()

    async def stop(self):
        await self.hermes.stop()

    def report(self) -> Dict:
        return {
            "bridge": self.bridge.status(),
            "hermes": self.hermes.status(),
        }


# Singletons
_bridge: Optional[RealEstateBridge] = None
_hermes: Optional[HermesBridge] = None


def get_bridge() -> RealEstateBridge:
    global _bridge
    if _bridge is None:
        _bridge = RealEstateBridge()
    return _bridge


def get_hermes() -> HermesBridge:
    global _hermes
    if _hermes is None:
        _hermes = HermesBridge(get_bridge())
    return _hermes
