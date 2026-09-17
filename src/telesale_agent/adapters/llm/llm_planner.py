import os
import json
import dataclasses
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

from telesale_agent.core.interfaces import Planner
from telesale_agent.core.models import ActionPlan, TurnContext
from telesale_agent.config.settings import settings

class ActionPlanSchema(BaseModel):
    action: str = Field(description="The next action to take, e.g., 'respond_to_customer', 'transfer_to_human', 'call_api'")
    rationale: str = Field(description="The rationale behind this decision")
    target_intent: str | None = Field(description="The target intent if applicable", default=None)
    response_text: str | None = Field(description="The final response text to speak/chat with the customer (must be in Vietnamese)", default=None)
    tool_name: str | None = Field(description="The name of the tool to call if action is 'call_api'", default=None)
    arguments: dict = Field(description="Arguments for the tool", default_factory=dict)

class LLMPlanner(Planner):
    """
    Planner using Groq LLM (LLaMA) to decide the next action and generate a response.
    """
    
    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        
        self.llm = ChatGroq(temperature=0.3, model_name=model_name, groq_api_key=api_key)
        self.structured_llm = self.llm.with_structured_output(ActionPlanSchema)
        
    async def plan(self, context: TurnContext) -> ActionPlan:
        intent = context.perception.intent if context.perception else "unknown"
        transcript = context.perception.transcript if context.perception else ""
        
        call_brief = dataclasses.asdict(context.call_brief) if context.call_brief else {}
        knowledge = context.retrieved.knowledge if context.retrieved else []
        
        prompt = f"""You are a professional and skillful Telesales Agent.
Your task is to determine the next action and write a response for the customer based on the Call Brief and retrieved Knowledge.
NOTE: Your internal reasoning can be in English, but the final `response_text` MUST be in fluent, polite Vietnamese suitable for a phone conversation.

-- CUSTOMER INFO & CONTEXT --
Current Customer Intent: {intent}
Recent Customer Utterance: "{transcript}"
Call Brief:
{json.dumps(call_brief, ensure_ascii=False, indent=2)}

-- RETRIEVED KNOWLEDGE (RAG) --
{json.dumps(knowledge, ensure_ascii=False, indent=2)}

-- INSTRUCTIONS --
1. Analyze the context and decide the next action ('respond_to_customer' or 'transfer_to_human').
2. ALWAYS provide a `response_text` naturally and politely in Vietnamese, even if you are transferring the call (e.g., "Dạ, để em nối máy cho chuyên viên hỗ trợ anh/chị nhé...").
3. Base your pricing and policy answers STRICTLY on the RETRIEVED KNOWLEDGE. Do not hallucinate information.

Formulate your action plan:"""

        try:
            result = await self.structured_llm.ainvoke(prompt)
            return ActionPlan(
                action=result.action,
                rationale=result.rationale,
                target_intent=result.target_intent,
                response_text=result.response_text,
                tool_name=result.tool_name,
                arguments=result.arguments
            )
        except Exception as e:
            print(f"LLMPlanner Error: {e}")
            return ActionPlan(
                action="transfer_to_human",
                rationale=f"LLM Error: {str(e)}",
                response_text="Dạ em xin lỗi, hệ thống đang gặp chút sự cố. Em sẽ chuyển máy cho bạn tư vấn viên hỗ trợ mình ngay ạ."
            )
