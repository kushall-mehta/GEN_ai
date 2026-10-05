import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_postgres import PGVector

# Load the same API environment file no matter which folder starts the API.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_FILE)
load_dotenv(dotenv_path=ENV_FILE.parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is missing from {ENV_FILE}")
#
# CONNECTION = "postgresql+psycopg://postgres:postgres@localhost:5433/gym_ai"

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is required for Hugging Face embedding inference.")

EMBEDDING_MODEL = os.getenv(
    "HF_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
COLLECTION_NAME = "fitness_knowledge_hf_minilm"

embeddings = HuggingFaceEndpointEmbeddings(
    model=EMBEDDING_MODEL,
    task="feature-extraction",
    huggingfacehub_api_token=HF_TOKEN,
)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=DATABASE_URL,
    use_jsonb=True,
)

# Keep the original unfiltered retriever here as a reference.
# retriever = vector_store.as_retriever(
#     search_kwargs={"k": 4}
# )

def get_retriever(category: Literal["diet", "workout"]):
    # Only return chunks that belong to the requested PDF category.
    return vector_store.as_retriever(
        search_kwargs={
            "k": 4,
            "filter": {"category": category},
        }
    )
