from telesale_agent.core.interfaces import Retriever
from telesale_agent.core.models import RetrievedContext, TurnContext
from telesale_agent.adapters.mock.mock_data import RETURN_POLICY, SHIPPING_POLICY, PRODUCTS, PRODUCT_ALIASES

class MockDataRetriever(Retriever):
    """Local demo that retrieves data from mock_data based on intent."""

    async def retrieve(self, context: TurnContext) -> RetrievedContext:
        knowledge = []
        if context.perception:
            intent = context.perception.intent
            if intent == "ask_return_policy":
                knowledge.append(RETURN_POLICY)
            elif intent == "ask_shipping_policy":
                knowledge.append(SHIPPING_POLICY)
            elif intent == "ask_product":
                # Tìm sản phẩm dựa trên entities (nếu có)
                product_found = False
                entities = context.perception.entities or {}
                
                # Check các value trong entities xem có khớp alias nào không
                for val in entities.values():
                    if isinstance(val, str):
                        val_lower = val.lower()
                        for alias, prod_id in PRODUCT_ALIASES.items():
                            if alias in val_lower or val_lower in alias:
                                if prod_id in PRODUCTS and PRODUCTS[prod_id] not in knowledge:
                                    knowledge.append(PRODUCTS[prod_id])
                                    product_found = True
                
                # Nếu không tìm thấy cụ thể, trả về toàn bộ danh sách sản phẩm
                if not product_found:
                    knowledge.append({"available_products": list(PRODUCTS.values())})
                
        return RetrievedContext(knowledge=knowledge)
