"""LangChain callback handler for tracking token usage and latency."""
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain_core.callbacks import AsyncCallbackHandler
from .constants import MODEL_PRICING, HOSTING_PRICING
from .utils import extract_usage
@dataclass
class StepTokens:

    """Aggregated tokens for a category of LLM steps (tool-call vs response)."""

    prompt_tokens: int = 0

    completion_tokens: int = 0

    cached_tokens: int = 0

    count: int = 0

    @property

    def total_tokens(self) -> int:

        return self.prompt_tokens + self.completion_tokens
@dataclass
class NodeTokenUsage:

    """Token usage breakdown for a single LangGraph node (agent)."""

    prompt_tokens: int = 0

    completion_tokens: int = 0

    cached_tokens: int = 0

    reasoning_tokens: int = 0

    llm_calls: int = 0

    tool_call_llm_calls: int = 0

    latencies: list[float] = field(default_factory=list)

    tool_call_steps: StepTokens = field(default_factory=StepTokens)

    response_steps: StepTokens = field(default_factory=StepTokens)

    @property

    def total_tokens(self) -> int:

        return self.prompt_tokens + self.completion_tokens
class TokenTracker(AsyncCallbackHandler):

    """
    LangChain callback handler that tracks token usage and latency across all LLM calls.

    Captures prompt_tokens, completion_tokens, per-call latency, and calculates
    estimated cost based on MODEL_PRICING. Works across orchestrator + all
    subagents automatically via LangGraph callback propagation.

    Per-node tracking uses LangGraph's ``langgraph_node`` metadata to attribute
    tokens to the specific agent/node that made the LLM call.
    """

    def __init__(self):

        self.prompt_tokens: int = 0

        self.completion_tokens: int = 0

        self.total_tokens: int = 0

        self.llm_calls: int = 0

        self._llm_start_times: Dict[UUID, float] = {}

        self.llm_latencies: List[float] = []

        self.cached_tokens: int = 0

        self.reasoning_tokens: int = 0

        self.tool_call_llm_calls: int = 0

        self.tool_call_steps: StepTokens = StepTokens()

        self.response_steps: StepTokens = StepTokens()

        self._run_node_map: Dict[UUID, str] = {}

        self.per_node: Dict[str, NodeTokenUsage] = defaultdict(NodeTokenUsage)

    def _track_start(self, run_id: UUID, metadata: Optional[Dict[str, Any]]) -> None:

        """Record start time and resolve agent/node name for a run."""

        self._llm_start_times[run_id] = time.perf_counter()

        meta = metadata or {}

        node_name = meta.get("agent_name") or meta.get("langgraph_node", "__root__")

        self._run_node_map[run_id] = node_name

    async def on_llm_start(

        self,

        serialized: Dict[str, Any],

        prompts: List[str],

        *,

        run_id: UUID,

        metadata: Optional[Dict[str, Any]] = None,

        **kwargs: Any,

    ) -> None:

        self._track_start(run_id, metadata)

    async def on_chat_model_start(

        self,

        serialized: Dict[str, Any],

        messages: List[Any],

        *,

        run_id: UUID,

        metadata: Optional[Dict[str, Any]] = None,

        **kwargs: Any,

    ) -> None:

        self._track_start(run_id, metadata)

    async def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:

        self.llm_calls += 1

        latency = 0.0

        if run_id in self._llm_start_times:

            latency = time.perf_counter() - self._llm_start_times.pop(run_id)

            self.llm_latencies.append(latency)

        node_name = self._run_node_map.pop(run_id, "__root__")

        node = self.per_node[node_name]

        node.llm_calls += 1

        if latency:

            node.latencies.append(latency)

        for generation_list in response.generations:

            for generation in generation_list:

                usage = extract_usage(generation)

                pt = usage["prompt_tokens"]

                ct = usage["completion_tokens"]

                cached = usage["cached_tokens"]

                is_tool_call = usage["has_tool_calls"]

                self.prompt_tokens += pt

                self.completion_tokens += ct

                self.total_tokens += usage["total_tokens"]

                self.cached_tokens += cached

                self.reasoning_tokens += usage["reasoning_tokens"]

                if is_tool_call:

                    self.tool_call_llm_calls += 1

                    self.tool_call_steps.prompt_tokens += pt

                    self.tool_call_steps.completion_tokens += ct

                    self.tool_call_steps.cached_tokens += cached

                    self.tool_call_steps.count += 1

                else:

                    self.response_steps.prompt_tokens += pt

                    self.response_steps.completion_tokens += ct

                    self.response_steps.cached_tokens += cached

                    self.response_steps.count += 1

                node.prompt_tokens += pt

                node.completion_tokens += ct

                node.cached_tokens += cached

                node.reasoning_tokens += usage["reasoning_tokens"]

                if is_tool_call:

                    node.tool_call_llm_calls += 1

                    node.tool_call_steps.prompt_tokens += pt

                    node.tool_call_steps.completion_tokens += ct

                    node.tool_call_steps.cached_tokens += cached

                    node.tool_call_steps.count += 1

                else:

                    node.response_steps.prompt_tokens += pt

                    node.response_steps.completion_tokens += ct

                    node.response_steps.cached_tokens += cached

                    node.response_steps.count += 1

    @staticmethod

    def _step_to_dict(step: StepTokens) -> dict[str, int]:

        return {

            "prompt_tokens": step.prompt_tokens,

            "completion_tokens": step.completion_tokens,

            "total_tokens": step.total_tokens,

            "cached_tokens": step.cached_tokens,

            "count": step.count,

        }

    def get_per_node_summary(self) -> list[dict[str, Any]]:

        """Return per-node token breakdown as a serializable list."""

        return [

            {

                "node": name,

                "prompt_tokens": node.prompt_tokens,

                "completion_tokens": node.completion_tokens,

                "total_tokens": node.total_tokens,

                "cached_tokens": node.cached_tokens,

                "reasoning_tokens": node.reasoning_tokens,

                "llm_calls": node.llm_calls,

                "tool_call_llm_calls": node.tool_call_llm_calls,

                "total_latency": round(sum(node.latencies), 3),

                "tool_call_steps": self._step_to_dict(node.tool_call_steps),

                "response_steps": self._step_to_dict(node.response_steps),

            }

            for name, node in sorted(self.per_node.items())

        ]

    def get_step_breakdown(self) -> dict[str, dict[str, int]]:

        """Return global token breakdown by step type (tool-call vs response)."""

        return {

            "tool_call_steps": self._step_to_dict(self.tool_call_steps),

            "response_steps": self._step_to_dict(self.response_steps),

        }

    def get_cost(self, model_name: str) -> float:

        """Calculate cost for API-based models (token-based pricing)."""

        pricing = MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})

        input_cost = (self.prompt_tokens / 1_000_000) * pricing["input"]

        output_cost = (self.completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_cost_hosted(self, model_name: str) -> float:

        """Calculate cost for self-hosted models (time-based pricing).

        Uses the captured LLM latencies to calculate cost based on
        infrastructure costs per second (e.g., GPU instance pricing).
        """

        pricing = HOSTING_PRICING.get(model_name, {"cost_per_second": 0.0})

        total_inference_time = sum(self.llm_latencies)

        return total_inference_time * pricing["cost_per_second"]

    def get_total_latency(self) -> float:

        """Get total LLM inference time in seconds."""

        return sum(self.llm_latencies)

    def print_summary(self, model_name: str, hosted: bool = False) -> None:

        """Print a summary of token usage, latency, and cost.

        Args:
            model_name: Name of the model (must exist in MODEL_PRICING or HOSTING_PRICING)
            hosted: If True, calculate cost based on inference time (for self-hosted models).
                    If False, calculate cost based on tokens (for API models).
        """

        cost = self.get_cost_hosted(model_name) if hosted else self.get_cost(model_name)

        total_llm_time = sum(self.llm_latencies)

        avg_llm_time = total_llm_time / len(self.llm_latencies) if self.llm_latencies else 0

        cost_basis = "time-based" if hosted else "token-based"

        print(f"  LLM Calls:         {self.llm_calls}")

        print(f"  Prompt Tokens:     {self.prompt_tokens:,}")

        print(f"  Completion Tokens: {self.completion_tokens:,}")

        print(f"  Total Tokens:      {self.total_tokens:,}")

        if self.cached_tokens:

            print(f"  Cached Tokens:     {self.cached_tokens:,}")

        if self.reasoning_tokens:

            print(f"  Reasoning Tokens:  {self.reasoning_tokens:,}")

        print(f"  Model:             {model_name}")

        print(f"  Cost Model:        {cost_basis}")

        print(f"  Estimated Cost:    ${cost:.6f}")

        print(f"  Total LLM Time:    {total_llm_time:.2f}s")

        print(f"  Avg LLM Latency:   {avg_llm_time:.2f}s")

        for i, lat in enumerate(self.llm_latencies, 1):

            print(f"    LLM Call #{i}:     {lat:.2f}s")

        if len(self.per_node) > 1:

            print(f"  Per-Node Breakdown:")

            for name, node in sorted(self.per_node.items()):

                print(f"    {name}: {node.total_tokens:,} tokens "

                      f"({node.llm_calls} calls, {node.tool_call_llm_calls} tool-call)")

