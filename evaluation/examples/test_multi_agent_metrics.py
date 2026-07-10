"""
Minimal test for Multi-Agent Coordination Metrics.
Imports directly to avoid langchain dependencies.
"""
import sys
from pathlib import Path
eval_dir = Path(__file__).parent.parent
sys.path.insert(0, str(eval_dir))
import importlib.util
spec = importlib.util.spec_from_file_location(

    "multi_agent_metrics",

    eval_dir / "eval_utils" / "multi_agent_metrics.py"
)
multi_agent_metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(multi_agent_metrics)
MultiAgentTestCase = multi_agent_metrics.MultiAgentTestCase
MultiAgentToolCall = multi_agent_metrics.MultiAgentToolCall
AgentMessage = multi_agent_metrics.AgentMessage
AgentTokenUsage = multi_agent_metrics.AgentTokenUsage
MessageDensityMetric = multi_agent_metrics.MessageDensityMetric
CoordinationOverheadMetric = multi_agent_metrics.CoordinationOverheadMetric
MultiAgentEvaluator = multi_agent_metrics.MultiAgentEvaluator
def create_orchestrator_example() -> MultiAgentTestCase:

    """Create example test case for Orchestrator pattern."""

    return MultiAgentTestCase(

        input="Move file.txt to backup/ and tweet about the backup",

        actual_output="File moved successfully and tweet posted.",

        expected_output="File moved and tweet posted.",

        architecture="orchestrator",

        tool_calls=[

            MultiAgentToolCall(

                name="find_file",

                agent_id="FileAgent",

                input_parameters={"filename": "file.txt"},

                success=True,

            ),

            MultiAgentToolCall(

                name="move_file",

                agent_id="FileAgent",

                input_parameters={"source": "file.txt", "dest": "backup/"},

                success=True,

            ),

            MultiAgentToolCall(

                name="post_tweet",

                agent_id="SocialAgent",

                input_parameters={"content": "Backup completed for file.txt"},

                success=True,

            ),

        ],

        messages=[

            AgentMessage(

                sender="Orchestrator",

                recipient="FileAgent",

                content="Please move file.txt to backup/",

                message_type="delegation",

            ),

            AgentMessage(

                sender="FileAgent",

                recipient="Orchestrator",

                content="File moved successfully",

                message_type="result",

            ),

            AgentMessage(

                sender="Orchestrator",

                recipient="SocialAgent",

                content="Tweet about the backup",

                message_type="delegation",

            ),

            AgentMessage(

                sender="SocialAgent",

                recipient="Orchestrator",

                content="Tweet posted",

                message_type="result",

            ),

        ],

        agent_tokens=[

            AgentTokenUsage(agent_id="Orchestrator", input_tokens=500, output_tokens=200),

            AgentTokenUsage(agent_id="FileAgent", input_tokens=300, output_tokens=100),

            AgentTokenUsage(agent_id="SocialAgent", input_tokens=200, output_tokens=80),

        ],

        single_agent_tokens=600,

        single_agent_turns=3,

        total_turns=5,

    )
def create_swarm_example() -> MultiAgentTestCase:

    """Create example test case for Swarm pattern with duplicate work."""

    return MultiAgentTestCase(

        input="Move file.txt to backup/ and tweet about the backup",

        actual_output="File moved successfully and tweet posted.",

        expected_output="File moved and tweet posted.",

        architecture="swarm",

        tool_calls=[

            MultiAgentToolCall(

                name="find_file",

                agent_id="FileAgent",

                input_parameters={"filename": "file.txt"},

                success=True,

            ),

            MultiAgentToolCall(

                name="find_file",

                agent_id="SocialAgent",

                input_parameters={"filename": "file.txt"},

                success=True,

            ),

            MultiAgentToolCall(

                name="move_file",

                agent_id="FileAgent",

                input_parameters={"source": "file.txt", "dest": "backup/"},

                success=True,

            ),

            MultiAgentToolCall(

                name="post_tweet",

                agent_id="SocialAgent",

                input_parameters={"content": "Backup completed for file.txt"},

                success=True,

            ),

        ],

        messages=[

            AgentMessage(sender="FileAgent", recipient="broadcast", content="I'll handle the file operations", message_type="delegation"),

            AgentMessage(sender="SocialAgent", recipient="broadcast", content="Let me check if the file exists first", message_type="clarification"),

            AgentMessage(sender="FileAgent", recipient="SocialAgent", content="File found at ./file.txt", message_type="result"),

            AgentMessage(sender="SocialAgent", recipient="FileAgent", content="Got it, I'll prepare the tweet", message_type="clarification"),

            AgentMessage(sender="FileAgent", recipient="broadcast", content="File moved to backup/", message_type="result"),

            AgentMessage(sender="SocialAgent", recipient="broadcast", content="Tweet posted", message_type="result"),

        ],

        agent_tokens=[

            AgentTokenUsage(agent_id="FileAgent", input_tokens=600, output_tokens=250),

            AgentTokenUsage(agent_id="SocialAgent", input_tokens=500, output_tokens=200),

        ],

        single_agent_tokens=600,

        single_agent_turns=3,

        total_turns=6,

    )
def main():

    print("=" * 70)

    print("MULTI-AGENT COORDINATION METRICS TEST")

    print("=" * 70)

    orchestrator_case = create_orchestrator_example()

    swarm_case = create_swarm_example()

    evaluator = MultiAgentEvaluator()

    print("\n" + "-" * 70)

    print("ORCHESTRATOR PATTERN")

    print("-" * 70)

    print(evaluator.summary(orchestrator_case))

    print("\n" + "-" * 70)

    print("SWARM PATTERN")

    print("-" * 70)

    print(evaluator.summary(swarm_case))

    print("\n" + "=" * 70)

    print("PATTERN COMPARISON")

    print("=" * 70)

    orch_results = evaluator.evaluate(orchestrator_case)

    swarm_results = evaluator.evaluate(swarm_case)

    print(f"\n{'Metric':<30} {'Orchestrator':>12} {'Swarm':>12} {'Winner':>15}")

    print("-" * 70)

    for metric_name in orch_results:

        orch_score = orch_results[metric_name]["score"]

        swarm_score = swarm_results[metric_name]["score"]

        winner = "Orchestrator" if orch_score > swarm_score else "Swarm" if swarm_score > orch_score else "Tie"

        print(f"{metric_name:<30} {orch_score:>12.2f} {swarm_score:>12.2f} {winner:>15}")

    print("\n[OK] All metrics executed successfully!")
if __name__ == "__main__":

    main()

