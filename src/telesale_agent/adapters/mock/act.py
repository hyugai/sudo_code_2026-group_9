from telesale_agent.core.interfaces import Actor
from telesale_agent.core.models import ActionResult, ActionStatus, TurnContext

class LocalActor(Actor):
    """Local demo that executes generic system tools."""

    async def act(self, context: TurnContext) -> ActionResult:
        if context.plan is None:
            raise ValueError("action plan is required")

        if context.plan.action in ("respond_to_customer", "transfer_to_human", "call_api"):
            return ActionResult(status=ActionStatus.EXECUTED)
            
        return ActionResult(
            status=ActionStatus.FAILED,
            error=f"unknown action '{context.plan.action}'",
        )
