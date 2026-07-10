"""
Example: Using Multi-Agent Coordination Metrics
================================================
This script demonstrates how to use the custom deepeval metrics
for evaluating multi-agent orchestration patterns.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from agenttim.evaluation.eval_utils.multi_agent_metrics import (

    MultiAgentTestCase,

    MultiAgentToolCall,

    AgentMessage,

    AgentTokenUsage,

    MessageDensityMetric,

    CoordinationOverheadMetric,

    MultiAgentEvaluator,
)
def create_orchestrator_example() -> MultiAgentTestCase:

    """
    Create example test case for Orchestrator pattern.

    Scenario: User asks to "Move file.txt to backup/ and tweet about it"
    - FileAgent handles file operations
    - SocialAgent handles Twitter
    - Orchestrator delegates correctly
    """

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

    """
    Create example test case for Swarm pattern.

    Scenario: Same task but with peer-to-peer discussion.
    Shows higher message density and some duplicate work.
    """

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

            AgentMessage(

                sender="FileAgent",

                recipient="broadcast",

                content="I'll handle the file operations",

                message_type="delegation",

            ),

            AgentMessage(

                sender="SocialAgent",

                recipient="broadcast",

                content="Let me check if the file exists first",

                message_type="clarification",

            ),

            AgentMessage(

                sender="FileAgent",

                recipient="SocialAgent",

                content="File found at ./file.txt",

                message_type="result",

            ),

            AgentMessage(

                sender="SocialAgent",

                recipient="FileAgent",

                content="Got it, I'll prepare the tweet",

                message_type="clarification",

            ),

            AgentMessage(

                sender="FileAgent",

                recipient="broadcast",

                content="File moved to backup/",

                message_type="result",

            ),

            AgentMessage(

                sender="SocialAgent",

                recipient="broadcast",

                content="Tweet posted",

                message_type="result",

            ),

        ],

        agent_tokens=[

            AgentTokenUsage(agent_id="FileAgent", input_tokens=600, output_tokens=250),

            AgentTokenUsage(agent_id="SocialAgent", input_tokens=500, output_tokens=200),

        ],

        single_agent_tokens=600,

        single_agent_turns=3,

        total_turns=6,

    )
def run_individual_metrics():

    """Run each metric individually to show detailed usage."""

    print("=" * 70)

    print("INDIVIDUAL METRIC EVALUATION")

    print("=" * 70)

    orchestrator_case = create_orchestrator_example()

    swarm_case = create_swarm_example()

    print("\n" + "-" * 70)

    print("1. MESSAGE DENSITY METRIC")

    print("-" * 70)

    density_metric = MessageDensityMetric(threshold=0.5)

    score = density_metric.measure(orchestrator_case)

    print(f"\nOrchestrator Pattern:")

    print(f"  Score: {score:.2f}")

    print(f"  Reason: {density_metric.reason}")

    score = density_metric.measure(swarm_case)

    print(f"\nSwarm Pattern:")

    print(f"  Score: {score:.2f}")

    print(f"  Reason: {density_metric.reason}")

    print("\n" + "-" * 70)

    print("2. COORDINATION OVERHEAD METRIC")

    print("-" * 70)

    overhead_metric = CoordinationOverheadMetric(threshold=0.5)

    score = overhead_metric.measure(orchestrator_case)

    print(f"\nOrchestrator Pattern:")

    print(f"  Score: {score:.2f}")

    print(f"  Reason: {overhead_metric.reason}")

    score = overhead_metric.measure(swarm_case)

    print(f"\nSwarm Pattern:")

    print(f"  Score: {score:.2f}")

    print(f"  Reason: {overhead_metric.reason}")
def run_aggregated_evaluation():

    """Run all metrics at once using MultiAgentEvaluator."""

    print("\n" + "=" * 70)

    print("AGGREGATED EVALUATION")

    print("=" * 70)

    evaluator = MultiAgentEvaluator(

        message_density_threshold=0.5,

        overhead_threshold=0.5,

    )

    orchestrator_case = create_orchestrator_example()

    swarm_case = create_swarm_example()

    print("\n" + "-" * 70)

    print("ORCHESTRATOR PATTERN")

    print("-" * 70)

    print(evaluator.summary(orchestrator_case))

    print("\n" + "-" * 70)

    print("SWARM PATTERN")

    print("-" * 70)

    print(evaluator.summary(swarm_case))
def compare_patterns():

    """Compare metrics across different patterns."""

    print("\n" + "=" * 70)

    print("PATTERN COMPARISON")

    print("=" * 70)

    evaluator = MultiAgentEvaluator()

    orchestrator_case = create_orchestrator_example()

    swarm_case = create_swarm_example()

    orch_results = evaluator.evaluate(orchestrator_case)

    swarm_results = evaluator.evaluate(swarm_case)

    print(f"\n{'Metric':<30} {'Orchestrator':>15} {'Swarm':>15} {'Winner':>15}")

    print("-" * 75)

    for metric_name in orch_results:

        orch_score = orch_results[metric_name]["score"]

        swarm_score = swarm_results[metric_name]["score"]

        winner = "Orchestrator" if orch_score > swarm_score else "Swarm" if swarm_score > orch_score else "Tie"

        print(f"{metric_name:<30} {orch_score:>15.2f} {swarm_score:>15.2f} {winner:>15}")
if __name__ == "__main__":

    run_individual_metrics()

    run_aggregated_evaluation()

    compare_patterns()

