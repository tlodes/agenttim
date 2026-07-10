"""ReactEvalAgent — Base for agents using LangGraph's create_agent (ReAct pattern).
Handles:
- Agent creation via create_agent()
- Default _execute_turn() with ainvoke + timeout
- Verbose streaming (defined once for all agents)
"""
from __future__ import annotations
import asyncio
from typing import Any, List, Optional
import functools
from langchain_core.tools import BaseTool, StructuredTool
from langchain.agents import create_agent
from langgraph.errors import GraphRecursionError
from agenttim.agents.base import StatefulEvalAgent
from agenttim.config.settings import Settings
class ReactEvalAgent(StatefulEvalAgent):

    """Base for agents using LangGraph's create_agent (ReAct pattern).

    Subclasses set SYSTEM_PROMPT and implement _do_initialize() to load tools.
    The ReAct execution logic (ainvoke, verbose streaming, error handling)
    is defined once here.
    """

    SYSTEM_PROMPT: str = ""

    RECURSION_LIMIT: int = 20

    def __init__(

        self,

        settings: Settings,

        logger_name: str,

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name, logger)

        self._agent: Any = None

        self._tools: List[BaseTool] = []

    @staticmethod

    def _wrap_tool_safe(tool: BaseTool) -> BaseTool:

        """Wrap a tool so client-side exceptions become error responses.

        MCP tools can throw exceptions on the client side (connection errors,
        serialization failures, timeouts). Without wrapping, these break the
        ReAct loop — the ToolNode never creates a ToolMessage, leaving an
        orphaned tool_calls entry that causes an OpenAI 400 error.

        This wrapper catches any exception and returns an error string,
        keeping the ReAct loop intact. The LLM sees the error and can
        decide to retry or proceed.
        """

        original_coroutine = getattr(tool, "coroutine", None)

        original_func = getattr(tool, "func", None)

        if original_coroutine:

            @functools.wraps(original_coroutine)

            async def safe_coroutine(*args, **kwargs):

                try:

                    return await original_coroutine(*args, **kwargs)

                except Exception as e:

                    return f"Error: {type(e).__name__}: {e}"

            return StructuredTool(

                name=tool.name,

                description=tool.description,

                args_schema=tool.args_schema,

                coroutine=safe_coroutine,

            )

        elif original_func:

            @functools.wraps(original_func)

            def safe_func(*args, **kwargs):

                try:

                    return original_func(*args, **kwargs)

                except Exception as e:

                    return f"Error: {type(e).__name__}: {e}"

            return StructuredTool(

                name=tool.name,

                description=tool.description,

                args_schema=tool.args_schema,

                func=safe_func,

            )

        return tool

    def _create_react_agent(

        self,

        tools: List[BaseTool],

        callbacks: Optional[List[Any]] = None,

        system_prompt: Optional[str] = None,

        **kwargs: Any,

    ) -> None:

        """Create/recreate the ReAct agent with safe-wrapped tools.

        Args:
            tools: Tools to bind to the agent.
            callbacks: Optional callbacks to bind to the LLM.
            system_prompt: Override for SYSTEM_PROMPT.
            **kwargs: Extra kwargs passed to create_agent().
        """

        safe_tools = [self._wrap_tool_safe(t) for t in tools]

        agent_name = getattr(self, "AGENT_NAME", "") or self.__class__.__name__

        llm_config: dict[str, Any] = {

            "metadata": {"agent_name": agent_name},

        }

        if callbacks:

            llm_config["callbacks"] = callbacks

        llm = self._llm.with_config(llm_config)

        self._agent = create_agent(

            llm,

            tools=safe_tools,

            system_prompt=system_prompt or self.SYSTEM_PROMPT,

            **kwargs,

        )

        self._agent = self._agent.with_config(

            {"recursion_limit": self.RECURSION_LIMIT}

        )

    async def _execute_turn(

        self,

        user_message: str,

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> tuple[str, list | None]:

        """Default ReAct execution: ainvoke with conversation history.

        Returns (response_text, full_messages) where full_messages is the
        complete message list from the agent graph, including tool_calls
        and ToolMessages. This is critical for multi-turn evaluation.
        """

        agent_name = getattr(self, "AGENT_NAME", "") or self.__class__.__name__

        invoke_config: dict[str, Any] = {

            "recursion_limit": self.RECURSION_LIMIT,

            "metadata": {"agent_name": agent_name},

        }

        if callbacks:

            invoke_config["callbacks"] = callbacks

        try:

            if verbose:

                return await self._execute_verbose(invoke_config)

            result = await asyncio.wait_for(

                self._agent.ainvoke(

                    {"messages": self._conversation_history},

                    config=invoke_config,

                ),

                timeout=self.TURN_TIMEOUT,

            )

            response_text = result["messages"][-1].text

            return response_text, result["messages"]

        except GraphRecursionError:

            self.logger.warning("Turn hit recursion limit (too many tool calls)")

            return "Reached maximum steps for this turn.", None

    async def _execute_verbose(self, invoke_config: dict) -> tuple[str, list | None]:

        """Verbose execution with step-by-step logging. Defined ONCE."""

        final_response = ""

        all_messages = list(self._conversation_history)

        step = 0

        async for chunk in self._agent.astream(

            {"messages": self._conversation_history},

            config=invoke_config,

        ):

            for node_name, node_data in chunk.items():

                step += 1

                if "messages" not in node_data:

                    continue

                for msg in node_data["messages"]:

                    all_messages.append(msg)

                    if hasattr(msg, "tool_calls") and msg.tool_calls:

                        for tc in msg.tool_calls:

                            print(f"    Step {step}: {tc['name']}({tc['args']})")

                    elif hasattr(msg, "content") and msg.content:

                        final_response = msg.content

        return final_response, all_messages

    def get_tool_count(self) -> int:

        return len(self._tools)

    def get_available_tools(self) -> list[str]:

        return [t.name for t in self._tools]

