"""Shared constants for evaluation scripts."""
from typing import Dict
ORCHESTRATOR_TOOLS = {"delegate_to_subagent", "load_skill"}
ORCHESTRATOR_TOOL_PREFIXES = ("transfer_to_",)
ORCHESTRATOR_DOMAIN_NAMES = {

    "weather", "travel", "calendar", "dining", "finance", "health", "code",

    "entertainment", "media", "data", "geo", "shopping", "lifestyle", "content",

    "simulation", "utilities",

    "filesystem", "communication", "productivity", "social", "sports",

    "email", "message",

    "daily_life", "professional",

    "router",
}
def is_orchestrator_tool(tool_name: str) -> bool:

    """Check if a tool is an orchestrator/coordination tool (not an actual MCP tool).

    Returns True for:
    - "delegate_to_subagent", "load_skill" (exact matches)
    - "transfer_to_*" (Handoff pattern - e.g., transfer_to_router)
    - "{domain}_agent" where domain is a known orchestrator domain
      (e.g., entertainment_agent, weather_agent - but NOT octagon_companies_agent)
    """

    if tool_name in ORCHESTRATOR_TOOLS:

        return True

    for prefix in ORCHESTRATOR_TOOL_PREFIXES:

        if tool_name.startswith(prefix):

            return True

    if tool_name.endswith("_agent"):

        domain = tool_name[:-6]

        if domain in ORCHESTRATOR_DOMAIN_NAMES:

            return True

    return False
INTERNAL_KEYS = {"runtime", "__pregel_context", "config"}
MODEL_PRICING: Dict[str, Dict[str, float]] = {

    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},

    "gpt-5.4-nano": {"input": 0.20, "output": 1.25},

    "gpt-5.4": {"input": 2.50, "output": 15.00},

    "gpt-5.4-pro": {"input": 30.00, "output": 270.00},

    "gpt-5.5": {"input": 5.00, "output": 30.00},

    "gpt-5.5-pro": {"input": 30.00, "output": 180.00},

    "june-gpt-5-4-mini-datazone": {"input": 0.75, "output": 4.50},

    "june-gpt-5-4-datazone": {"input": 2.50, "output": 15.00},

    "deepseek/deepseek-v4-pro": {"input": 0.435, "output": 0.87},

    "june-gpt-4-1-mini-datazone": {"input": 0.40, "output": 1.60},

    "june-gpt-4-1-datazone": {"input": 2.00, "output": 8.00},

    "gpt-4o-mini": {"input": 0.15, "output": 0.60},

    "gpt-4o": {"input": 2.50, "output": 10.00},
}
HOSTING_PRICING: Dict[str, Dict[str, float]] = {

    "llama-3.1-70b": {"cost_per_second": 0.00125},

    "llama-3.1-405b": {"cost_per_second": 0.00250},

    "llama-3.1-8b": {"cost_per_second": 0.00056},

    "mistral-7b": {"cost_per_second": 0.00056},

    "mistral-7b-t4": {"cost_per_second": 0.00042},

    "local": {"cost_per_second": 0.0},
}

