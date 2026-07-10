"""LangChain callback handler for tracking tool invocations with latency."""
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain_core.callbacks import AsyncCallbackHandler
class ToolTracker(AsyncCallbackHandler):

    """
    LangChain callback handler that captures every tool invocation with latency.

    LangGraph automatically propagates callbacks through the entire agent graph,
    so this tracker sees tool calls from the orchestrator AND all subagents
    without any production code modification.

    Also tracks tool errors via on_tool_error for post-run diagnostics.
    """

    def __init__(self):

        self.calls: List[Dict[str, Any]] = []

        self.errors: List[Dict[str, Any]] = []

        self._tool_start_times: Dict[UUID, float] = {}

        self._first_start: Optional[float] = None

    async def on_tool_start(

        self,

        serialized: Dict[str, Any],

        input_str: str,

        *,

        run_id: UUID,

        inputs: Optional[Dict[str, Any]] = None,

        **kwargs: Any,

    ) -> None:

        now = time.perf_counter()

        if self._first_start is None:

            self._first_start = now

        self._tool_start_times[run_id] = now

        tool_name = serialized.get("name", "<unknown>")

        args = inputs if isinstance(inputs, dict) else {"input": input_str}

        self.calls.append({

            "name": tool_name,

            "args": args,

            "output": "",

            "run_id": run_id,

            "start_time": round(now - self._first_start, 3),

            "latency": 0.0,

        })

    async def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> None:

        for call in reversed(self.calls):

            if call.get("run_id") == run_id:

                call["output"] = str(output)[:200]

                if run_id in self._tool_start_times:

                    call["latency"] = time.perf_counter() - self._tool_start_times.pop(run_id)

                break

    async def on_tool_error(

        self, error: BaseException, *, run_id: UUID, **kwargs: Any,

    ) -> None:

        tool_name = "<unknown>"

        tool_args = {}

        for call in reversed(self.calls):

            if call.get("run_id") == run_id:

                tool_name = call["name"]

                tool_args = call.get("args", {})

                call["error"] = str(error)[:500]

                if run_id in self._tool_start_times:

                    call["latency"] = time.perf_counter() - self._tool_start_times.pop(run_id)

                break

        self.errors.append({

            "tool": tool_name,

            "error": str(error)[:1000],

            "error_type": type(error).__name__,

            "args": {k: str(v)[:200] for k, v in tool_args.items()} if isinstance(tool_args, dict) else {},

            "timestamp": round(time.perf_counter() - self._first_start, 3) if self._first_start else 0,

        })

