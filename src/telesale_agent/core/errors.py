class PipelineStageError(RuntimeError):
    """Error raised when one named pipeline stage fails."""

    def __init__(self, stage: str, conversation_id: str, cause: Exception) -> None:
        self.stage = stage
        self.conversation_id = conversation_id
        self.cause = cause
        super().__init__(
            f"stage '{stage}' failed for conversation '{conversation_id}': {cause}"
        )


class AgentLoopLimitError(RuntimeError):
    """Error raised when the agent does not finish within the configured limit."""

