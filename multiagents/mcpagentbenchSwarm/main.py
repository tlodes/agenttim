"""
MCPAgentBench Swarm Agent - CLI Entry Point.
Collaborative peer discussion: domain agents discuss and reach consensus
before executing tools. All agents see all messages.
Prerequisites:
    uvicorn mcpservers.mcpagentbench.main:app --port 9000
Usage:
    python main.py --verbose
    python main.py --verbose --max-rounds 3
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
from swarm.swarm_coordinator import MCPBenchSwarmAgent
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("MCPAgentBenchSwarm")
async def run_interactive_chat(verbose: bool = False, max_rounds: int = 3) -> None:

    settings = get_settings()

    print("=" * 60)

    print("  MCPAgentBench - Swarm Agent")

    print(f"  Collaborative discussion pattern ({max_rounds} max rounds)")

    print("=" * 60)

    agent = MCPBenchSwarmAgent(settings=settings, max_rounds=max_rounds, logger=logger)

    await agent.initialize()

    print(f"\nAgent ready! Type 'exit' to quit.\n")

    while True:

        try:

            user_input = input("You: ").strip()

            if not user_input:

                continue

            if user_input.lower() in ("exit", "quit", "q"):

                break

            if user_input.lower() == "/clear":

                agent.clear_conversation_history()

                print("History cleared.\n")

                continue

            response = await agent.chat(user_input, verbose=verbose)

            print(f"\nAgent: {response}\n")

        except KeyboardInterrupt:

            break
def main():

    parser = argparse.ArgumentParser(description="MCPAgentBench Swarm Agent")

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument("--max-rounds", type=int, default=3)

    args = parser.parse_args()

    asyncio.run(run_interactive_chat(verbose=args.verbose, max_rounds=args.max_rounds))
if __name__ == "__main__":

    main()

