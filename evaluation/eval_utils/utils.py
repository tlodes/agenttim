"""Shared utility functions for evaluation scripts."""
from typing import Any, Dict
from .constants import INTERNAL_KEYS
def extract_usage(generation: Any) -> Dict[str, Any]:

    """Extract token usage from a LangChain generation object.

    Azure OpenAI stores usage under response_metadata["token_usage"],
    standard OpenAI under response_metadata["usage"] or generation_info["usage"].

    Returns detailed breakdown including cached and reasoning tokens
    when available from the provider.
    """

    message = getattr(generation, "message", None)

    metadata = getattr(message, "response_metadata", {}) or {}

    usage = (

        metadata.get("token_usage")

        or metadata.get("usage")

        or (getattr(generation, "generation_info", {}) or {}).get("usage")

        or {}

    )

    prompt_details = usage.get("prompt_tokens_details") or {}

    completion_details = usage.get("completion_tokens_details") or {}

    if isinstance(prompt_details, dict):

        cached = prompt_details.get("cached_tokens") or 0

    else:

        cached = getattr(prompt_details, "cached_tokens", 0) or 0

    if isinstance(completion_details, dict):

        reasoning = completion_details.get("reasoning_tokens") or 0

    else:

        reasoning = getattr(completion_details, "reasoning_tokens", 0) or 0

    has_tool_calls = bool(

        getattr(message, "tool_calls", None)

        or (getattr(message, "additional_kwargs", {}) or {}).get("tool_calls")

    )

    return {

        "prompt_tokens": usage.get("prompt_tokens", 0) or 0,

        "completion_tokens": usage.get("completion_tokens", 0) or 0,

        "total_tokens": usage.get("total_tokens", 0) or 0,

        "cached_tokens": cached,

        "reasoning_tokens": reasoning,

        "has_tool_calls": has_tool_calls,

    }
def sanitize_args(args: Dict[str, Any]) -> Dict[str, Any]:

    """Filter out internal LangGraph keys, preserving original value types."""

    return {k: v for k, v in args.items() if k not in INTERNAL_KEYS}

