"""Test case definitions for evaluation scripts.
Structure:
    test_cases/
    |-- singleturn/              # User provides complete info
    |   |-- bfcl/                # BFCL benchmark
    |   |-- gaia/                # GAIA benchmark
    |   +-- toolbench/           # ToolBench benchmark
    |-- multiturn/               # User needs clarification
    +-- argument_correctness_cases.py  # Cross-cutting tests
Naming Convention:
    {pattern}_{dimension}.py or general_{dimension}.py
Dimensions:
    STurn-1T: Single-Turn, Single Tool
    STurn-MT: Single-Turn, Multi Tool
    MTurn-1T: Multi-Turn, Single Tool
    MTurn-MT: Multi-Turn, Multi Tool
"""
try:

    from .singleturn import (

        ST_MT_PARALLEL_CASES,

        ST_MT_SEQUENTIAL_CASES,

        TOOLBENCH_ST_1T_CASES,

        BFCL_ST_MT_CASES,

        GAIA_ST_MT_CASES,

        ALL_SINGLETURN_CASES,

    )
except (ImportError, ModuleNotFoundError):

    ST_MT_PARALLEL_CASES = []

    ST_MT_SEQUENTIAL_CASES = []

    TOOLBENCH_ST_1T_CASES = []

    BFCL_ST_MT_CASES = []

    GAIA_ST_MT_CASES = []

    ALL_SINGLETURN_CASES = []
try:

    from .multiturn import (

        MT_1T_BASE_CASES,

        MT_1T_MISSING_PARAMS_CASES,

        MT_1T_MISSING_FUNC_CASES,

        MT_MT_BASE_CASES,

        MT_MT_MISSING_PARAMS_CASES,

        MT_MT_MISSING_FUNC_CASES,

        ALL_MULTITURN_CASES,

    )
except (ImportError, ModuleNotFoundError):

    MT_1T_BASE_CASES = []

    MT_1T_MISSING_PARAMS_CASES = []

    MT_1T_MISSING_FUNC_CASES = []

    MT_MT_BASE_CASES = []

    MT_MT_MISSING_PARAMS_CASES = []

    MT_MT_MISSING_FUNC_CASES = []

    ALL_MULTITURN_CASES = []
try:

    from .argument_correctness_cases import ARGUMENT_CORRECTNESS_CASES
except (ImportError, ModuleNotFoundError):

    ARGUMENT_CORRECTNESS_CASES = []
ALL_CASES_BY_DIMENSION = {

    "STurn-1T": TOOLBENCH_ST_1T_CASES,

    "STurn-MT": BFCL_ST_MT_CASES + GAIA_ST_MT_CASES,
}
ALL_TEST_CASES = ALL_SINGLETURN_CASES + ALL_MULTITURN_CASES + ARGUMENT_CORRECTNESS_CASES
__all__ = [

    "ST_MT_PARALLEL_CASES",

    "ST_MT_SEQUENTIAL_CASES",

    "TOOLBENCH_ST_1T_CASES",

    "BFCL_ST_MT_CASES",

    "GAIA_ST_MT_CASES",

    "MT_1T_BASE_CASES",

    "MT_1T_MISSING_PARAMS_CASES",

    "MT_1T_MISSING_FUNC_CASES",

    "MT_MT_BASE_CASES",

    "MT_MT_MISSING_PARAMS_CASES",

    "MT_MT_MISSING_FUNC_CASES",

    "ARGUMENT_CORRECTNESS_CASES",

    "ALL_SINGLETURN_CASES",

    "ALL_MULTITURN_CASES",

    "ALL_CASES_BY_DIMENSION",

    "ALL_TEST_CASES",
]

