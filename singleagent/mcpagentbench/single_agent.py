"""
MCPAgentBench Single Agent - Per-test-case tool sampling.
Loads all 141 tools from the 16 domain MCP servers once at startup,
then per test case creates a ReAct agent with a subset of ~40 tools:
- The correct tools for the task (from their domains)
- Random distractor domains until ~40 tools are reached
This mirrors the original MCPAgentBench paper methodology where each task
gets the correct tools plus random distractors, adapted to domain-level
sampling since our MCP servers group tools by domain.
Reference: MCPAgentBench (Liu et al., 2025) - arxiv.org/abs/2512.24565
  Original: 40 individual tool servers per task (random.sample)
  Ours: correct domains + distractor domains ≈ 40 tools per task
"""
import random
import time
from typing import Any, Callable, Dict, List, Optional
from langchain_core.tools import BaseTool
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.config.settings import Settings
from agenttim.mcpservers.mcpagentbench.domain_config import (

    ALL_DOMAINS,

    BASE_PROMPT,

    DOMAIN_TOOLS,

    get_tool_to_domain_map,
)
from .combined_mcp_client import CombinedBenchMCPClient
DEFAULT_NUM_TOOLS = 40
ToolCallCallback = Callable[[str, Dict[str, Any], str], None]
class MCPBenchSingleAgent(ReactEvalAgent):

    """
    Single agent with domain-level tool sampling per test case.

    At startup, connects to all 16 domain MCP servers and loads all 141 tools.
    For each test case, selects a subset of tools (~40) by:
    1. Including all tools from domains that contain the correct tools
    2. Adding tools from random distractor domains until target count is reached
    3. Shuffling the tool list

    Args:
        settings: Application settings
        num_tools: Target number of tools per test case (default: 40)
        logger: Optional logger
        on_tool_call: Optional callback for tool tracking

    Example:
        ```python
        agent = MCPBenchSingleAgent(settings, num_tools=40)
        await agent.initialize()

        # Per test case: create agent with sampled tools
        response = await agent.run_test_case(test_case, verbose=True)
        ```
    """

    SYSTEM_PROMPT = ""

    def __init__(

        self,

        settings: Settings,

        num_tools: int = DEFAULT_NUM_TOOLS,

        logger: Optional[Any] = None,

        on_tool_call: Optional[ToolCallCallback] = None,

    ):

        super().__init__(settings, logger_name="MCPBenchSingle", logger=logger)

        self.num_tools = num_tools

        self.on_tool_call = on_tool_call

        self._mcp_client: Optional[CombinedBenchMCPClient] = None

        self._all_tools: Dict[str, BaseTool] = {}

        self._tools_by_domain: Dict[str, List[BaseTool]] = {}

        self._tool_to_domain = get_tool_to_domain_map()

    async def _do_initialize(self) -> None:

        """Load all 141 tools from the 16 domain MCP servers."""

        self._mcp_client = CombinedBenchMCPClient(self.settings)

        all_tools = await self._mcp_client.get_tools()

        for tool in all_tools:

            self._all_tools[tool.name] = tool

        for domain in ALL_DOMAINS:

            domain_tool_names = DOMAIN_TOOLS[domain]

            self._tools_by_domain[domain] = [

                self._all_tools[name]

                for name in domain_tool_names

                if name in self._all_tools

            ]

        self.logger.info(

            f"Loaded {len(self._all_tools)} tools across "

            f"{len(self._tools_by_domain)} domains"

        )

    def _sample_tools_for_test_case(

        self, test_case: Dict[str, Any],

    ) -> List[BaseTool]:

        """Sample tools for a test case: correct domains + distractor domains.

        Mirrors MCPAgentBench paper methodology adapted to domain-level sampling.

        Args:
            test_case: Test case dict with expected_tool_calls

        Returns:
            Shuffled list of ~num_tools BaseTool objects
        """

        expected_calls = test_case.get("expected_tool_calls", [])

        correct_tool_names = {call["name"] for call in expected_calls}

        correct_domains = set()

        for tool_name in correct_tool_names:

            domain = self._tool_to_domain.get(tool_name)

            if domain:

                correct_domains.add(domain)

        selected_tools = []

        for domain in correct_domains:

            selected_tools.extend(self._tools_by_domain.get(domain, []))

        remaining_domains = [d for d in ALL_DOMAINS if d not in correct_domains]

        random.shuffle(remaining_domains)

        for domain in remaining_domains:

            if len(selected_tools) >= self.num_tools:

                break

            selected_tools.extend(self._tools_by_domain.get(domain, []))

        random.shuffle(selected_tools)

        return selected_tools

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        *,

        test_case: Optional[Dict[str, Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Configure agent with sampled tools for a new test case.

        Args:
            tools: Pre-sampled tools (if None, sampled from test_case).
            test_case: Test case dict used for sampling and prompt generation.
        """

        super().setup_for_test_case()

        if tools is not None:

            sampled_tools = list(tools)

        elif test_case is not None:

            sampled_tools = self._sample_tools_for_test_case(test_case)

        else:

            sampled_tools = []

        self._tools = sampled_tools

        self._create_react_agent(sampled_tools, system_prompt=BASE_PROMPT)

        self.logger.info(f"Setup for test case: {len(sampled_tools)} tools")

    async def run_test_case(

        self,

        test_case: Dict[str, Any],

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> Dict[str, Any]:

        """Run a single test case with sampled tools.

        Convenience method that handles tool sampling, agent setup, and
        execution in one call. Delegates to setup_for_test_case() + run_turn().

        Args:
            test_case: Test case dict with 'input', 'expected_tool_calls', etc.
            callbacks: LangGraph callbacks (e.g. [ToolTracker(), TokenTracker()])
            verbose: Show tool calls and reasoning

        Returns:
            Dict with actual_output, latency, num_tools_available, domains_loaded
        """

        self._ensure_initialized()

        sampled_tools = self._sample_tools_for_test_case(test_case)

        self.setup_for_test_case(tools=sampled_tools, test_case=test_case)

        if verbose:

            expected_calls = test_case.get("expected_tool_calls", [])

            correct_names = {c["name"] for c in expected_calls}

            print(f"    Tools: {len(sampled_tools)} loaded ({len(correct_names)} correct)")

        start_time = time.perf_counter()

        actual_output = await self.run_turn(

            test_case["input"], callbacks=callbacks, verbose=verbose,

        )

        latency = time.perf_counter() - start_time

        if verbose:

            print(f"    Response: {actual_output[:100]}...")

        loaded_domains = set()

        for t in sampled_tools:

            d = self._tool_to_domain.get(t.name)

            if d:

                loaded_domains.add(d)

        return {

            "actual_output": actual_output,

            "latency": latency,

            "num_tools_available": len(sampled_tools),

            "domains_loaded": sorted(loaded_domains),

        }

    def get_tool_count(self) -> int:

        """Get total number of loaded tools (all domains)."""

        return len(self._all_tools)

    def get_available_tools(self) -> list[str]:

        """Get names of all loaded tools."""

        return list(self._all_tools.keys())

