"""
BFCL Single Agent - Multi-turn with all 128 tools.
Loads tools from BFCL Python class instances (not MCP servers).
Processes multi-turn test cases by maintaining conversation history
across turns while tools mutate shared class instances.
Usage:
    agent = BFCLSingleAgent(settings)
    await agent.initialize()

    # Per test case:
    agent.setup_for_test_case(tools)

    for turn in test_case["turns"]:
        response = await agent.run_turn(turn["input"], callbacks=[tracker])

    agent.clear_conversation_history()
"""
from typing import Any, List, Optional
from langchain_core.tools import BaseTool
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.bfcl.domain_config import BASE_PROMPT
from agenttim.config.settings import Settings
class BFCLSingleAgent(ReactEvalAgent):

    """Single agent for BFCL multi-turn evaluation.

    All 128 BFCL tools loaded into one ReAct agent.
    Tools are set per test case via setup_for_test_case().
    """

    SYSTEM_PROMPT = BASE_PROMPT

    RECURSION_LIMIT = 20

    def __init__(

        self,

        settings: Settings,

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name="BFCLSingle", logger=logger)

    async def _do_initialize(self) -> None:

        """LLM is ready. Tools are loaded per test case, not at init."""

        pass

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Configure agent with tools for a new test case."""

        super().setup_for_test_case()

        self._tools = tools or []

        self._create_react_agent(self._tools)

        self.logger.info(f"Setup for test case: {len(self._tools)} tools")

