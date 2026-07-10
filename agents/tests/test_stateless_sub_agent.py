"""Tests for StatelessSubAgent — stateless chat(), error handling, timeout."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agenttim.agents.base import StatelessSubAgent
class StubSubAgent(StatelessSubAgent):

    """Minimal concrete subagent for testing."""

    DOMAIN = "test_domain"

    AGENT_NAME = "TestSubAgent"

    SYSTEM_PROMPT = "You are a test agent."

    TURN_TIMEOUT = 5

    def __init__(self, agent_response="Sub response"):

        settings = MagicMock()

        settings.SERVICE_NAME = "test"

        super().__init__(settings)

        self._initialized = True

        mock_result = {"messages": [MagicMock(text=agent_response)]}

        self._agent = AsyncMock()

        self._agent.ainvoke = AsyncMock(return_value=mock_result)

        self._agent.astream = self._make_astream(agent_response)

    @staticmethod

    def _make_astream(response):

        async def astream(messages, config=None):

            msg = MagicMock()

            msg.content = response

            msg.tool_calls = None

            msg.name = None

            yield {"agent": {"messages": [msg]}}

        return astream

    async def _do_initialize(self):

        pass
class TestStatelessChat:

    @pytest.mark.asyncio

    async def test_chat_returns_response(self):

        agent = StubSubAgent(agent_response="Hello from sub")

        response = await agent.chat("Test query")

        assert response == "Hello from sub"

    @pytest.mark.asyncio

    async def test_chat_does_not_maintain_history(self):

        agent = StubSubAgent()

        await agent.chat("Query 1")

        await agent.chat("Query 2")

        assert not hasattr(agent, "_conversation_history")

    @pytest.mark.asyncio

    async def test_chat_passes_callbacks_to_ainvoke(self):

        agent = StubSubAgent()

        mock_cb = MagicMock()

        await agent.chat("Test", callbacks=[mock_cb])

        _, kwargs = agent._agent.ainvoke.call_args

        assert "callbacks" in kwargs.get("config", {})

        assert mock_cb in kwargs["config"]["callbacks"]

    @pytest.mark.asyncio

    async def test_chat_without_callbacks(self):

        agent = StubSubAgent()

        await agent.chat("Test")

        _, kwargs = agent._agent.ainvoke.call_args

        assert "callbacks" not in kwargs.get("config", {})
class TestSubAgentErrors:

    @pytest.mark.asyncio

    async def test_exception_returns_error_string(self):

        agent = StubSubAgent()

        agent._agent.ainvoke = AsyncMock(side_effect=ValueError("bad input"))

        response = await agent.chat("Test")

        assert "Error in TestSubAgent" in response

        assert "bad input" in response

    @pytest.mark.asyncio

    async def test_timeout_returns_error_string(self):

        agent = StubSubAgent()

        agent.TURN_TIMEOUT = 0.01

        async def slow_invoke(*args, **kwargs):

            await asyncio.sleep(1)

            return {"messages": [MagicMock(text="too late")]}

        agent._agent.ainvoke = slow_invoke

        response = await agent.chat("Test")

        assert "Error in TestSubAgent" in response

        assert "Timed out" in response
class TestDomainConfig:

    def test_get_domains_single(self):

        agent = StubSubAgent()

        assert agent._get_domains() == ["test_domain"]

    def test_get_domains_multiple(self):

        agent = StubSubAgent()

        agent.DOMAINS = ["domain_a", "domain_b"]

        assert agent._get_domains() == ["domain_a", "domain_b"]

    def test_get_domains_prefers_domains_over_domain(self):

        agent = StubSubAgent()

        agent.DOMAIN = "single"

        agent.DOMAINS = ["multi_a", "multi_b"]

        assert agent._get_domains() == ["multi_a", "multi_b"]

