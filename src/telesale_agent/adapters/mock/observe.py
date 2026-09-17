from telesale_agent.core.interfaces import Observer
from telesale_agent.core.models import ActionStatus, Observation, TurnContext

class BasicObserver(Observer):
    """Local demo that logs the result of the previous action."""

    async def observe(self, context: TurnContext) -> Observation:
        if context.action_result is None:
            raise ValueError("action result is required before observing")

        match context.action_result.status:
            case ActionStatus.EXECUTED:
                summary = "Action completed successfully."
            case ActionStatus.BLOCKED:
                summary = "Action blocked by policy guardrails."
            case ActionStatus.FAILED:
                summary = "Action failed."
            case _:
                summary = "Unknown status."

        return Observation(summary=summary, should_continue=False)
