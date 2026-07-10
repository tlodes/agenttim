"""
BFCL Router Agent.
Classifies user requests upfront via LLM with structured output, routes to
domain-specific agents using LangGraph primitives:
- Send() for parallel multi-domain routing
- Command(goto=...) for single-domain routing
Reference: https://docs.langchain.com/oss/python/langchain/multi-agent/router
Unlike the Orchestrator (iterative ReAct delegation), the Router makes
a single classification decision per turn using Pydantic models for type-safe
structured output.
Reuses the same subagent classes as bfclOrchestrator.
"""
import asyncio
import operator
from logging import Logger
from typing import Annotated, Any, Dict, List, Optional
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from agenttim.agents.base import StatefulEvalAgent
from agenttim.config.settings import Settings
from agenttim.bfcl.domain_config import (

    ALL_DOMAINS,

    BASE_PROMPT,

    DOMAIN_DESCRIPTIONS,

    get_tool_to_domain_map,
)
from agenttim.multiagents.bfclOrchestrator.subagents.agent_definitions import (

    AGENT_REGISTRY,
)
MAX_RECURSION_LIMIT = 20
class Classification(BaseModel):

    """A single domain classification with a targeted sub-query."""

    domain: str = Field(description="The domain name that should handle this part of the request")

    query: str = Field(description="A targeted sub-question for this specific domain")
class ClassificationResult(BaseModel):

    """Result of classifying a user request into domain(s)."""

    classifications: List[Classification] = Field(

        default_factory=list,

        description="List of domains to invoke with their targeted sub-questions. Empty for greetings.",

    )
CLASSIFICATION_PROMPT = BASE_PROMPT + """
## Your Role: Request Classifier
Analyze the user's message and determine which domain(s) should handle it.
## Available Domains
{domains_section}
## Instructions
- Analyze the request and determine which domain agent(s) are relevant
- For each relevant domain, generate a targeted sub-question specific to that domain
- For single-domain requests, return one classification
- For multi-domain requests, return multiple classifications IN EXECUTION ORDER
- If the request is a greeting or non-tool question, return an empty list
## Examples
User: "Create a directory called temp"
-> classifications: [{{"domain": "filesystem", "query": "Create a directory called temp"}}]
User: "Calculate the mean of [1,2,3] and send the result to Alice"
-> classifications: [
    {{"domain": "math", "query": "Calculate the mean of [1,2,3]"}},
    {{"domain": "messaging", "query": "Send the calculation result to Alice"}}
  ]
User: "Hello!"
-> classifications: []"""
SYNTHESIS_PROMPT = """Synthesize the following results from domain agents into a single coherent response for the user.
User request: {user_request}
Agent results:
{agent_results}
Provide a clear, concise response that combines all results."""
class RouterState(TypedDict):

    """State for the router graph."""

    query: str

    classifications: List[Classification]

    agent_results: Annotated[List[dict], operator.add]

    final_response: str
