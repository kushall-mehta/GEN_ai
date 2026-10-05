import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq


API_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(API_ENV_FILE)
load_dotenv(API_ENV_FILE.parents[1] / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
)