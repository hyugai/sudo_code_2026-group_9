import os
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

from telesale_agent.core.interfaces import Perceiver
from telesale_agent.core.models import Perception, TurnContext
from telesale_agent.config.settings import settings

class IntentSchema(BaseModel):
    intent: str = Field(
        description="The main intent of the customer. Must be exactly one of: ask_product, ask_return_policy, ask_shipping_policy, price_objection, complain, unknown"
    )
    entities: dict = Field(
        description="Entities extracted from the utterance, e.g., {'product_name': 'headphones', 'price': 500000}", 
        default_factory=dict
    )

class LLMPerceiver(Perceiver):
    """Uses Groq LLM (LLaMA) to extract intents and entities from customer utterances."""
    
    def __init__(self, model_name: str = "openai/gpt-oss-20b"):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables. Please check your .env file.")
        
        # Temperature = 0 for accurate, non-creative extraction
        self.llm = ChatGroq(temperature=0, model_name=model_name, groq_api_key=api_key)
        self.structured_llm = self.llm.with_structured_output(IntentSchema)

    async def perceive(self, context: TurnContext) -> Perception:
        if context.input.text is None:
            raise ValueError("LLMPerceiver only processes text. ASR (e.g., Whisper) is required to convert audio to text first.")

        transcript = context.input.text.strip()
        
        prompt = f"""You are an advanced NLU AI system designed for a telesales call center.
Analyze the following customer utterance and extract the main intent and relevant entities.
The utterance is in Vietnamese, but you must output the structured JSON.

Customer utterance: "{transcript}"
"""
        
        # Call Groq API for structured JSON
        try:
            result = await self.structured_llm.ainvoke(prompt)
            
            return Perception(
                transcript=transcript,
                intent=result.intent,
                entities=result.entities,
                confidence=1.0
            )
        except Exception as e:
            # Fallback if LLM fails
            print(f"LLMPerceiver Error: {e}")
            return Perception(
                transcript=transcript,
                intent="unknown",
                entities={},
                confidence=0.0
            )