class BFCLRouterAgent(StatefulEvalAgent):

    """
    Router for BFCL multi-turn evaluation.

    Uses a LangGraph StateGraph with:
    - classify node: LLM classifies domain(s)
    - Send() to fan out to domain agent nodes in parallel
    - synthesize node: combines results

    Conversation history is maintained across turns by the base class.
    """

    TURN_TIMEOUT: int = 120

    def __init__(

        self,

        settings: Settings,

        logger: Optional[Logger] = None,

    ):

        super().__init__(settings, logger_name="BFCLRouter", logger=logger)

        self._subagents: Dict[str, Any] = {}

        self._graph = None

        self._tool_to_domain = get_tool_to_domain_map()

    async def _do_initialize(self) -> None:

        """Initialize all domain subagents. LLM is already set by base class."""

        for name, agent_class in AGENT_REGISTRY.items():

            agent = agent_class(settings=self.settings, logger=self.logger)

            await agent.initialize()

            self._subagents[name] = agent

        self.logger.info(

            f"Router initialized with {len(self._subagents)} domain agents"

        )

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Distribute tools to domain subagents and rebuild graph."""

        super().setup_for_test_case(tools=tools, **kwargs)

        tools = tools or []

        domain_tools: Dict[str, List[BaseTool]] = {

            name: [] for name in self._subagents

        }

        for t in tools:

            domain = self._tool_to_domain.get(t.name)

            if domain and domain in domain_tools:

                domain_tools[domain].append(t)

        for name, subagent in self._subagents.items():

            subagent.set_tools(domain_tools.get(name, []))

        self._graph = self._build_graph()

        total = sum(len(v) for v in domain_tools.values())

        self.logger.info(f"Test case setup: {total} tools distributed")

    def _build_graph(self) -> Any:

        """Build the LangGraph StateGraph for routing.

        Uses structured output for type-safe classification per LangChain docs.

        History Propagation: The router's conversation history is passed to
        domain subagents via chat_with_history(). This allows subagents to see
        previous turns' tool calls and results.
        """

        subagents = self._subagents

        llm = self._llm

        logger = self.logger

        router = self

        structured_llm = llm.with_structured_output(ClassificationResult)

        async def classify(state: RouterState) -> dict:

            """Classify the user query into domain(s) with targeted sub-queries."""

            domains_section = "\n".join(

                f"- **{d}**: {DOMAIN_DESCRIPTIONS.get(d, '')}"

                for d in ALL_DOMAINS

            )

            prompt = CLASSIFICATION_PROMPT.format(

                domains_section=domains_section,

            )

            try:

                result: ClassificationResult = await structured_llm.ainvoke([

                    {"role": "system", "content": prompt},

                    {"role": "user", "content": state["query"]},

                ], config={"metadata": {"agent_name": "router_classify"}})

                valid_classifications = [

                    c for c in result.classifications

                    if c.domain in subagents and subagents[c.domain].get_available_tools()

                ]

                logger.info(

                    f"Classified: {[c.domain for c in valid_classifications]}"

                )

                return {"classifications": valid_classifications}

            except Exception as e:

                logger.warning(f"Classification failed: {e}")

                return {"classifications": []}

        async def run_domain_agent(state: RouterState, config: dict = None) -> dict:

            """Run a single domain agent with its targeted sub-query.

            Passes conversation history to subagent so it can see previous
            turns' tool calls and results.
            """

            classification = state["classifications"][0]

            domain = classification.domain

            targeted_query = classification.query

            agent = subagents[domain]

            callbacks = (config or {}).get("callbacks", None)

            history = router.get_conversation_history()

            response = await agent.chat_with_history(

                targeted_query, history=history, callbacks=callbacks

            )

            return {"agent_results": [{"domain": domain, "result": response}]}

        async def synthesize(state: RouterState):

            results = state.get("agent_results", [])

            if len(results) == 1:

                return {"final_response": results[0]["result"]}

            agent_results_str = "\n\n".join(

                f"[{r['domain']}]: {r['result']}" for r in results

            )

            prompt = SYNTHESIS_PROMPT.format(

                user_request=state["query"],

                agent_results=agent_results_str,

            )

            result = await llm.ainvoke([

                {"role": "system", "content": prompt},

            ], config={"metadata": {"agent_name": "router_synthesize"}})

            return {"final_response": result.content}

        async def direct_response(state: RouterState):

            result = await llm.ainvoke([

                {"role": "system", "content": "Respond briefly and helpfully."},

                {"role": "user", "content": state["query"]},

            ], config={"metadata": {"agent_name": "router_direct"}})

            return {"final_response": result.content}

        def route_after_classify(state: RouterState):

            """Route based on classification results.

            - Empty classifications -> direct_response
            - Single classification -> domain_agent
            - Multiple classifications -> parallel Send() to domain_agent

            Returns plain strings for single routing (not Command objects).
            Command(goto=...) is for transfer tools, not conditional edge functions.
            """

            classifications = state.get("classifications", [])

            if not classifications:

                return "direct_response"

            if len(classifications) == 1:

                return "domain_agent"

            return [

                Send("domain_agent", {

                    "query": state["query"],

                    "classifications": [c],

                    "agent_results": [],

                })

                for c in classifications

            ]

        builder = StateGraph(RouterState)

        builder.add_node("classify", classify)

        builder.add_node("domain_agent", run_domain_agent)

        builder.add_node("synthesize", synthesize)

        builder.add_node("direct_response", direct_response)

        builder.add_edge(START, "classify")

        builder.add_conditional_edges("classify", route_after_classify)

        builder.add_edge("domain_agent", "synthesize")

        builder.add_edge("synthesize", END)

        builder.add_edge("direct_response", END)

        return builder.compile()

    async def _execute_turn(

        self,

        user_message: str,

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> tuple[str, list | None]:

        """Execute one turn through the router graph.

        The base class handles history snapshot/restore and user/assistant
        message appending. This method only invokes the graph.
        """

        if self._graph is None:

            raise RuntimeError("Call setup_for_test_case() first.")

        invoke_config: dict[str, Any] = {"recursion_limit": MAX_RECURSION_LIMIT}

        if callbacks:

            invoke_config["callbacks"] = callbacks

        try:

            result = await asyncio.wait_for(

                self._graph.ainvoke(

                    {

                        "query": user_message,

                        "classifications": [],

                        "agent_results": [],

                        "final_response": "",

                    },

                    config=invoke_config,

                ),

                timeout=self.TURN_TIMEOUT,

            )

        except asyncio.TimeoutError:

            self.logger.error(f"Turn timed out after {self.TURN_TIMEOUT}s")

            raise

        except Exception as e:

            self.logger.error(f"Turn failed: {e}")

            raise

        return result.get("final_response", ""), None

    def get_available_subagents(self) -> Dict[str, str]:

        return {

            name: DOMAIN_DESCRIPTIONS.get(name, "")

            for name in self._subagents

        }

