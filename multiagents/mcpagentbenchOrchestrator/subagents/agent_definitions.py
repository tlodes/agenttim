"""
Domain-specific agent definitions for MCPAgentBench.
Fine-grained agents (Option A): 16 agents, each connecting to exactly one MCP server.
Coarse-grained agents (Option B): 3 broad agents, each connecting to N MCP servers.
Each agent extends BaseBenchAgent with domain-specific configuration.
All agents share BASE_PROMPT from domain_config.py — the only
variable across architectures is the tool distribution, not the prompt.
"""
from agenttim.multiagents.mcpagentbenchOrchestrator.subagents.base_agent import BaseBenchAgent
from agenttim.mcpservers.mcpagentbench.domain_config import COARSE_AGENT_GROUPS
class WeatherAgent(BaseBenchAgent):

    DOMAIN = "weather"

    AGENT_NAME = "Weather Agent"
class TravelAgent(BaseBenchAgent):

    DOMAIN = "travel"

    AGENT_NAME = "Travel Agent"
class CalendarAgent(BaseBenchAgent):

    DOMAIN = "calendar"

    AGENT_NAME = "Calendar Agent"
class DiningAgent(BaseBenchAgent):

    DOMAIN = "dining"

    AGENT_NAME = "Dining Agent"
class FinanceAgent(BaseBenchAgent):

    DOMAIN = "finance"

    AGENT_NAME = "Finance Agent"
class HealthAgent(BaseBenchAgent):

    DOMAIN = "health"

    AGENT_NAME = "Health Agent"
class CodeAgent(BaseBenchAgent):

    DOMAIN = "code"

    AGENT_NAME = "Code Agent"
class EntertainmentAgent(BaseBenchAgent):

    DOMAIN = "entertainment"

    AGENT_NAME = "Entertainment Agent"
class MediaAgent(BaseBenchAgent):

    DOMAIN = "media"

    AGENT_NAME = "Media Agent"
class DataAgent(BaseBenchAgent):

    DOMAIN = "data"

    AGENT_NAME = "Data Agent"
class GeoAgent(BaseBenchAgent):

    DOMAIN = "geo"

    AGENT_NAME = "Geo Agent"
class ShoppingAgent(BaseBenchAgent):

    DOMAIN = "shopping"

    AGENT_NAME = "Shopping Agent"
class LifestyleAgent(BaseBenchAgent):

    DOMAIN = "lifestyle"

    AGENT_NAME = "Lifestyle Agent"
class ContentAgent(BaseBenchAgent):

    DOMAIN = "content"

    AGENT_NAME = "Content Agent"
class SimulationAgent(BaseBenchAgent):

    DOMAIN = "simulation"

    AGENT_NAME = "Simulation Agent"
class UtilitiesAgent(BaseBenchAgent):

    DOMAIN = "utilities"

    AGENT_NAME = "Utilities Agent"
AGENT_REGISTRY: dict[str, type[BaseBenchAgent]] = {

    "weather": WeatherAgent,

    "travel": TravelAgent,

    "calendar": CalendarAgent,

    "dining": DiningAgent,

    "finance": FinanceAgent,

    "health": HealthAgent,

    "code": CodeAgent,

    "entertainment": EntertainmentAgent,

    "media": MediaAgent,

    "data": DataAgent,

    "geo": GeoAgent,

    "shopping": ShoppingAgent,

    "lifestyle": LifestyleAgent,

    "content": ContentAgent,

    "simulation": SimulationAgent,

    "utilities": UtilitiesAgent,
}
class DailyLifeAgent(BaseBenchAgent):

    DOMAINS = COARSE_AGENT_GROUPS["daily_life"]["domains"]

    AGENT_NAME = "Daily Life Agent"
class ProfessionalAgent(BaseBenchAgent):

    DOMAINS = COARSE_AGENT_GROUPS["professional"]["domains"]

    AGENT_NAME = "Professional Agent"
class MediaEntertainmentAgent(BaseBenchAgent):

    DOMAINS = COARSE_AGENT_GROUPS["media"]["domains"]

    AGENT_NAME = "Media & Entertainment Agent"
COARSE_AGENT_REGISTRY: dict[str, type[BaseBenchAgent]] = {

    "daily_life": DailyLifeAgent,

    "professional": ProfessionalAgent,

    "media": MediaEntertainmentAgent,
}

