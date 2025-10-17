"""
Agent Orchestrator - Central coordinator for all AI agents
Manages agent lifecycle, task routing, and inter-agent communication
"""
import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import json

from .base_agent import BaseAgent, AgentStatus, AgentCapability
from .sales_agent import SalesAgent
from .marketing_agent import MarketingAgent
from .content_agent import ContentAgent  
from .analytics_agent import AnalyticsAgent

class AgentOrchestrator:
    """
    Central orchestrator for managing all AI agents in the NOWHERE platform
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_registry: Dict[str, Type[BaseAgent]] = {
            "sales": SalesAgent,
            "marketing": MarketingAgent, 
            "content": ContentAgent,
            "analytics": AnalyticsAgent
        }
        
        self.task_queue = asyncio.Queue()
        self.running = False
        self.worker_count = 4
        self.workers: List[asyncio.Task] = []
        
        # Event system for inter-agent communication
        self.event_bus = {}
        self.subscribers = {}
        
        # Orchestrator metrics
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "active_agents": 0,
            "uptime_start": datetime.now(timezone.utc)
        }
        
        self.logger = logging.getLogger("agent_orchestrator")
        self.logger.info("Agent Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the orchestrator and default agents"""
        self.logger.info("Initializing Agent Orchestrator...")
        
        # Create and register default agents
        await self.create_agent("sales", SalesAgent)
        
        # Start worker tasks
        await self.start_workers()
        
        self.logger.info("Agent Orchestrator initialized successfully")
    
    async def create_agent(self, agent_type: str, agent_class: Type[BaseAgent] = None, config: Dict[str, Any] = None) -> str:
        """Create and register a new agent"""
        if agent_class is None:
            agent_class = self.agent_registry.get(agent_type)
            if not agent_class:
                raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create agent instance
        agent = agent_class()
        
        # Configure agent if config provided
        if config:
            agent.configure(config)
        
        # Register agent
        self.agents[agent.agent_id] = agent
        self.metrics["active_agents"] = len(self.agents)
        
        self.logger.info(f"Created {agent_type} agent: {agent.agent_id}")
        return agent.agent_id
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the orchestrator"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.pause()  # Gracefully pause before removal
            del self.agents[agent_id]
            self.metrics["active_agents"] = len(self.agents)
            self.logger.info(f"Removed agent: {agent_id}")
            return True
        return False
    
    async def submit_task(self, task: Dict[str, Any], agent_id: str = None, agent_type: str = None) -> str:
        """Submit a task to be processed by agents"""
        task_id = task.get('id', str(uuid.uuid4()))
        task['id'] = task_id
        task['submitted_at'] = datetime.now(timezone.utc).isoformat()
        
        # Route task to specific agent or find suitable agent
        if agent_id:
            target_agent = self.agents.get(agent_id)
            if not target_agent:
                raise ValueError(f"Agent {agent_id} not found")
            task['target_agent_id'] = agent_id
        elif agent_type:
            target_agent = self._find_agent_by_type(agent_type)
            if not target_agent:
                raise ValueError(f"No agent found for type: {agent_type}")
            task['target_agent_id'] = target_agent.agent_id
        else:
            # Auto-route based on task type
            target_agent = self._route_task(task)
            if target_agent:
                task['target_agent_id'] = target_agent.agent_id
            else:
                raise ValueError(f"No suitable agent found for task: {task.get('type')}")
        
        # Add to task queue
        await self.task_queue.put(task)
        self.metrics["total_tasks"] += 1
        
        self.logger.info(f"Task {task_id} submitted to agent {task['target_agent_id']}")
        return task_id
    
    def _find_agent_by_type(self, agent_type: str) -> Optional[BaseAgent]:
        """Find an agent by type"""
        for agent in self.agents.values():
            if agent_type.lower() in agent.name.lower():
                return agent
        return None
    
    def _route_task(self, task: Dict[str, Any]) -> Optional[BaseAgent]:
        """Auto-route task to appropriate agent based on task type and capabilities"""
        task_type = task.get('type', '').lower()
        
        # Task type to capability mapping
        capability_mapping = {
            'qualify_lead': AgentCapability.LEAD_QUALIFICATION,
            'schedule_follow_up': AgentCapability.CLIENT_COMMUNICATION,
            'generate_proposal': AgentCapability.LEAD_QUALIFICATION,
            'create_campaign': AgentCapability.CAMPAIGN_MANAGEMENT,
            'generate_content': AgentCapability.CONTENT_CREATION,
            'analyze_data': AgentCapability.DATA_ANALYSIS,
            'analyze_sales_pipeline': AgentCapability.DATA_ANALYSIS
        }
        
        required_capability = capability_mapping.get(task_type)
        if not required_capability:
            # Default to first available agent
            return next(iter(self.agents.values())) if self.agents else None
        
        # Find agent with required capability
        for agent in self.agents.values():
            if required_capability in agent.get_capabilities():
                return agent
        
        return None
    
    async def start_workers(self):
        """Start worker tasks to process the task queue"""
        if self.running:
            return
        
        self.running = True
        self.workers = []
        
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        self.logger.info(f"Started {self.worker_count} worker tasks")
    
    async def stop_workers(self):
        """Stop all worker tasks"""
        self.running = False
        
        # Cancel all worker tasks
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers = []
        self.logger.info("All workers stopped")
    
    async def _worker(self, worker_name: str):
        """Worker task to process tasks from the queue"""
        self.logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Process task
                await self._process_task(task, worker_name)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks available, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                self.metrics["failed_tasks"] += 1
        
        self.logger.info(f"Worker {worker_name} stopped")
    
    async def _process_task(self, task: Dict[str, Any], worker_name: str):
        """Process a task with the appropriate agent"""
        task_id = task['id']
        agent_id = task.get('target_agent_id')
        
        if not agent_id or agent_id not in self.agents:
            self.logger.error(f"Invalid agent_id {agent_id} for task {task_id}")
            self.metrics["failed_tasks"] += 1
            return
        
        agent = self.agents[agent_id]
        
        try:
            self.logger.info(f"{worker_name} processing task {task_id} with agent {agent.name}")
            
            # Execute task with agent
            result = await agent.execute(task)
            
            if result.get('success'):
                self.metrics["successful_tasks"] += 1
                self.logger.info(f"Task {task_id} completed successfully")
                
                # Emit success event
                await self._emit_event('task_completed', {
                    'task_id': task_id,
                    'agent_id': agent_id,
                    'result': result
                })
            else:
                self.metrics["failed_tasks"] += 1
                self.logger.error(f"Task {task_id} failed: {result.get('error')}")
                
                # Emit failure event
                await self._emit_event('task_failed', {
                    'task_id': task_id,
                    'agent_id': agent_id,
                    'error': result.get('error')
                })
                
        except Exception as e:
            self.metrics["failed_tasks"] += 1
            self.logger.error(f"Task {task_id} execution error: {e}")
            
            await self._emit_event('task_error', {
                'task_id': task_id,
                'agent_id': agent_id,
                'error': str(e)
            })
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to subscribers"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(data)
                except Exception as e:
                    self.logger.error(f"Event callback error: {e}")
    
    def subscribe(self, event_type: str, callback):
        """Subscribe to orchestrator events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def get_agent_status(self, agent_id: str = None) -> Dict[str, Any]:
        """Get status of specific agent or all agents"""
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                return agent.get_status()
            return {"error": f"Agent {agent_id} not found"}
        
        # Return status of all agents
        return {
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "orchestrator_metrics": self.get_metrics()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        uptime = (datetime.now(timezone.utc) - self.metrics["uptime_start"]).total_seconds()
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "queue_size": self.task_queue.qsize(),
            "worker_count": len(self.workers),
            "success_rate": (
                self.metrics["successful_tasks"] / self.metrics["total_tasks"] * 100 
                if self.metrics["total_tasks"] > 0 else 0
            )
        }
    
    async def pause_agent(self, agent_id: str) -> bool:
        """Pause a specific agent"""
        agent = self.agents.get(agent_id)
        if agent:
            await agent.pause()
            return True
        return False
    
    async def resume_agent(self, agent_id: str) -> bool:
        """Resume a specific agent"""
        agent = self.agents.get(agent_id)
        if agent:
            await agent.resume()
            return True
        return False
    
    async def reset_agent(self, agent_id: str) -> bool:
        """Reset a specific agent"""
        agent = self.agents.get(agent_id)
        if agent:
            await agent.reset()
            return True
        return False
    
    async def get_task_history(self, agent_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get task history for agents"""
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                tasks = await agent.get_memory('tasks')
                return list(tasks.values())[-limit:] if tasks else []
        
        # Get task history from all agents
        all_tasks = []
        for agent in self.agents.values():
            tasks = await agent.get_memory('tasks')
            if tasks:
                all_tasks.extend(tasks.values())
        
        # Sort by timestamp and return latest
        all_tasks.sort(key=lambda x: x.get('started_at', ''), reverse=True)
        return all_tasks[:limit]
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.logger.info("Shutting down Agent Orchestrator...")
        
        # Pause all agents
        for agent in self.agents.values():
            await agent.pause()
        
        # Stop workers
        await self.stop_workers()
        
        # Wait for queue to empty
        await self.task_queue.join()
        
        self.logger.info("Agent Orchestrator shutdown complete")

# Global orchestrator instance
orchestrator = AgentOrchestrator()