"""Tests for StatefulEvalAgent — history management, snapshot/restore, error handling.
These tests use a concrete stub that implements _execute_turn() and _do_initialize()
without any real LLM or MCP connection.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from agenttim.agents.base import StatefulEvalAgent
class StubAgent(StatefulEvalAgent):

    """Minimal concrete agent for testing base class behavior."""

    def __init__(self, execute_fn=None):

        self._settings_stub = MagicMock()

        self._settings_stub.SERVICE_NAME = "test"

        super().__init__(self._settings_stub, logger_name="StubAgent")

        self._execute_fn = execute_fn or self._default_execute

        self._initialized = True

    async def _do_initialize(self):

        pass

    async def _execute_turn(self, user_message, callbacks=None, verbose=False):

        return await self._execute_fn(user_message, callbacks, verbose)

    @staticmethod

    async def _default_execute(user_message, callbacks=None, verbose=False):

        return f"Response to: {user_message}", None
class FailingAgent(StubAgent):

    """Agent whose _execute_turn always raises."""

    def __init__(self, error=None):

        super().__init__()

        self._error = error or RuntimeError("Turn exploded")

    async def _execute_turn(self, user_message, callbacks=None, verbose=False):

        raise self._error
class TestHistoryManagement:

    @pytest.mark.asyncio

    async def test_run_turn_appends_user_and_assistant(self):

        agent = StubAgent()

        response = await agent.run_turn("Hello")

        history = agent.get_conversation_history()

        assert len(history) == 2

        assert history[0] == {"role": "user", "content": "Hello"}

        assert history[1] == {"role": "assistant", "content": "Response to: Hello"}

    @pytest.mark.asyncio

    async def test_multi_turn_builds_history(self):

        agent = StubAgent()

        await agent.run_turn("Turn 1")

        await agent.run_turn("Turn 2")

        await agent.run_turn("Turn 3")

        history = agent.get_conversation_history()

        assert len(history) == 6

        assert history[0]["content"] == "Turn 1"

        assert history[2]["content"] == "Turn 2"

        assert history[4]["content"] == "Turn 3"

    @pytest.mark.asyncio

    async def test_clear_conversation_history(self):

        agent = StubAgent()

        await agent.run_turn("Hello")

        assert len(agent.get_conversation_history()) == 2

        agent.clear_conversation_history()

        assert len(agent.get_conversation_history()) == 0

    @pytest.mark.asyncio

    async def test_get_conversation_history_returns_copy(self):

        agent = StubAgent()

        await agent.run_turn("Hello")

        history = agent.get_conversation_history()

        history.clear()

        assert len(agent.get_conversation_history()) == 2

    @pytest.mark.asyncio

    async def test_setup_for_test_case_clears_history(self):

        agent = StubAgent()

        await agent.run_turn("Old turn")

        assert len(agent.get_conversation_history()) == 2

        agent.setup_for_test_case()

        assert len(agent.get_conversation_history()) == 0
class TestSnapshotRestore:

    @pytest.mark.asyncio

    async def test_error_restores_history_to_pre_turn_state(self):

        agent = FailingAgent()

        agent._initialized = True

        agent._conversation_history = [

            {"role": "user", "content": "Turn 1"},

            {"role": "assistant", "content": "OK"},

        ]

        with pytest.raises(RuntimeError, match="Turn exploded"):

            await agent.run_turn("Turn 2 that fails")

        history = agent.get_conversation_history()

        assert len(history) == 2

        assert history[0]["content"] == "Turn 1"

        assert history[1]["content"] == "OK"

    @pytest.mark.asyncio

    async def test_error_does_not_leave_partial_user_message(self):

        agent = FailingAgent()

        with pytest.raises(RuntimeError):

            await agent.run_turn("This will fail")

        assert len(agent.get_conversation_history()) == 0

    @pytest.mark.asyncio

    async def test_can_continue_after_error(self):

        """After a failed turn, the next turn should work with clean history."""

        call_count = 0

        async def fail_then_succeed(msg, callbacks=None, verbose=False):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                raise RuntimeError("First call fails")

            return f"Success: {msg}", None

        agent = StubAgent(execute_fn=fail_then_succeed)

        with pytest.raises(RuntimeError):

            await agent.run_turn("Attempt 1")

        assert len(agent.get_conversation_history()) == 0

        response = await agent.run_turn("Attempt 2")

        assert response == "Success: Attempt 2"

        assert len(agent.get_conversation_history()) == 2
class TestChatAlias:

    @pytest.mark.asyncio

    async def test_chat_calls_run_turn(self):

        agent = StubAgent()

        response = await agent.chat("Hello via chat")

        assert response == "Response to: Hello via chat"

        assert len(agent.get_conversation_history()) == 2

    @pytest.mark.asyncio

    async def test_chat_passes_callbacks(self):

        received_callbacks = []

        async def capture_callbacks(msg, callbacks=None, verbose=False):

            received_callbacks.append(callbacks)

            return "OK", None

        agent = StubAgent(execute_fn=capture_callbacks)

        mock_cb = MagicMock()

        await agent.chat("Hello", callbacks=[mock_cb])

        assert received_callbacks[0] == [mock_cb]
class TestCallbackPropagation:

    @pytest.mark.asyncio

    async def test_callbacks_passed_to_execute_turn(self):

        received_callbacks = []

        async def capture(msg, callbacks=None, verbose=False):

            received_callbacks.append(callbacks)

            return "OK", None

        agent = StubAgent(execute_fn=capture)

        mock_tracker = MagicMock()

        mock_token = MagicMock()

        await agent.run_turn("Hello", callbacks=[mock_tracker, mock_token])

        assert len(received_callbacks) == 1

        assert received_callbacks[0] == [mock_tracker, mock_token]

    @pytest.mark.asyncio

    async def test_callbacks_none_by_default(self):

        received_callbacks = []

        async def capture(msg, callbacks=None, verbose=False):

            received_callbacks.append(callbacks)

            return "OK", None

        agent = StubAgent(execute_fn=capture)

        await agent.run_turn("Hello")

        assert received_callbacks[0] is None
class TestInitializationGuard:

    @pytest.mark.asyncio

    async def test_run_turn_raises_if_not_initialized(self):

        agent = StubAgent()

        agent._initialized = False

        with pytest.raises(RuntimeError, match="not initialized"):

            await agent.run_turn("Hello")

    @pytest.mark.asyncio

    async def test_chat_raises_if_not_initialized(self):

        agent = StubAgent()

        agent._initialized = False

        with pytest.raises(RuntimeError, match="not initialized"):

            await agent.chat("Hello")

