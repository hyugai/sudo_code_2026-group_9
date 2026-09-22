from telesale_agent.core.interfaces import Guardrail
from telesale_agent.core.models import PolicyDecision, TurnContext

class AllowAllGuardrail(Guardrail):
    """Local demo only. It must be replaced before production use."""

    async def check(self, context: TurnContext) -> PolicyDecision:
        return PolicyDecision(allowed=True)
