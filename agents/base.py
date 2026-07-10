"""Base classes for all evaluation agents.
Provides three base classes:
- BaseEvalAgent: Universal root (settings, logger, LLM, initialize)
- StatefulEvalAgent: Agents with conversation history and run_turn() interface
- StatelessSubAgent: Inner agents called by orchestrators (no history)
"""
from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from typing import Any, List, Optional
from langchain_openai import AzureChatOpenAI
from agenttim.config.settings import Settings
from agenttim.services.llm_service import create_llm
class BaseEvalAgent(ABC):

    """Universal base for all evaluation agents.

    Handles:
    - Settings, logger, LLM instance
    - Idempotent initialization via initialize()
    - Subclasses implement _do_initialize() for domain-specific setup
    """

    def __init__(

        self,

        settings: Settings,

        logger_name: str,

        logger: Optional[Logger] = None,

    ):

        self.settings = settings

        self.logger = logger or getLogger(f"{settings.SERVICE_NAME}.{logger_name}")

        self._llm: Optional[AzureChatOpenAI] = None

        self._initialized: bool = False

    async def initialize(self) -> None:

        """Initialize the agent. Idempotent — safe to call multiple times."""

        if self._initialized:

            return

        self._llm = create_llm(self.settings)

        await self._do_initialize()

        self._initialized = True

        self.logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod

    async def _do_initialize(self) -> None:

        """Subclass hook: load tools, create agents, etc. LLM is already set."""

    @property

    def is_initialized(self) -> bool:

        return self._initialized

    def _ensure_initialized(self) -> None:

        """Raise RuntimeError if not initialized."""

        if not self._initialized:

            raise RuntimeError(

                f"{self.__class__.__name__} not initialized. Call initialize() first."

            )

    def get_tool_count(self) -> int:

        """Override in subclasses that track tools."""

        return 0
