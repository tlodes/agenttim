"""Tests for ReactEvalAgent — create_react_agent, verbose, callback binding.
Tests agent creation and the default _execute_turn flow.
Uses mocked LangGraph to avoid real LLM calls.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agenttim.agents.react_base import ReactEvalAgent
class StubReactAgent(ReactEvalAgent):

    """Minimal concrete ReactEvalAgent for testing."""

    SYSTEM_PROMPT = "You are a test agent."

    RECURSION_LIMIT = 10

    def __init__(self):

        settings = MagicMock()

        settings.SERVICE_NAME = "test"

        super().__init__(settings, logger_name="StubReact")

        self._initialized = True

        self._llm = MagicMock()

        self._llm.with_config = MagicMock(return_value=self._llm)

    async def _do_initialize(self):

        pass
class TestAgentCreation:

    @patch("agenttim.agents.react_base.create_agent")

    def test_create_react_agent_calls_create_agent(self, mock_create):

        agent = StubReactAgent()

        mock_compiled = MagicMock()

        mock_compiled.with_config = MagicMock(return_value=mock_compiled)

        mock_create.return_value = mock_compiled

        mock_tool = MagicMock(spec=[])

        mock_tool.name = "test_tool"

        agent._create_react_agent([mock_tool])

        mock_create.assert_called_once()

        call_kwargs = mock_create.call_args

        assert call_kwargs[1]["system_prompt"] == "You are a test agent."

    @patch("agenttim.agents.react_base.create_agent")

    def test_create_react_agent_with_callbacks_binds_to_llm(self, mock_create):

        agent = StubReactAgent()

        mock_compiled = MagicMock()

        mock_compiled.with_config = MagicMock(return_value=mock_compiled)

        mock_create.return_value = mock_compiled

        mock_cb = MagicMock()

        agent._create_react_agent([], callbacks=[mock_cb])

        agent._llm.with_config.assert_called_with({"callbacks": [mock_cb]})

    @patch("agenttim.agents.react_base.create_agent")

    def test_create_react_agent_sets_recursion_limit(self, mock_create):

        agent = StubReactAgent()

        mock_compiled = MagicMock()

        mock_compiled.with_config = MagicMock(return_value=mock_compiled)

        mock_create.return_value = mock_compiled

        agent._create_react_agent([])

        mock_compiled.with_config.assert_called_with({"recursion_limit": 10})
class TestExecuteTurn:

    @pytest.mark.asyncio

    async def test_execute_turn_invokes_agent(self):

        agent = StubReactAgent()

        mock_result = {"messages": [MagicMock(text="Agent response")]}

        agent._agent = AsyncMock()

        agent._agent.ainvoke = AsyncMock(return_value=mock_result)

        response = await agent._execute_turn("Hello")

        assert response == "Agent response"

        agent._agent.ainvoke.assert_called_once()

    @pytest.mark.asyncio

    async def test_execute_turn_passes_conversation_history(self):

        agent = StubReactAgent()

        agent._conversation_history = [

            {"role": "user", "content": "Prior turn"},

            {"role": "assistant", "content": "Prior response"},

            {"role": "user", "content": "Current turn"},

        ]

        mock_result = {"messages": [MagicMock(text="Response")]}

        agent._agent = AsyncMock()

        agent._agent.ainvoke = AsyncMock(return_value=mock_result)

        await agent._execute_turn("Current turn")

        call_args = agent._agent.ainvoke.call_args[0]

        assert call_args[0]["messages"] == agent._conversation_history

    @pytest.mark.asyncio

    async def test_execute_turn_passes_callbacks_in_config(self):

        agent = StubReactAgent()

        mock_result = {"messages": [MagicMock(text="Response")]}

        agent._agent = AsyncMock()

        agent._agent.ainvoke = AsyncMock(return_value=mock_result)

        agent._tools = []

        agent._create_react_agent = MagicMock()

        mock_cb = MagicMock()

        await agent._execute_turn("Hello", callbacks=[mock_cb])

        _, kwargs = agent._agent.ainvoke.call_args

        assert mock_cb in kwargs["config"]["callbacks"]
class TestRunTurnIntegration:

    @pytest.mark.asyncio

    async def test_run_turn_full_flow(self):

        agent = StubReactAgent()

        mock_result = {"messages": [MagicMock(text="LLM says hi")]}

        agent._agent = AsyncMock()

        agent._agent.ainvoke = AsyncMock(return_value=mock_result)

        agent._tools = []

        agent._create_react_agent = MagicMock()

        response = await agent.run_turn("Hello")

        assert response == "LLM says hi"

        history = agent.get_conversation_history()

        assert len(history) == 2

        assert history[0] == {"role": "user", "content": "Hello"}

        assert history[1] == {"role": "assistant", "content": "LLM says hi"}

    @pytest.mark.asyncio

    async def test_run_turn_error_restores_history(self):

        agent = StubReactAgent()

        agent._agent = AsyncMock()

        agent._agent.ainvoke = AsyncMock(side_effect=RuntimeError("LLM crashed"))

        agent._tools = []

        agent._create_react_agent = MagicMock()

        agent._conversation_history = [

            {"role": "user", "content": "Turn 1"},

            {"role": "assistant", "content": "OK"},

        ]

        with pytest.raises(RuntimeError, match="LLM crashed"):

            await agent.run_turn("Turn 2")

        history = agent.get_conversation_history()

        assert len(history) == 2

        assert history[-1]["content"] == "OK"
class TestToolHelpers:

    def test_get_tool_count(self):

        agent = StubReactAgent()

        mock_tool_a = MagicMock()

        mock_tool_a.name = "tool_a"

        mock_tool_b = MagicMock()

        mock_tool_b.name = "tool_b"

        agent._tools = [mock_tool_a, mock_tool_b]

        assert agent.get_tool_count() == 2

    def test_get_available_tools(self):

        agent = StubReactAgent()

        mock_tool = MagicMock()

        mock_tool.name = "my_tool"

        agent._tools = [mock_tool]

        assert agent.get_available_tools() == ["my_tool"]

    def test_empty_tools(self):

        agent = StubReactAgent()

        agent._tools = []

        assert agent.get_tool_count() == 0

        assert agent.get_available_tools() == []

