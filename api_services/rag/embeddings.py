"""Gemini text embeddings using the REST API and existing dependencies."""

import math
import os

import requests
from langchain_core.embeddings import Embeddings


MODEL = "gemini-embedding-2"
DIMENSIONS = 768
# Version the collection whenever the model, dimensions, or input format changes.
COLLECTION_NAME = "fitness_knowledge_gemini2_768_v1"


class GeminiEmbeddings(Embeddings):
    def __init__(self):
        self._api_key = os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini embeddings.")

    def _embed(self, text: str) -> list[float]:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:embedContent",
            headers={"x-goog-api-key": self._api_key},
            json={
                "model": f"models/{MODEL}",
                "content": {"parts": [{"text": text}]},
                "outputDimensionality": DIMENSIONS,
            },
            timeout=(5, 30),
        )
        response.raise_for_status()
        values = response.json()["embedding"]["values"]
        if len(values) != DIMENSIONS or not all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in values
        ):
            raise ValueError("Gemini returned an invalid embedding vector.")
        return values

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Each chunk needs its own vector; multiple inputs can be aggregated by
        # Embedding 2, which would lose the mapping between chunks and vectors.
        return [self._embed(f"title: none | text: {text}") for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(f"task: search result | query: {text}")
