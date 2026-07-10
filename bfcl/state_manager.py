"""Manages test sessions with dual class instances (model vs ground-truth).
Each BFCL test case runs two parallel sets of class instances:
- **model_instances**: mutated by the agent's tool calls during evaluation
- **gt_instances**: mutated by ground-truth tool calls for comparison
After all turns, comparing the two sets reveals whether the model achieved
the correct final state.
"""
import logging
from typing import Any
from langchain_core.tools import BaseTool
from agenttim.bfcl.domain_config import CLASS_TO_DOMAIN, DOMAIN_TOOLS
logger = logging.getLogger(__name__)
def _build_tool_to_class_map() -> dict[str, str]:

    """Build a reverse mapping from tool name to BFCL class name.

    Uses DOMAIN_TOOLS (tool -> domain) and the inverse of CLASS_TO_DOMAIN
    (domain -> class) to produce tool_name -> class_name.
    """

    domain_to_class: dict[str, str] = {

        domain: class_name for class_name, domain in CLASS_TO_DOMAIN.items()

    }

    tool_to_class: dict[str, str] = {}

    for domain, tools in DOMAIN_TOOLS.items():

        class_name = domain_to_class.get(domain)

        if class_name is None:

            logger.warning("No class found for domain '%s'", domain)

            continue

        for tool in tools:

            tool_to_class[tool] = class_name

    return tool_to_class
TOOL_TO_CLASS: dict[str, str] = _build_tool_to_class_map()
def _deep_equals(a: Any, b: Any) -> bool:

    """Deep equality comparison that handles nested dicts, lists, and objects.

    For objects with a custom __eq__, delegates to that. Otherwise compares
    public attributes recursively via vars().
    """

    if type(a) is not type(b):

        return False

    if isinstance(a, (str, int, float, bool, type(None))):

        return a == b

    if isinstance(a, dict):

        if a.keys() != b.keys():

            return False

        return all(_deep_equals(a[k], b[k]) for k in a)

    if isinstance(a, (list, tuple)):

        if len(a) != len(b):

            return False

        return all(_deep_equals(x, y) for x, y in zip(a, b))

    if "__eq__" in type(a).__dict__:

        return a == b

    a_vars = {k: v for k, v in vars(a).items() if not k.startswith("_")}

    b_vars = {k: v for k, v in vars(b).items() if not k.startswith("_")}

    return _deep_equals(a_vars, b_vars)
def _compute_attr_diffs(

    model_obj: Any, gt_obj: Any
) -> list[dict[str, Any]]:

    """Compare public attributes of two objects and return a list of diffs.

    Skips private attributes (starting with '_').
    """

    model_attrs = {

        k: v for k, v in vars(model_obj).items() if not k.startswith("_")

    }

    gt_attrs = {

        k: v for k, v in vars(gt_obj).items() if not k.startswith("_")

    }

    diffs: list[dict[str, Any]] = []

    all_keys = set(model_attrs.keys()) | set(gt_attrs.keys())

    for key in sorted(all_keys):

        model_val = model_attrs.get(key, "<missing>")

        gt_val = gt_attrs.get(key, "<missing>")

        if not _deep_equals(model_val, gt_val):

            diffs.append({

                "attribute": key,

                "model": _safe_repr(model_val),

                "ground_truth": _safe_repr(gt_val),

            })

    return diffs
def _safe_repr(value: Any, max_length: int = 500) -> str:

    """Produce a truncated string representation of a value."""

    text = repr(value)

    if len(text) > max_length:

        return text[:max_length] + "..."

    return text
class BFCLTestSession:

    """Holds model and GT instances for one test case."""

    def __init__(

        self,

        model_tools: list[BaseTool],

        model_instances: dict[str, Any],

        gt_instances: dict[str, Any],

    ):

        self.model_tools = model_tools

        self.model_instances = model_instances

        self.gt_instances = gt_instances

    def execute_ground_truth_turn(

        self, expected_tool_calls: list[dict[str, Any]]

    ) -> list[Any]:

        """Execute ground truth tool calls against GT instances.

        Each expected_tool_call has the shape::

            {"name": "cd", "arguments": {"folder": "document"}}

        Finds the correct GT instance that has this method and calls it.

        Args:
            expected_tool_calls: List of tool call dicts with 'name' and
                'arguments' keys.

        Returns:
            List of results from each ground-truth call, in order.
        """

        results: list[Any] = []

        for call in expected_tool_calls:

            tool_name: str = call["name"]

            arguments: dict[str, Any] = call.get("arguments", {})

            class_name = TOOL_TO_CLASS.get(tool_name)

            if class_name is None:

                class_name = self._find_class_for_method(tool_name)

            if class_name is None:

                logger.error(

                    "No GT instance found for tool '%s'", tool_name

                )

                results.append(

                    {"error": f"No instance found for tool '{tool_name}'"}

                )

                continue

            gt_instance = self.gt_instances.get(class_name)

            if gt_instance is None:

                logger.error(

                    "GT instance '%s' not in session for tool '%s'",

                    class_name,

                    tool_name,

                )

                results.append(

                    {"error": f"GT instance '{class_name}' not in session"}

                )

                continue

            method = getattr(gt_instance, tool_name, None)

            if method is None or not callable(method):

                logger.error(

                    "Method '%s' not found on GT instance '%s'",

                    tool_name,

                    class_name,

                )

                results.append(

                    {"error": f"Method '{tool_name}' not on '{class_name}'"}

                )

                continue

            try:

                result = method(**arguments)

                results.append(result)

            except Exception as exc:

                logger.error(

                    "GT call %s(**%s) failed: %s",

                    tool_name,

                    arguments,

                    exc,

                )

                results.append({"error": str(exc)})

        return results

    def compare_states(self) -> dict[str, Any]:

        """Compare model_instances vs gt_instances state.

        For each class present in both instance dicts, compares public
        (non-underscore) attributes using deep equality.

        Returns:
            Dictionary with structure::

                {
                    "match": True/False,
                    "per_class": {
                        "GorillaFileSystem": {"match": True, "diffs": []},
                        ...
                    }
                }
        """

        per_class: dict[str, dict[str, Any]] = {}

        overall_match = True

        all_class_names = (

            set(self.model_instances.keys()) | set(self.gt_instances.keys())

        )

        for class_name in sorted(all_class_names):

            model_inst = self.model_instances.get(class_name)

            gt_inst = self.gt_instances.get(class_name)

            if model_inst is None:

                per_class[class_name] = {

                    "match": False,

                    "diffs": [{"error": "Missing in model instances"}],

                }

                overall_match = False

                continue

            if gt_inst is None:

                per_class[class_name] = {

                    "match": False,

                    "diffs": [{"error": "Missing in GT instances"}],

                }

                overall_match = False

                continue

            diffs = _compute_attr_diffs(model_inst, gt_inst)

            class_match = len(diffs) == 0

            per_class[class_name] = {

                "match": class_match,

                "diffs": diffs,

            }

            if not class_match:

                overall_match = False

        return {

            "match": overall_match,

            "per_class": per_class,

        }

    def _find_class_for_method(self, method_name: str) -> str | None:

        """Fallback: search GT instances for one that has the given method."""

        for class_name, instance in self.gt_instances.items():

            if hasattr(instance, method_name) and callable(

                getattr(instance, method_name)

            ):

                return class_name

        return None

