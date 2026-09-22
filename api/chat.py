from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add src to Python path so we can import the agent
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from telesale_agent.bootstrap import build_default_harness
from telesale_agent.core.models import TurnInput, ConversationState

app = FastAPI(title="Telesale Agent API")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

harness = build_default_harness()

# Simple in-memory session store for the UI
sessions = {}

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if req.conversation_id not in sessions:
        sessions[req.conversation_id] = ConversationState(conversation_id=req.conversation_id)
    
    state = sessions[req.conversation_id]
    turn_input = TurnInput(conversation_id=req.conversation_id, text=req.message)
    
    result = await harness.run_turn(turn_input, state)
    return {"response": result.response_text}

# Optional root endpoint for health checks
@app.get("/")
def read_root():
    return {"status": "ok"}
