from pathlib import Path
import os
import secrets
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from langsmith import traceable

# Load tracing and model settings before importing modules that create clients.
API_DIR = Path(__file__).resolve().parent
load_dotenv(API_DIR / ".env")
load_dotenv(API_DIR.parent / ".env")

from schemas import ChatRequest
from graph import graph, graph_builder
from memory import conversation_graph


def require_api_key(x_ai_api_key: Annotated[str | None, Header()] = None):
    expected = os.getenv("AI_API_KEY", "")
    if os.getenv("VERCEL") == "1" and not expected:
        raise HTTPException(status_code=503, detail="AI API authentication is not configured")
    if expected and not secrets.compare_digest(x_ai_api_key or "", expected):
        raise HTTPException(status_code=401, detail="Invalid API key")

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Fitness Assistant API is running"}


@app.post("/chat", dependencies=[Depends(require_api_key)])
@traceable(
    name="Fitness chat request",
    run_type="chain",
    process_inputs=lambda _: {"request": "[redacted]"},#intentionally hiding the actual input/output from LangSmith.
    process_outputs=lambda _: {"response": "[redacted]"},
)
def chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.session_id
        }
    }

    with conversation_graph(graph_builder, graph) as active_graph:
        result = active_graph.invoke(
            {
                "message": request.message,
                "age": request.age,
                "height": request.height,
                "weight": request.weight,
                "goal": request.goal,
                "activity_level": request.activity_level,
                "experience_level": request.experience_level
            },
            config={
                **config,
                "tags": ["fitness-api"],
                "metadata": {"source": "fitness-api"},
            },
        )

    return {
        "message": result["response"],
        "intent": result["intent"],
        "history": [
            {
                "role": "user" if message.type == "human" else "assistant",
                "content": message.content,
            }
            for message in result["messages"]
        ],
    }
