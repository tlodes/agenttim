"""Argument Correctness test cases - user requests contain misleading parameters for no-param tools.
These cases test whether the model correctly avoids passing unnecessary arguments
to tools that don't require any parameters (e.g., list_databases()).
The user query intentionally includes information that could mislead the model
into constructing invalid tool calls with arguments that don't exist in the schema.
"""
try:

    from deepeval.test_case import ToolCall
except ImportError:

    from dataclasses import dataclass

    @dataclass

    class ToolCall:

        name: str

        input_parameters: dict = None

        def __post_init__(self):

            if self.input_parameters is None:

                self.input_parameters = {}
ARGUMENT_CORRECTNESS_CASES = [

    {

        "id": "AC-01",

        "description": "No-param tool with explicit database filter in query (should ignore filter)",

        "input": "Liste mir alle Datenbanken auf, die mit 'Repo' beginnen",

        "expected_output": "Es gibt die Datenbanken: ReadRepo, Ai und WriteRepo.",

        "expected_tools": [

            ToolCall(name="list_databases", input_parameters={}),

        ],

        "notes": "User requests filtering by prefix, but list_databases has no filter param. "

        "Model should call list_databases() without args and filter in response text.",

    },

    {

        "id": "AC-02",

        "description": "No-param tool with limit/count in query (should ignore limit)",

        "input": "Zeige mir nur die ersten 2 Datenbanken",

        "expected_output": "Es gibt die Datenbanken: ReadRepo, Ai und WriteRepo.",

        "expected_tools": [

            ToolCall(name="list_databases", input_parameters={}),

        ],

        "notes": "User requests a limit, but list_databases has no limit param. "

        "Model should call list_databases() without args and limit in response text.",

    },
]

