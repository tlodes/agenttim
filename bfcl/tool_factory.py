"""
Factory for wrapping BFCL Python class methods as LangChain StructuredTool instances.
Each BFCL API class (GorillaFileSystem, TradingBot, etc.) has public methods that
serve as tools. This module instantiates those classes, loads their scenario state,
and wraps every public method as a StructuredTool with a Pydantic args_schema built
from the JSON func_doc schema that ships with every converted test case.
"""
import importlib
import logging
from copy import deepcopy
from typing import Any
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field, create_model
from agenttim.bfcl.domain_config import CLASS_TO_MODULE
logger = logging.getLogger(__name__)
_JSON_TYPE_MAP: dict[str, type] = {

    "string": str,

    "integer": int,

    "float": float,

    "boolean": bool,
}
class BFCLToolFactory:

    """Creates LangChain StructuredTool instances from BFCL Python classes."""

    def __init__(self) -> None:

        """Initialise the factory.

        The full func-doc registry is built lazily from test-case data
        so no extra file I/O is needed at construction time.
        """

        self._func_doc_registry: dict[str, dict] = {}

    def create_tools_for_test_case(

        self,

        test_case: dict,

        all_tools: bool = False,

    ) -> tuple[list[BaseTool], dict[str, Any]]:

        """Create tools and class instances for a single test case.

        Args:
            test_case: Converted BFCL test case dict with ``initial_config``,
                       ``available_functions``, etc.
            all_tools: If True, load all 128 tools (for multi-agent routing
                       tests).  If False, only load tools for classes that
                       appear in ``initial_config``.

        Returns:
            A 2-tuple of (tools, instances) where *tools* is a list of
            LangChain ``StructuredTool`` objects and *instances* maps each
            class name to its live Python instance (for state comparison
            after execution).
        """

        initial_config = test_case.get("initial_config", {})

        func_doc_index = self._build_func_doc_index(

            test_case.get("available_functions", []),

        )

        involved_classes = set(initial_config.keys())

        classes_to_load = (

            list(CLASS_TO_MODULE.keys()) if all_tools else list(involved_classes)

        )

        instances: dict[str, Any] = {}

        tools: list[BaseTool] = []

        for class_name in classes_to_load:

            instance = self._create_instance(class_name, initial_config)

            instances[class_name] = instance

            class_tools = self._wrap_instance_methods(

                instance, class_name, func_doc_index,

            )

            tools.extend(class_tools)

        return tools, instances

    def create_instances(

        self,

        test_case: dict,

        all_classes: bool = False,

    ) -> dict[str, Any]:

        """Create class instances only (no tools). Used for GT execution.

        Args:
            test_case: Converted BFCL test case dict with ``initial_config``.
            all_classes: If True, instantiate all 8 classes.

        Returns:
            Dict mapping class_name -> live Python instance.
        """

        initial_config = test_case.get("initial_config", {})

        long_context = test_case.get("long_context", False)

        classes_to_load = (

            list(CLASS_TO_MODULE.keys()) if all_classes

            else list(initial_config.keys())

        )

        return {

            name: self._create_instance(name, initial_config, long_context)

            for name in classes_to_load

        }

    @staticmethod

    def _create_instance(

        class_name: str,

        initial_config: dict[str, Any],

        long_context: bool = False,

    ) -> Any:

        """Import a BFCL class, instantiate it, and load its scenario state."""

        module_name = CLASS_TO_MODULE[class_name]

        module_path = f"agenttim.bfcl.func_source_code.{module_name}"

        module = importlib.import_module(module_path)

        cls = getattr(module, class_name)

        instance = cls()

        scenario = deepcopy(initial_config.get(class_name, {}))

        if hasattr(instance, "_load_scenario"):

            instance._load_scenario(scenario, long_context=long_context)

        return instance

    def _wrap_instance_methods(

        self,

        instance: Any,

        class_name: str,

        func_doc_index: dict[str, dict],

    ) -> list[BaseTool]:

        """Wrap every public method on *instance* as a StructuredTool."""

        tools: list[BaseTool] = []

        for method_name in self._public_method_names(instance):

            func_doc = func_doc_index.get(method_name)

            if func_doc is None:

                func_doc = self._func_doc_registry.get(method_name)

            if func_doc is None:

                logger.warning(

                    "No func_doc for %s.%s – skipping", class_name, method_name,

                )

                continue

            tool = _make_tool(instance, method_name, func_doc)

            tools.append(tool)

        return tools

    @staticmethod

    def _public_method_names(instance: Any) -> list[str]:

        """Return sorted public method names of *instance*."""

        return sorted(

            name

            for name in dir(instance)

            if not name.startswith("_") and callable(getattr(instance, name))

        )

    def _build_func_doc_index(

        self,

        available_functions: list[dict],

    ) -> dict[str, dict]:

        """Index func-doc schemas by function name.

        Also merges them into the persistent ``_func_doc_registry`` so that
        subsequent ``all_tools=True`` calls can find docs for functions not
        present in the current test case's ``available_functions``.
        """

        index: dict[str, dict] = {}

        for func_doc in available_functions:

            name = func_doc["name"]

            index[name] = func_doc

            self._func_doc_registry[name] = func_doc

        return index

    def seed_func_docs(self, test_cases: list[dict]) -> None:

        """Pre-populate the func-doc registry from a list of test cases.

        Call this once with *all* converted test cases before running
        ``all_tools=True`` evaluations so that every function has a schema.

        Args:
            test_cases: List of converted BFCL test case dicts.
        """

        for tc in test_cases:

            for func_doc in tc.get("available_functions", []):

                self._func_doc_registry[func_doc["name"]] = func_doc
def _make_tool(

    instance: Any,

    method_name: str,

    func_doc: dict,
) -> StructuredTool:

    """Create a single StructuredTool that delegates to *instance.method_name*."""

    method = getattr(instance, method_name)

    args_schema = _build_pydantic_model(method_name, func_doc.get("parameters", {}))

    def _invoke(**kwargs: Any) -> Any:

        return method(**kwargs)

    async def _ainvoke(**kwargs: Any) -> Any:

        return method(**kwargs)

    return StructuredTool(

        name=method_name,

        description=func_doc.get("description", ""),

        args_schema=args_schema,

        func=_invoke,

        coroutine=_ainvoke,

    )
def _build_pydantic_model(

    tool_name: str,

    params_schema: dict,
) -> type[BaseModel]:

    """Dynamically create a Pydantic model from a BFCL parameter schema."""

    properties = params_schema.get("properties", {})

    required = set(params_schema.get("required", []))

    fields: dict[str, Any] = {}

    for name, prop in properties.items():

        python_type = _resolve_type(prop)

        is_required = name in required

        default = ... if is_required else prop.get("default", None)

        description = prop.get("description", "")

        fields[name] = (python_type, Field(default=default, description=description))

    return create_model(f"{tool_name}_args", **fields)
def _resolve_type(prop: dict) -> type:

    """Map a BFCL JSON-schema property to a Python type annotation."""

    json_type = prop.get("type", "string")

    if json_type in _JSON_TYPE_MAP:

        return _JSON_TYPE_MAP[json_type]

    if json_type == "array":

        return _resolve_array_type(prop)

    if json_type == "dict":

        return dict[str, Any]

    return Any
def _resolve_array_type(prop: dict) -> type:

    """Resolve array types to ``list[<item_type>]``."""

    items = prop.get("items", {})

    item_type_str = items.get("type", "string")

    item_type = _JSON_TYPE_MAP.get(item_type_str, Any)

    return list[item_type]

