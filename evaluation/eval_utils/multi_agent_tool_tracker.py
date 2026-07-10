"""Shared MultiAgentToolTracker for all benchmark evaluation scripts.
Tracks tool calls with agent attribution for multi-agent architectures.
Used by BFCL and MCPAgentBench evaluation scripts.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain_core.callbacks import AsyncCallbackHandler
from .constants import is_orchestrator_tool
from .utils import sanitize_args
from .multi_agent_metrics import (

    AgentMessage,

    MultiAgentToolCall,
)
class MultiAgentToolTracker(AsyncCallbackHandler):

    """Extended tracker that captures agent attribution for multi-agent eval.

    Tracks which subagent called each tool, records delegation messages,
    and provides filtered views of MCP-only calls.
    """

    def __init__(self):

        self.calls: List[Dict[str, Any]] = []

        self.errors: List[Dict[str, Any]] = []

        self.messages: List[AgentMessage] = []

        self._tool_start_times: Dict[UUID, float] = {}

        self._first_start: Optional[float] = None

        self._current_agent: str = "orchestrator"

        self._delegation_count: int = 0

    def _is_delegation_tool(self, tool_name: str) -> bool:

        return is_orchestrator_tool(tool_name)

    def _extract_agent_name(self, tool_name: str) -> str:

        if tool_name == "delegate_to_subagent":

            return "subagent"

        if tool_name.endswith("_agent"):

            return tool_name[:-6]

        if tool_name.startswith("transfer_to_"):

            return tool_name[12:]

        return tool_name

    async def on_tool_start(

        self, serialized: Dict[str, Any], input_str: str, *,

        run_id: UUID, inputs: Optional[Dict[str, Any]] = None, **kwargs: Any,

    ) -> None:

        now = time.perf_counter()

        if self._first_start is None:

            self._first_start = now

        self._tool_start_times[run_id] = now

        tool_name = serialized.get("name", "<unknown>")

        args = inputs if isinstance(inputs, dict) else {"input": input_str}

        if self._is_delegation_tool(tool_name):

            agent_name = self._extract_agent_name(tool_name)

            self._current_agent = agent_name

            self._delegation_count += 1

            content = args.get("task_description") or args.get("request") or str(args)[:500]

            self.messages.append(AgentMessage(

                sender="orchestrator", recipient=agent_name,

                content=content[:500],

                message_type="delegation",

                timestamp=now - self._first_start,

                token_count=len(content.split()),

            ))

        self.calls.append({

            "name": tool_name, "args": args, "output": "",

            "run_id": run_id, "start_time": round(now - self._first_start, 3),

            "latency": 0.0, "agent_id": self._current_agent,

        })

    async def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> None:

        for call in reversed(self.calls):

            if call.get("run_id") == run_id:

                output_str = str(output)[:500]

                call["output"] = output_str

                if run_id in self._tool_start_times:

                    call["latency"] = time.perf_counter() - self._tool_start_times.pop(run_id)

                if self._is_delegation_tool(call["name"]):

                    self.messages.append(AgentMessage(

                        sender=call["agent_id"], recipient="orchestrator",

                        content=output_str, message_type="result",

                        timestamp=call["start_time"] + call["latency"],

                        token_count=len(output_str.split()),

                    ))

                    self._current_agent = "orchestrator"

                break

    async def on_tool_error(

        self, error: BaseException, *, run_id: UUID, **kwargs: Any,

    ) -> None:

        tool_name = "<unknown>"

        tool_args = {}

        agent_id = self._current_agent

        for call in reversed(self.calls):

            if call.get("run_id") == run_id:

                tool_name = call["name"]

                tool_args = call.get("args", {})

                agent_id = call.get("agent_id", self._current_agent)

                call["error"] = str(error)[:500]

                if run_id in self._tool_start_times:

                    call["latency"] = time.perf_counter() - self._tool_start_times.pop(run_id)

                break

        self.errors.append({

            "tool": tool_name,

            "agent": agent_id,

            "error": str(error)[:1000],

            "error_type": type(error).__name__,

            "args": {k: str(v)[:200] for k, v in tool_args.items()} if isinstance(tool_args, dict) else {},

            "timestamp": round(time.perf_counter() - self._first_start, 3) if self._first_start else 0,

        })

    def get_mcp_calls(self) -> List[Dict[str, Any]]:

        """Return only MCP tool calls (excludes delegation/orchestrator tools)."""

        return [c for c in self.calls if not is_orchestrator_tool(c["name"])]

    def get_multi_agent_tool_calls(self) -> List[MultiAgentToolCall]:

        """Convert to MultiAgentToolCall dataclass instances."""

        return [

            MultiAgentToolCall(

                name=c["name"], agent_id=c["agent_id"],

                input_parameters=sanitize_args(c["args"]),

                output=c.get("output", ""), success=True,

                execution_time_ms=c["latency"] * 1000,

                timestamp=c["start_time"],

            )

            for c in self.get_mcp_calls()

        ]

    @property

    def total_turns(self) -> int:

        """Estimate total delegation turns (for multi-agent metrics)."""

        return max(1, self._delegation_count * 2 + 1)

