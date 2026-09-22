"""Public API for the telesale agent harness."""

from .bootstrap import build_default_harness
from .core.errors import AgentLoopLimitError, PipelineStageError
from .core.models import (
    CallBrief,
    Channel,
    ConversationState,
    CustomerIdentity,
    TurnInput,
    TurnResult,
)

__all__ = [
    "AgentLoopLimitError",
    "CallBrief",
    "Channel",
    "ConversationState",
    "CustomerIdentity",
    "PipelineStageError",
    "TurnInput",
    "TurnResult",
    "build_default_harness",
]
