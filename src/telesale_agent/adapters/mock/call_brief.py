from telesale_agent.core.interfaces import CallBriefBuilder
from telesale_agent.core.models import CallBrief, TurnContext

class SimpleCallBriefBuilder(CallBriefBuilder):
    """Local demo that combines identity and retrieved data."""

    async def build_call_brief(self, context: TurnContext) -> CallBrief:
        if context.identity is None or context.retrieved is None:
            raise ValueError("identity and retrieved context are required")

        customer_name = context.identity.profile.get("name")
        
        needs = []
        if context.perception:
            if context.perception.intent == "ask_return_policy":
                needs.append("Khách hàng quan tâm đến chính sách đổi trả.")
            elif context.perception.intent == "ask_shipping_policy":
                needs.append("Khách hàng quan tâm đến chính sách giao hàng.")
            elif context.perception.intent == "price_objection":
                needs.append("Khách hàng có lo ngại về giá cả.")
                
        return CallBrief(
            customer_id=context.identity.customer_id,
            customer_name=str(customer_name) if customer_name else None,
            summary="No previous customer history was found."
            if not context.retrieved.customer_history
            else "Customer history is available for this conversation.",
            needs=needs,
            active_promotions=context.retrieved.active_promotions,
        )
