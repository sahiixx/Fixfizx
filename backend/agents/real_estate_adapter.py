"""
Real Estate Swarm Adapter — Wraps agency-agents for Fixfizx integration.

Converts the sequential real_estate_swarm.py into an async service
that can be called from Fixfizx's FastAPI endpoints via the
HermesV2 message bus.
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

# Import DSL components from sovereign-swarm-v2
sys.path.insert(0, "/home/sahiix/sovereign-swarm-v2")
from sovereign_swarm.dsl import DeterministicSovereignLoop, Mission
from sovereign_swarm.protocols.hermes_v2 import HermesV2


class RealEstateSwarmAdapter:
    """Async adapter for the real estate investment swarm."""

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
        self._running = False

    async def run_mission(
        self,
        mission: str,
        scope: str = "full",
        requester_id: str = "fixfizx",
    ) -> Dict[str, Any]:
        """Run a real estate mission via the DSL with checkpointing."""

        # Create a DSL mission
        dsl_mission = Mission(
            goal=f"Real estate: {mission} [{scope}]",
            domain="real_estate",
            max_tokens=200_000,
            max_time_sec=600,
            max_cost_usd=2.0,
            allow_self_modify=False,
            requester_id=requester_id,
        )

        # Run through DSL
        result = await self.dsl.run(mission=dsl_mission)

        # If DSL completed but we want actual swarm output, run the legacy pipeline
        if result.ok and scope in self.SCOPES:
            try:
                swarm_output = await self._run_legacy_swarm(mission, scope)
                result.data["swarm_output"] = swarm_output
            except Exception as e:
                result.data["swarm_warning"] = str(e)

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

    async def _run_legacy_swarm(self, mission: str, scope: str) -> Dict[str, Any]:
        """Run the legacy real_estate_swarm.py in a subprocess."""
        import subprocess

        cmd = [
            sys.executable,
            str(AGENCY_ROOT / "real_estate_swarm.py"),
            "--mission", mission,
            "--scope", scope,
            "--model", self.model,
        ]

        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = self.base_url

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=str(AGENCY_ROOT),
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=300,
        )

        return {
            "returncode": proc.returncode,
            "stdout": stdout.decode("utf-8", errors="replace")[-2000:],
            "stderr": stderr.decode("utf-8", errors="replace")[-1000:],
        }

    async def run_lead_qualification(self, leads: List[Dict]) -> Dict[str, Any]:
        """Run lead qualification on a batch of leads."""
        mission = f"Qualify {len(leads)} leads: " + json.dumps(leads[:3])
        return await self.run_mission(mission, scope="leads")

    async def run_property_matching(self, criteria: Dict) -> Dict[str, Any]:
        """Match properties for investor criteria."""
        mission = f"Match properties for: {json.dumps(criteria)}"
        return await self.run_mission(mission, scope="matching")

    async def run_market_intelligence(self, area: str = "Dubai") -> Dict[str, Any]:
        """Generate market intelligence report."""
        mission = f"Analyze {area} real estate market trends and DLD data"
        return await self.run_mission(mission, scope="leads")

    def status(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "dsl_ready": self.dsl is not None,
            "scopes_available": list(self.SCOPES.keys()),
        }


class RealEstateHermesBridge:
    """Connects RealEstateSwarmAdapter to HermesV2 bus."""

    def __init__(self, adapter: RealEstateSwarmAdapter, hermes: HermesV2 = None):
        self.adapter = adapter
        self.hermes = hermes or HermesV2()
        self._register_handlers()

    def _register_handlers(self):
        """Register handlers for real estate channels."""
        self.hermes.register("real_estate", self._handle_real_estate)
        self.hermes.register("agency", self._handle_agency)

    async def _handle_real_estate(self, payload: Dict) -> Dict:
        """Handle real estate requests from any Hermes channel."""
        action = payload.get("action", "mission")
        mission = payload.get("mission", payload.get("goal", "default mission"))
        scope = payload.get("scope", "full")
        requester = payload.get("requester_id", "hermes")

        if action == "mission":
            return await self.adapter.run_mission(mission, scope, requester)
        elif action == "lead_qual":
            leads = payload.get("leads", [])
            return await self.adapter.run_lead_qualification(leads)
        elif action == "match":
            criteria = payload.get("criteria", {})
            return await self.adapter.run_property_matching(criteria)
        elif action == "market":
            area = payload.get("area", "Dubai")
            return await self.adapter.run_market_intelligence(area)
        elif action == "status":
            return self.adapter.status()
        else:
            return {"error": f"Unknown action: {action}"}

    async def _handle_agency(self, payload: Dict) -> Dict:
        """Handle general agency requests."""
        return await self._handle_real_estate(payload)

    async def start(self):
        """Start the Hermes bus."""
        await self.hermes.start()

    async def stop(self):
        """Stop the Hermes bus."""
        await self.hermes.stop()

    def report(self) -> Dict:
        return {
            "adapter": self.adapter.status(),
            "hermes": self.hermes.status(),
        }


# Singleton instance
_swarm_adapter: Optional[RealEstateSwarmAdapter] = None
_hermes_bridge: Optional[RealEstateHermesBridge] = None


def get_swarm_adapter() -> RealEstateSwarmAdapter:
    global _swarm_adapter
    if _swarm_adapter is None:
        _swarm_adapter = RealEstateSwarmAdapter()
    return _swarm_adapter


def get_hermes_bridge() -> RealEstateHermesBridge:
    global _hermes_bridge
    if _hermes_bridge is None:
        adapter = get_swarm_adapter()
        _hermes_bridge = RealEstateHermesBridge(adapter)
    return _hermes_bridge
