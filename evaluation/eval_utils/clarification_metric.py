"""
Clarification Detection Metric for Multi-Turn Evaluation.
Measures whether an agent appropriately asks for clarification when
the user's request is ambiguous or incomplete. This is a key metric
for evaluating multi-turn conversational agents.
Scientific Description:
    The Clarification Detection Score (CDS) quantifies an agent's ability
    to recognize incomplete or ambiguous user requests and respond with
    appropriate clarifying questions rather than proceeding with assumptions.

    CDS = w_q * I_question + w_k * (K_match / K_total) - w_e * I_execution

    Where:
    - I_question: Binary indicator for presence of question syntax (?)
    - K_match: Count of clarification keywords detected
    - K_total: Normalization factor for keyword density
    - I_execution: Binary indicator for premature tool execution
    - w_q, w_k, w_e: Weighting factors (default: 0.4, 0.4, 0.2)

    The metric penalizes agents that execute tools without first clarifying
    ambiguous requests, while rewarding those that ask relevant questions
    with options or examples.
Reference:
    Based on BFCL v3 Multi-Turn evaluation methodology where "missing_param"
    test cases require the agent to ask for missing information before
    proceeding with tool execution.
"""
from typing import List, Optional
class ClarificationMetric:

    """
    Metric to detect if an agent asked for clarification.

    Uses keyword matching and syntactic analysis to determine if the agent's
    response is a clarification request rather than a direct answer or
    premature tool execution.

    Attributes:
        CLARIFICATION_KEYWORDS: List of German and English clarification indicators
        threshold: Minimum score to consider clarification detected
        score: The computed clarification score (0.0 to 1.0)
        reason: Human-readable explanation of the score

    Example:
        ```python
        metric = ClarificationMetric(threshold=0.5)
        score = metric.measure("Welche Collection moechten Sie? (DashboardCases, DashboardTasks)")
        print(f"Clarification detected: {metric.is_success()}")  # True
        print(f"Score: {score}")  # 1.0
        ```
    """

    CLARIFICATION_KEYWORDS: List[str] = [

        "welche", "welchen", "welches", "welcher",

        "wie viele", "wieviele",

        "was fuer", "was für",

        "moechten", "möchten", "wollen", "sollen",

        "koennen sie", "können sie", "koennten sie", "könnten sie",

        "meinen", "meinten", "gemeint",

        "bevorzugen", "praeferieren", "präferieren",

        "optionen", "option", "moeglichkeiten", "möglichkeiten",

        "auswahl", "auswaehlen", "auswählen",

        "z.b.", "zum beispiel", "beispielsweise",

        "bitte geben sie an", "bitte spezifizieren",

        "genauer", "praeziser", "präziser",

        "which", "what kind", "how many",

        "would you like", "do you want", "should i",

        "could you", "can you", "please specify", "please provide",

        "options", "choose", "select",

        "do you mean", "did you mean",

        "for example", "e.g.", "such as",

        "more specifically", "clarify",

    ]

    EXECUTION_INDICATORS: List[str] = [

        "pipeline", "aggregation", "ergebnis", "ergebnisse",

        "hier sind", "hier ist", "zeigt",

        "daten:", "resultate:",

        "erfolgreich", "abgeschlossen",

        "gefunden:", "insgesamt:",

        "result", "results", "here are", "here is",

        "data:", "output:",

        "successfully", "completed",

        "found:", "total:",

    ]

    def __init__(

        self,

        expected_clarification: Optional[str] = None,

        threshold: float = 0.5,

    ):

        """
        Initialize the clarification metric.

        Args:
            expected_clarification: Expected clarification text for semantic matching
                                   (currently unused, reserved for future LLM-based matching)
            threshold: Minimum score to consider clarification detected (default: 0.5)
        """

        self.expected_clarification = expected_clarification

        self.threshold = threshold

        self.score: float = 0.0

        self.reason: str = ""

        self._keyword_matches: int = 0

        self._has_question: bool = False

        self._has_execution: bool = False

    def measure(self, agent_response: str) -> float:

        """
        Measure if the agent response is a clarification request.

        Args:
            agent_response: The agent's response text to evaluate

        Returns:
            Score between 0.0 (no clarification) and 1.0 (clear clarification)
        """

        response_lower = agent_response.lower()

        self._has_question = "?" in agent_response

        self._keyword_matches = sum(

            1 for kw in self.CLARIFICATION_KEYWORDS

            if kw in response_lower

        )

        self._has_execution = any(

            ind in response_lower for ind in self.EXECUTION_INDICATORS

        )

        self._calculate_score()

        return self.score

    def _calculate_score(self) -> None:

        """Calculate the clarification score based on detected signals."""

        w_question = 0.4

        w_keywords = 0.4

        w_execution_penalty = 0.3

        keyword_factor = min(self._keyword_matches / 3.0, 1.0)

        base_score = (

            w_question * (1.0 if self._has_question else 0.0) +

            w_keywords * keyword_factor

        )

        if self._has_execution:

            base_score -= w_execution_penalty

        self.score = max(0.0, min(1.0, base_score))

        self._generate_reason()

    def _generate_reason(self) -> None:

        """Generate a human-readable explanation of the score."""

        parts = []

        if self._has_question:

            parts.append("question mark detected")

        if self._keyword_matches > 0:

            parts.append(f"{self._keyword_matches} clarification keyword(s)")

        if self._has_execution:

            parts.append("tool execution detected (penalty applied)")

        if self.score >= 0.8:

            prefix = "Strong clarification signal"

        elif self.score >= 0.5:

            prefix = "Likely clarification"

        elif self.score > 0:

            prefix = "Weak clarification signal"

        else:

            prefix = "No clarification detected"

        if parts:

            self.reason = f"{prefix}: {', '.join(parts)}"

        else:

            self.reason = prefix

    def is_success(self) -> bool:

        """Check if clarification was detected (score >= threshold)."""

        return self.score >= self.threshold

    def get_details(self) -> dict:

        """Get detailed breakdown of the metric calculation."""

        return {

            "score": self.score,

            "threshold": self.threshold,

            "success": self.is_success(),

            "reason": self.reason,

            "has_question": self._has_question,

            "keyword_matches": self._keyword_matches,

            "has_execution_indicators": self._has_execution,

        }

