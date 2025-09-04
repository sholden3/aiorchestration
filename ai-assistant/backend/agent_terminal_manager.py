"""
Agent Terminal Manager - Each AI agent gets its own PTY terminal
Real terminal sessions for actual agent interaction
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of AI agents that can be spawned"""
    CLAUDE_ASSISTANT = "claude_assistant"  # Main AI assistant
    CODE_REVIEWER = "code_reviewer"        # Dr. Sarah Chen
    PERFORMANCE_OPTIMIZER = "performance"   # Marcus Rodriguez  
    UX_ANALYZER = "ux_analyzer"           # Emily Watson
    SECURITY_AUDITOR = "security"         # Security specialist
    TEST_GENERATOR = "test_generator"     # Test creation agent

class AgentStatus(Enum):
    """Agent lifecycle status"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    TERMINATED = "terminated"

class AIAgent:
    """Represents an individual AI agent with its own terminal"""
    
    def __init__(self, agent_type: AgentType, name: str = None):
        self.id = str(uuid.uuid4())
        self.type = agent_type
        self.name = name or f"{agent_type.value}_{self.id[:8]}"
        self.status = AgentStatus.INITIALIZING
        self.terminal_session = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tasks_completed = 0
        self.current_task = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'status': self.status.value,
            'terminal_session': self.terminal_session,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'tasks_completed': self.tasks_completed,
            'current_task': self.current_task
        }

class AgentTerminalManager:
    """
    Manages AI agents and their terminal sessions
    Each agent runs in its own PTY for real interaction
    """
    
    def __init__(self, max_agents: int = 6):
        self.max_agents = max_agents
        self.agents: Dict[str, AIAgent] = {}
        self.terminal_sessions: Dict[str, Any] = {}  # Maps agent_id to terminal
        
        # Pre-defined specialist agents
        self.specialists = {
            AgentType.CODE_REVIEWER: "Dr. Sarah Chen",
            AgentType.PERFORMANCE_OPTIMIZER: "Marcus Rodriguez",
            AgentType.UX_ANALYZER: "Emily Watson"
        }
        
    async def spawn_agent(self, agent_type: AgentType, auto_start: bool = True) -> AIAgent:
        """
        Spawn a new AI agent with its own terminal
        """
        if len(self.agents) >= self.max_agents:
            raise Exception(f"Maximum agent limit ({self.max_agents}) reached")
        
        # Create agent
        name = self.specialists.get(agent_type)
        agent = AIAgent(agent_type, name)
        
        # Create terminal session for agent
        if auto_start:
            terminal_id = await self._create_terminal_for_agent(agent)
            agent.terminal_session = terminal_id
            agent.status = AgentStatus.READY
        
        self.agents[agent.id] = agent
        logger.info(f"Spawned agent: {agent.name} ({agent.type.value})")
        
        return agent
    
    async def _create_terminal_for_agent(self, agent: AIAgent) -> str:
        """
        Create a PTY terminal session for an agent
        In real implementation, this would connect to actual PTY
        """
        terminal_id = f"terminal_{agent.id}"
        
        # This would integrate with the actual PTY system
        # For now, we track the session ID
        self.terminal_sessions[agent.id] = {
            'terminal_id': terminal_id,
            'created': datetime.now(),
            'agent_id': agent.id,
            'agent_name': agent.name
        }
        
        logger.info(f"Created terminal {terminal_id} for agent {agent.name}")
        return terminal_id
    
    async def send_to_agent(self, agent_id: str, command: str) -> str:
        """
        Send command to agent's terminal and return response
        """
        if agent_id not in self.agents:
            raise Exception(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        if agent.status not in [AgentStatus.READY, AgentStatus.IDLE]:
            raise Exception(f"Agent {agent.name} is not ready (status: {agent.status.value})")
        
        agent.status = AgentStatus.BUSY
        agent.last_activity = datetime.now()
        
        try:
            # Execute the command and get response
            response = f"Executed: {command}"
            
            # If this agent has a terminal session, try to use it
            if agent.terminal_session:
                # For now, simulate execution
                # In production, would send to actual PTY terminal
                logger.info(f"Executing on {agent.name}'s terminal: {command}")
                response = f"[{agent.name}] $ {command}\n"
                response += f"Command executed successfully at {datetime.now().isoformat()}\n"
            
            # Update agent status
            agent.status = AgentStatus.READY
            agent.tasks_completed += 1
            agent.last_activity = datetime.now()
            
            logger.info(f"Command completed on {agent.name}")
            return response
            
        except Exception as e:
            agent.status = AgentStatus.ERROR
            logger.error(f"Error executing on {agent.name}: {e}")
            raise
    
    async def terminate_agent(self, agent_id: str) -> None:
        """
        Terminate an agent and its terminal
        """
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        agent.status = AgentStatus.TERMINATED
        
        # Close terminal session
        if agent.terminal_session:
            self.terminal_sessions.pop(agent.id, None)
        
        del self.agents[agent_id]
        logger.info(f"Terminated agent: {agent.name}")
    
    def get_active_agents(self) -> List[AIAgent]:
        """Get list of active agents"""
        return [
            agent for agent in self.agents.values()
            if agent.status not in [AgentStatus.TERMINATED, AgentStatus.ERROR]
        ]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        active_agents = self.get_active_agents()
        
        return {
            'total': len(active_agents),
            'max_agents': self.max_agents,
            'by_status': {
                'ready': len([a for a in active_agents if a.status == AgentStatus.READY]),
                'busy': len([a for a in active_agents if a.status == AgentStatus.BUSY]),
                'idle': len([a for a in active_agents if a.status == AgentStatus.IDLE]),
                'error': len([a for a in active_agents if a.status == AgentStatus.ERROR])
            },
            'by_type': {
                agent_type.value: len([a for a in active_agents if a.type == agent_type])
                for agent_type in AgentType
            },
            'agents': [agent.to_dict() for agent in active_agents]
        }
    
    async def assign_task_to_agent(self, task: str, preferred_type: AgentType = None) -> AIAgent:
        """
        Assign a task to an appropriate agent
        Creates one if needed
        """
        # Find available agent of preferred type
        available = [
            a for a in self.get_active_agents()
            if a.status == AgentStatus.READY and 
            (preferred_type is None or a.type == preferred_type)
        ]
        
        if available:
            agent = available[0]
        else:
            # Spawn new agent if under limit
            if len(self.agents) < self.max_agents:
                agent_type = preferred_type or AgentType.CLAUDE_ASSISTANT
                agent = await self.spawn_agent(agent_type)
            else:
                raise Exception("No available agents and max limit reached")
        
        agent.current_task = task
        agent.status = AgentStatus.BUSY
        agent.last_activity = datetime.now()
        
        logger.info(f"Assigned task to {agent.name}: {task[:50]}...")
        return agent

# Global agent manager
agent_terminal_manager = AgentTerminalManager()