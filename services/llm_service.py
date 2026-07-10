"""LLM Service - Provides Azure OpenAI and OpenRouter LLM instances."""
from __future__ import annotations
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import SecretStr
import shared.config.constants as constants
from agenttim.config.settings import Settings
from agenttim.config.secret_manager_dependency import get_secret_manager
EVAL_JUDGE_MODEL = "june-gpt-4-1-mini-datazone"
OPENROUTER_MODELS = {

    "deepseek/deepseek-v4-pro",
}
def create_llm(

    settings: Settings,

    temperature: float = 0.1,

    parallel_tool_calls: bool = True,

    model_override: str | None = None,
):

    """
    Create an LLM instance (Azure OpenAI or OpenRouter).

    Models listed in OPENROUTER_MODELS are routed through OpenRouter.
    All other models use Azure OpenAI.

    Args:
        settings: Application settings with API version and model config
        temperature: LLM temperature (default: 0.1 for deterministic responses)
        parallel_tool_calls: Allow LLM to generate multiple tool calls per response
        model_override: Override model name from settings

    Returns:
        Configured ChatOpenAI or AzureChatOpenAI instance
    """

    model = model_override or settings.AZURE_OPENAI_MODEL

    model_kwargs = {}

    if not parallel_tool_calls:

        model_kwargs["parallel_tool_calls"] = False

    if model in OPENROUTER_MODELS or model.startswith("deepseek/"):

        return ChatOpenAI(

            api_key=SecretStr(settings.OPENROUTER_API_KEY),

            base_url=settings.OPENROUTER_BASE_URL,

            model=model,

            temperature=temperature,

            model_kwargs=model_kwargs,

        )

    secret_manager = get_secret_manager()

    api_key = secret_manager.get_secret(

        constants.MNT_SHARED_DESCRIPTOR_KEY,

        constants.MNT_OPEN_AI_API_SWC_KEY

    )

    endpoint = secret_manager.get_secret(

        constants.MNT_SHARED_DESCRIPTOR_KEY,

        constants.MNT_OPEN_AI_SWC_RESOURCE_ENDPOINT_CONFIG_KEY

    )

    return AzureChatOpenAI(

        api_key=SecretStr(api_key),

        api_version=settings.AZURE_OPENAI_API_VERSION,

        azure_endpoint=endpoint,

        model=model,

        temperature=temperature,

        model_kwargs=model_kwargs,

    )

