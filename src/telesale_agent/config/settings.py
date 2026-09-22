"""Global configuration settings for the agent harness."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "default")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")

settings = Settings()
