"""DeepEval model wrapper for LangChain models."""
from deepeval.models.base_model import DeepEvalBaseLLM
class LangChainDeepEvalModel(DeepEvalBaseLLM):

    """
    Wrapper to use LangChain models with DeepEval.

    DeepEval requires its own model interface. This class wraps a LangChain
    model (e.g., AzureChatOpenAI) to make it compatible with DeepEval metrics.

    Example:
        ```python
        from services import create_llm
        from services.deepeval_model import LangChainDeepEvalModel

        langchain_llm = create_llm(settings)
        eval_model = LangChainDeepEvalModel(langchain_llm)

        metric = ToolCorrectnessMetric(model=eval_model)
        ```
    """

    def __init__(self, langchain_model):

        """
        Initialize with a LangChain model.

        Args:
            langchain_model: A LangChain chat model (e.g., AzureChatOpenAI)
        """

        self.model = langchain_model

    def load_model(self):

        """Return the underlying LangChain model."""

        return self.model

    def generate(self, prompt: str) -> str:

        """Synchronous generation."""

        return self.model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:

        """Asynchronous generation for faster evaluation."""

        res = await self.model.ainvoke(prompt)

        return res.content

    def get_model_name(self) -> str:

        """Return a descriptive model name."""

        if hasattr(self.model, 'model'):

            return f"LangChain ({self.model.model})"

        return "LangChain Model"