class StatefulEvalAgent(BaseEvalAgent):

    """Agent that maintains conversation history across turns.

    Provides a unified run_turn() interface for ALL benchmarks.
    Error handling (snapshot + restore) is defined once here.

    Subclasses implement _execute_turn() with their domain-specific logic.
    """

    TURN_TIMEOUT: int = 120

    def __init__(

        self,

        settings: Settings,

        logger_name: str,

        logger: Optional[Logger] = None,

    ):

        super().__init__(settings, logger_name, logger)

        self._conversation_history: list = []

    def clear_conversation_history(self) -> None:

        """Clear conversation history. Override to reset additional state."""

        self._conversation_history = []

    def get_conversation_history(self) -> list:

        """Return a copy of the conversation history."""

        return list(self._conversation_history)

    async def run_turn(

        self,

        user_message: str,

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> str:

        """Run one conversation turn with history management and error recovery.

        Works for both single-turn and multi-turn evaluation:
        - Single-turn: clear_conversation_history() + run_turn(input)
        - Multi-turn: clear_conversation_history() + run_turn(turn1) + run_turn(turn2) + ...

        For multi-turn, the full message list (including tool_calls and
        ToolMessages) from the agent graph is stored in _conversation_history.
        This gives the LLM complete context in subsequent turns.

        History snapshot/restore prevents corrupted tool_calls messages
        from breaking subsequent turns.
        """

        self._ensure_initialized()

        snapshot = list(self._conversation_history)

        self._conversation_history.append(

            {"role": "user", "content": user_message}

        )

        try:

            response, full_messages = await self._execute_turn(

                user_message, callbacks, verbose,

            )

            if full_messages is not None:

                self._conversation_history = full_messages

            else:

                self._conversation_history.append(

                    {"role": "assistant", "content": response}

                )

            return response

        except Exception:

            self._conversation_history = snapshot

            raise

    @abstractmethod

    async def _execute_turn(

        self,

        user_message: str,

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> tuple[str, list | None]:

        """Execute domain-specific turn logic.

        Returns:
            (response_text, full_messages) where full_messages is the
            complete message list from the agent graph (or None to fall
            back to simple text-only history).

        History management, snapshot/restore, and message appending
        are handled by run_turn().
        """

    async def chat(

        self,

        user_message: str,

        verbose: bool = False,

        callbacks: Optional[List[Any]] = None,

    ) -> str:

        """Alias for run_turn(). Backwards compatible with existing code."""

        return await self.run_turn(user_message, callbacks=callbacks, verbose=verbose)

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Configure agent for a new test case.

        Default: clears history. Subclasses override to accept tools, etc.
        """

        self.clear_conversation_history()
class StatelessSubAgent(BaseEvalAgent):

    """Base for stateless subagents called by orchestrators.

    Subagents don't maintain conversation history. Each chat() call
    is independent. They are called by orchestrators, handoff agents, etc.
    """

    DOMAIN: str = ""

    DOMAINS: list[str] = []

    AGENT_NAME: str = ""

    SYSTEM_PROMPT: str = ""

    RECURSION_LIMIT: int = 20

    TURN_TIMEOUT: int = 120

    _agent: Any = None

    _mcp_client: Any = None

    _current_tools: list | None = None

    def __init__(

        self,

        settings: Settings,

        logger: Optional[Logger] = None,

    ):

        name = self.AGENT_NAME or self.__class__.__name__

        super().__init__(settings, logger_name=name, logger=logger)

    def _get_domains(self) -> list[str]:

        """Return domain list for MCP client."""

        return self.DOMAINS if self.DOMAINS else [self.DOMAIN]

    def _get_system_prompt(self) -> str:

        """Return the system prompt for this agent. Override in subclasses."""

        return self.SYSTEM_PROMPT

    def set_tools(self, tools: list) -> None:

        """Replace tools and rebuild the ReAct agent.

        Handles empty tool lists gracefully (sets agent to None).
        Used by tool-sampling evaluation to restrict tools per test case.
        """

        from langchain.agents import create_agent

        self._current_tools = tools

        if tools:

            agent_name = self.AGENT_NAME or self.__class__.__name__

            llm = self._llm.with_config({"metadata": {"agent_name": agent_name}})

            self._agent = create_agent(

                llm,

                tools=tools,

                system_prompt=self._get_system_prompt(),

            )

        else:

            self._agent = None

        self.logger.info(f"{self.AGENT_NAME} rebuilt with {len(tools)} tools")

    def get_available_tools(self) -> list[str]:

        """Return current tool names (post-sampling if applicable)."""

        if self._current_tools is not None:

            return [t.name for t in self._current_tools]

        if self._mcp_client is None:

            return []

        return self._mcp_client.get_tool_names()

    def get_mcp_client(self):

        return self._mcp_client

    async def chat(

        self,

        user_message: str,

        verbose: bool = False,

        callbacks: Optional[List[Any]] = None,

    ) -> str:

        """Stateless chat. No history management."""

        return await self.chat_with_history(

            user_message, history=[], verbose=verbose, callbacks=callbacks

        )

    async def chat_with_history(

        self,

        user_message: str,

        history: List[Any],

        verbose: bool = False,

        callbacks: Optional[List[Any]] = None,

    ) -> str:

        """Chat with conversation history from parent agent.

        Args:
            user_message: Current user request
            history: Conversation history from parent (can include AIMessage
                     with tool_calls, ToolMessage, etc.)
            verbose: Enable step-by-step logging
            callbacks: LangChain callbacks for token tracking
        """

        self._ensure_initialized()

        invoke_config: dict[str, Any] = {

            "recursion_limit": self.RECURSION_LIMIT,

            "metadata": {"agent_name": self.AGENT_NAME or self.__class__.__name__},

        }

        if callbacks:

            invoke_config["callbacks"] = callbacks

        messages = list(history) + [{"role": "user", "content": user_message}]

        try:

            if verbose:

                return await self._chat_verbose_with_messages(messages, invoke_config)

            result = await asyncio.wait_for(

                self._agent.ainvoke(

                    {"messages": messages},

                    config=invoke_config,

                ),

                timeout=self.TURN_TIMEOUT,

            )

            return result["messages"][-1].text

        except asyncio.TimeoutError:

            self.logger.error(f"{self.AGENT_NAME} timed out after {self.TURN_TIMEOUT}s")

            return f"Error in {self.AGENT_NAME}: Timed out after {self.TURN_TIMEOUT} seconds"

        except Exception as e:

            self.logger.error(f"{self.AGENT_NAME} failed: {e}")

            return f"Error in {self.AGENT_NAME}: {e}"

    async def _chat_verbose(self, user_message: str, invoke_config: dict) -> str:

        """Verbose chat with step-by-step logging (no history)."""

        messages = [{"role": "user", "content": user_message}]

        return await self._chat_verbose_with_messages(messages, invoke_config)

    async def _chat_verbose_with_messages(

        self, messages: list, invoke_config: dict

    ) -> str:

        """Verbose chat with step-by-step logging."""

        label = self._get_domains()[0] if len(self._get_domains()) == 1 else self.AGENT_NAME

        final_response = ""

        step = 0

        async for chunk in self._agent.astream(

            {"messages": messages},

            config=invoke_config,

        ):

            for node_name, node_data in chunk.items():

                step += 1

                if "messages" not in node_data:

                    continue

                for msg in node_data["messages"]:

                    if hasattr(msg, "tool_calls") and msg.tool_calls:

                        for tc in msg.tool_calls:

                            print(f"    [{label}] Step {step}: {tc['name']}({tc['args']})")

                    elif hasattr(msg, "content") and msg.content:

                        final_response = msg.content

        return final_response

