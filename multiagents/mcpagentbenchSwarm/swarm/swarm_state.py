"""
Shared state for MCPAgentBench Swarm pattern.
All agents see all messages. Consensus emerges from discussion.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
class MessageType(str, Enum):

    ANALYSIS = "analysis"

    PROPOSAL = "proposal"

    CRITIQUE = "critique"

    AGREEMENT = "agreement"

    REFINEMENT = "refinement"

    FINAL_DECISION = "final_decision"
@dataclass
class SwarmMessage:

    """A message in the swarm discussion."""

    sender: str

    message_type: MessageType

    content: str

    timestamp: float = 0.0

    tool_calls_proposed: list[dict] = field(default_factory=list)
@dataclass
class SwarmState:

    """Shared state visible to all swarm agents."""

    user_request: str = ""

    messages: list[SwarmMessage] = field(default_factory=list)

    proposed_tool_calls: list[dict] = field(default_factory=list)

    agreed_tool_calls: list[dict] = field(default_factory=list)

    execution_results: list[dict] = field(default_factory=list)

    current_round: int = 0

    max_rounds: int = 3

    consensus_reached: bool = False

    participating_domains: list[str] = field(default_factory=list)

    agents_responded_this_round: list[str] = field(default_factory=list)

    def add_message(self, sender: str, msg_type: MessageType, content: str,

                    tool_calls: list[dict] | None = None) -> None:

        self.messages.append(SwarmMessage(

            sender=sender,

            message_type=msg_type,

            content=content,

            timestamp=datetime.now().timestamp(),

            tool_calls_proposed=tool_calls or [],

        ))

    def format_discussion_history(self) -> str:

        """Format all messages for agent context."""

        lines = []

        for msg in self.messages:

            lines.append(f"[{msg.sender}] ({msg.message_type.value}): {msg.content}")

            if msg.tool_calls_proposed:

                for tc in msg.tool_calls_proposed:

                    lines.append(f"  → Tool: {tc['name']}({tc.get('arguments', {})})")

        return "\n".join(lines)

    def count_agreements(self) -> int:

        return sum(

            1 for m in self.messages

            if m.message_type == MessageType.AGREEMENT

            and m.timestamp > (self.messages[-1].timestamp - 60 if self.messages else 0)

        )

    def get_latest_proposals(self) -> list[dict]:

        """Get tool calls from the most recent proposal."""

        for msg in reversed(self.messages):

            if msg.message_type in (MessageType.PROPOSAL, MessageType.REFINEMENT):

                return msg.tool_calls_proposed

        return []

