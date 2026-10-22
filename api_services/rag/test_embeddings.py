import os
import unittest
from unittest.mock import Mock, patch

import requests

from rag.embeddings import DIMENSIONS, GeminiEmbeddings


class GeminiEmbeddingsTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("rag.embeddings.requests.post")
    def test_query_uses_retrieval_prefix_and_header_auth(self, post):
        post.return_value.json.return_value = {
            "embedding": {"values": [0.1] * DIMENSIONS}
        }
        result = GeminiEmbeddings().embed_query("diet plan")
        self.assertEqual(len(result), DIMENSIONS)
        args, kwargs = post.call_args
        self.assertNotIn("test-key", args[0])
        self.assertEqual(kwargs["headers"]["x-goog-api-key"], "test-key")
        self.assertEqual(
            kwargs["json"]["content"]["parts"][0]["text"],
            "task: search result | query: diet plan",
        )
        self.assertNotIn("taskType", kwargs["json"])

    @patch("rag.embeddings.requests.post")
    def test_documents_keep_one_vector_per_chunk_in_order(self, post):
        post.side_effect = [
            Mock(json=Mock(return_value={"embedding": {"values": [v] * DIMENSIONS}}))
            for v in (0.1, 0.2)
        ]
        result = GeminiEmbeddings().embed_documents(["first", "second"])
        self.assertEqual([vector[0] for vector in result], [0.1, 0.2])
        texts = [
            call.kwargs["json"]["content"]["parts"][0]["text"]
            for call in post.call_args_list
        ]
        self.assertEqual(texts, ["title: none | text: first", "title: none | text: second"])

    @patch("rag.embeddings.requests.post")
    def test_invalid_dimensions_are_rejected(self, post):
        post.return_value.json.return_value = {"embedding": {"values": [0.1]}}
        with self.assertRaises(ValueError):
            GeminiEmbeddings().embed_query("test")

    @patch("rag.embeddings.requests.post")
    def test_quota_errors_are_not_silently_turned_into_vectors(self, post):
        post.return_value.raise_for_status.side_effect = requests.HTTPError("429")
        with self.assertRaises(requests.HTTPError):
            GeminiEmbeddings().embed_query("test")

    def test_missing_key_has_clear_error(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                GeminiEmbeddings()


if __name__ == "__main__":
    unittest.main()
