from telesale_agent.core.interfaces import Retriever
from telesale_agent.core.models import RetrievedContext, TurnContext
from telesale_agent.adapters.mock.mock_data import RETURN_POLICY, SHIPPING_POLICY, PRIVACY_POLICY, PRODUCTS, PRODUCT_ALIASES

class MockDataRetriever(Retriever):
    """Local demo that retrieves data from mock_data based on intent."""

    async def retrieve(self, context: TurnContext) -> RetrievedContext:
        knowledge = []
        if context.perception:
            intents = context.perception.intents or [context.perception.intent]
            transcript = context.perception.transcript.lower()
            
            # Route to correct database based on Intent (Pre-filtering)
            if "ask_policy" in intents:
                matched_any = False
                if any(k in transcript for k in ["bảo mật", "thông tin", "quyền riêng tư"]):
                    knowledge.append(PRIVACY_POLICY)
                    matched_any = True
                if any(k in transcript for k in ["đổi trả", "hoàn tiền", "trả hàng", "bảo hành"]):
                    knowledge.append(RETURN_POLICY)
                    matched_any = True
                if any(k in transcript for k in ["giao hàng", "ship", "vận chuyển", "freeship"]):
                    knowledge.append(SHIPPING_POLICY)
                    matched_any = True
                    
                if not matched_any:
                    # Fallback: Return all if the customer asks generally about "policies"
                    knowledge.extend([RETURN_POLICY, SHIPPING_POLICY, PRIVACY_POLICY])
                    
            if "ask_product" in intents:
                # Use extracted entities to query the Catalog DB directly
                product_found = False
                entities = context.perception.entities or {}
                
                for val in entities.values():
                    if isinstance(val, str):
                        val_lower = val.lower()
                        for alias, prod_id in PRODUCT_ALIASES.items():
                            if alias in val_lower or val_lower in alias:
                                if prod_id in PRODUCTS and PRODUCTS[prod_id] not in knowledge:
                                    knowledge.append(PRODUCTS[prod_id])
                                    product_found = True
                
                # Fallback to keyword matching in transcript if LLM failed to extract the entity
                if not product_found:
                    for alias, prod_id in PRODUCT_ALIASES.items():
                        if alias in transcript and PRODUCTS[prod_id] not in knowledge:
                            knowledge.append(PRODUCTS[prod_id])
                            product_found = True
                            
                if not product_found:
                    short_products = [{"name": p["name"], "price_vnd": p["price_vnd"]} for p in PRODUCTS.values()]
                    knowledge.append({"available_products": short_products})
                
        return RetrievedContext(knowledge=knowledge)
