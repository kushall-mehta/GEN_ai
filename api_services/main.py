from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from langsmith import traceable

# Load tracing and model settings before importing modules that create clients.
API_DIR = Path(__file__).resolve().parent
load_dotenv(API_DIR / ".env")
load_dotenv(API_DIR.parent / ".env")

from schemas import ChatRequest
from graph import graph

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Fitness Assistant API is running"}


@app.post("/chat")
@traceable(
    name="Fitness chat request",
    run_type="chain",
    process_inputs=lambda _: {"request": "[redacted]"},#intentionally hiding the actual input/output from LangSmith.
    process_outputs=lambda _: {"response": "[redacted]"},
)
#This is very important for your conversation memory. for graph #MemorySaver() used
def chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.session_id
        }
    }

    result = graph.invoke(
        {
            "message": request.message,
            "age": request.age,
            "height": request.height,
            "weight": request.weight,
            "goal": request.goal,
            "activity_level": request.activity_level,
            "experience_level": request.experience_level
        },#helps identify/filter runs in LangSmith.
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