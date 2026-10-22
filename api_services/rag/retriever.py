import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_postgres import PGVector
from rag.embeddings import COLLECTION_NAME, DIMENSIONS, GeminiEmbeddings

# Load the same API environment file no matter which folder starts the API.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_FILE)
load_dotenv(dotenv_path=ENV_FILE.parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is missing from {ENV_FILE}")
#
# CONNECTION = "postgresql+psycopg://postgres:postgres@localhost:5433/gym_ai"

embeddings = GeminiEmbeddings()

vector_store = PGVector(
    embeddings=embeddings,
    embedding_length=DIMENSIONS,
    collection_name=COLLECTION_NAME,
    connection=DATABASE_URL,
    use_jsonb=True, #Store document metadata using PostgreSQL's JSONB type b= binary/optimized format.
)

# Keep the original unfiltered retriever here as a reference.
# retriever = vector_store.as_retriever(s
#     search_kwargs={"k": 4}
# )

def get_retriever(category: Literal["diet", "workout"]):
    # Only return chunks that belong to the requested PDF category.
    return vector_store.as_retriever(
        search_kwargs={ #it gives us a searcher that we can use later on
            "k": 4,
            "filter": {"category": category},
        }
    )
#
# as_retriever()
#
# You ask the vector database:
#
# "Give me a searcher that I can use later."
