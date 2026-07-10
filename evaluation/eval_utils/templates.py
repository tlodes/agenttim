"""Custom DeepEval evaluation templates."""
import textwrap
from typing import List
from deepeval.metrics.argument_correctness.template import ArgumentCorrectnessTemplate
class DetailedArgumentCorrectnessTemplate(ArgumentCorrectnessTemplate):

    """Custom template that forces the LLM judge to always list the actual
    parameters and their values in the reason — even when the score is 1.0."""

    @staticmethod

    def generate_reason(

        incorrect_tool_calls_reasons: List[str],

        input: str,

        score: float,

        multimodal: bool = False,

    ):

        return textwrap.dedent(

            f"""Given the argument correctness score, the list of reasons of incorrect tool calls, and the input, provide a detailed reason for the score.

            IMPORTANT: You MUST always list the actual tool calls with their concrete input parameter names and values in your reason. This is mandatory regardless of whether the score is perfect or not.

            Format your reason like this:
            "The score is <score> because <tool_name> was called with <param1>=<value1>, <param2>=<value2>. <explanation of correctness or issues>."

            If there are incorrect tool calls, explain what was wrong.
            If all tool calls are correct, confirm which parameters were passed and why they correctly address the input.

            **
            IMPORTANT: Please make sure to only return in JSON format, with the 'reason' key providing the reason.

            Example JSON:
            {
                "reason": "The score is 1.00 because get_schema_for_collections was called with collection_names='addressesShort', database_name='p1-Read'. Both parameters correctly match the user's request for the addressesShort collection from the p1-Read repository."
            }
            ===== END OF EXAMPLE ======
            **

            Argument Correctness Score:
            {score}

            Reasons why the score can't be higher based on incorrect tool calls:
            {incorrect_tool_calls_reasons}

            Input:
            {input}

            JSON:
             """

        )

