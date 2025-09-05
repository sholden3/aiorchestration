"""
Default agent initialization for AI Orchestration Engine
Simplified version using enum capabilities
"""

from ai_orchestration_engine import AIAgent, AgentType, AgentCapability, AgentStatus


def get_default_agents():
    """Get default AI agents for the orchestration system"""
    agents = []
    
    # Claude agents
    agents.append(AIAgent(
        agent_id="claude_sonnet_primary",
        agent_type=AgentType.CLAUDE_SONNET,
        name="Claude Sonnet Primary",
        capabilities=[
            AgentCapability.CODE_GENERATION,
            AgentCapability.TEXT_GENERATION,
            AgentCapability.REASONING,
            AgentCapability.ANALYSIS
        ],
        context_window=200000,
        concurrent_capacity=3
    ))
    
    agents.append(AIAgent(
        agent_id="claude_haiku_fast",
        agent_type=AgentType.CLAUDE_HAIKU,
        name="Claude Haiku Fast",
        capabilities=[
            AgentCapability.TEXT_GENERATION,
            AgentCapability.SUMMARIZATION,
            AgentCapability.CLASSIFICATION
        ],
        context_window=200000,
        concurrent_capacity=5
    ))
    
    agents.append(AIAgent(
        agent_id="claude_opus_advanced",
        agent_type=AgentType.CLAUDE_OPUS,
        name="Claude Opus Advanced",
        capabilities=[
            AgentCapability.CODE_GENERATION,
            AgentCapability.TEXT_GENERATION,
            AgentCapability.REASONING,
            AgentCapability.ANALYSIS,
            AgentCapability.IMAGE_ANALYSIS
        ],
        context_window=200000,
        concurrent_capacity=2
    ))
    
    # GPT agents
    agents.append(AIAgent(
        agent_id="gpt4_turbo",
        agent_type=AgentType.GPT_4,
        name="GPT-4 Turbo",
        capabilities=[
            AgentCapability.TEXT_GENERATION,
            AgentCapability.CODE_GENERATION,
            AgentCapability.REASONING,
            AgentCapability.IMAGE_ANALYSIS
        ],
        context_window=128000,
        concurrent_capacity=3
    ))
    
    agents.append(AIAgent(
        agent_id="gpt35_turbo",
        agent_type=AgentType.GPT_3_5,
        name="GPT-3.5 Turbo",
        capabilities=[
            AgentCapability.TEXT_GENERATION,
            AgentCapability.SUMMARIZATION
        ],
        context_window=16385,
        concurrent_capacity=5
    ))
    
    # Local LLM
    agents.append(AIAgent(
        agent_id="local_llm",
        agent_type=AgentType.LOCAL_LLM,
        name="Local LLM",
        capabilities=[
            AgentCapability.TEXT_GENERATION
        ],
        context_window=4096,
        concurrent_capacity=1
    ))
    
    return agents