"""
Domain-specific agent definitions for BFCL evaluation.
8 agents, one per BFCL API class. All share BASE_PROMPT from
bfcl/domain_config.py — the only variable across architectures
is the tool distribution, not the prompt.
"""
from agenttim.multiagents.bfclOrchestrator.subagents.base_agent import BaseBFCLAgent
class FilesystemAgent(BaseBFCLAgent):

    DOMAIN = "filesystem"

    AGENT_NAME = "Filesystem Agent"
class MathAgent(BaseBFCLAgent):

    DOMAIN = "math"

    AGENT_NAME = "Math Agent"
class MessagingAgent(BaseBFCLAgent):

    DOMAIN = "messaging"

    AGENT_NAME = "Messaging Agent"
class SocialAgent(BaseBFCLAgent):

    DOMAIN = "social"

    AGENT_NAME = "Social Media Agent"
class TicketingAgent(BaseBFCLAgent):

    DOMAIN = "ticketing"

    AGENT_NAME = "Ticketing Agent"
class TradingAgent(BaseBFCLAgent):

    DOMAIN = "trading"

    AGENT_NAME = "Trading Agent"
class TravelAgent(BaseBFCLAgent):

    DOMAIN = "travel"

    AGENT_NAME = "Travel Agent"
class VehicleAgent(BaseBFCLAgent):

    DOMAIN = "vehicle"

    AGENT_NAME = "Vehicle Agent"
AGENT_REGISTRY: dict[str, type[BaseBFCLAgent]] = {

    "filesystem": FilesystemAgent,

    "math": MathAgent,

    "messaging": MessagingAgent,

    "social": SocialAgent,

    "ticketing": TicketingAgent,

    "trading": TradingAgent,

    "travel": TravelAgent,

    "vehicle": VehicleAgent,
}

