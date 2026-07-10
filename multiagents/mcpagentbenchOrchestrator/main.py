"""
MCPAgentBench Multi-Agent Orchestrator - CLI Entry Point.
Supports two granularity modes:
- **fine** (default): 16 focused subagents (1 Agent = 1 MCP Server)
- **coarse**: 3 broad subagents (1 Agent = N MCP Servers)
Prerequisites:
    Start the MCPAgentBench MCP server first:
        cd mcpservers/mcpagentbench
        python main.py
    (or: uvicorn mcpservers.mcpagentbench.main:app --port 9000)
Usage:
    python main.py                          # Fine-grained (16 agents)
    python main.py --granularity coarse     # Coarse-grained (3 agents)
    python main.py -g coarse --verbose      # Coarse with reasoning logs
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path
_bench_dir = Path(__file__).resolve().parent
_python_services_dir = _bench_dir.parent.parent.parent
for _path in [str(_bench_dir), str(_python_services_dir)]:

    if _path not in sys.path:

        sys.path.insert(0, _path)
from agenttim.config.settings import get_settings
from orchestrator.orchestrator_agent import MCPBenchOrchestratorAgent
logging.basicConfig(

    level=logging.WARNING,

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MCPAgentBench")
GRANULARITY_LABELS = {

    "fine": "Option A: 1 Agent = 1 MCP Server (16 domains)",

    "coarse": "Option B: 1 Agent = N MCP Servers (3 broad agents)",
}
async def run_interactive_chat(

    granularity: str = "fine", verbose: bool = False,
) -> None:

    """Run interactive chat with the MCPBench orchestrator."""

    settings = get_settings()

    print("=" * 60)

    print("  MCPAgentBench - Multi-Agent Orchestrator")

    print(f"  {GRANULARITY_LABELS[granularity]}")

    if verbose:

        print("  [VERBOSE MODE: Showing reasoning & tool calls]")

    print("=" * 60)

    print("\nInitializing agents (this may take a moment)...")

    orchestrator = MCPBenchOrchestratorAgent(

        settings=settings,

        granularity=granularity,

        logger=logger,

    )

    await orchestrator.initialize()

    subagents = orchestrator.get_available_subagents()

    print(f"\nAgent ready! {len(subagents)} domain agents available:")

    for domain, desc in subagents.items():

        print(f"  - {domain}: {desc}")

    print("\nType '/clear' to reset conversation history.")

    print("Type 'exit' or 'quit' to end the conversation.")

    print("=" * 60)

    print()

    while True:

        try:

            user_input = input("You: ").strip()

            if not user_input:

                continue

            if user_input.lower() in ("exit", "quit", "q"):

                print("\nGoodbye!")

                break

            if user_input.lower() in ("/clear", "clear"):

                orchestrator.clear_conversation_history()

                print("\nConversation history cleared.\n")

                continue

            if verbose:

                print("\n--- Agent Reasoning ---")

                response = await orchestrator.chat(user_input, verbose=True)

                print("--- End Reasoning ---\n")

                print(f"Agent: {response}")

            else:

                print("\nAgent: ", end="", flush=True)

                response = await orchestrator.chat(user_input)

                print(response)

            print()

        except KeyboardInterrupt:

            print("\n\nGoodbye!")

            break

        except Exception as e:

            print(f"\nError: {e}")

            print()
def main():

    """Main entry point."""

    parser = argparse.ArgumentParser(

        description="MCPAgentBench - Multi-Agent Orchestrator"

    )

    parser.add_argument(

        "--granularity",

        "-g",

        choices=["fine", "coarse"],

        default="fine",

        help="Agent granularity: fine (16 agents, 1:1) or coarse (3 agents, 1:N)",

    )

    parser.add_argument(

        "--verbose",

        "-v",

        action="store_true",

        help="Show agent reasoning and tool calls",

    )

    args = parser.parse_args()

    asyncio.run(run_interactive_chat(

        granularity=args.granularity, verbose=args.verbose,

    ))
if __name__ == "__main__":

    main()

