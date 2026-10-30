import os
import unittest
import importlib.util
from contextlib import nullcontext
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

from memory import checkpoint_url, conversation_graph


class ApiAuthenticationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient

        fake_graph = ModuleType("graph")
        fake_graph.graph = MagicMock()
        fake_graph.graph_builder = MagicMock()
        spec = importlib.util.spec_from_file_location("deployment_api", Path(__file__).with_name("main.py"))
        cls.module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"graph": fake_graph}):
            spec.loader.exec_module(cls.module)
        cls.client = TestClient(cls.module.app)

    def test_production_chat_requires_shared_secret_before_model_execution(self):
        from fastapi import HTTPException

        with patch.dict(os.environ, {"VERCEL": "1", "AI_API_KEY": "test-secret"}):
            with self.assertRaises(HTTPException) as error:
                self.module.require_api_key("incorrect")
            self.assertEqual(error.exception.status_code, 401)
            self.module.require_api_key("test-secret")

    def test_missing_production_secret_fails_closed(self):
        from fastapi import HTTPException

        with patch.dict(os.environ, {"VERCEL": "1", "AI_API_KEY": ""}):
            with self.assertRaises(HTTPException) as error:
                self.module.require_api_key()
            self.assertEqual(error.exception.status_code, 503)

    def test_authorized_chat_keeps_response_contract_and_thread_id(self):
        graph = MagicMock()
        graph.invoke.return_value = {"response": "Hello", "intent": "fitness", "messages": []}
        payload = {"session_id": "thread-one", "message": "Hi", "age": 25,
                   "height": 175, "weight": 70, "goal": "fitness",
                   "activity_level": "moderate", "experience_level": "beginner"}
        with patch.dict(os.environ, {"VERCEL": "1", "AI_API_KEY": "test-secret", "LANGSMITH_TRACING": "false"}):
            with patch.object(self.module, "conversation_graph", return_value=nullcontext(graph)):
                denied = self.client.post("/chat", json=payload)
                self.assertEqual(denied.status_code, 401)
                graph.invoke.assert_not_called()
                response = self.client.post("/chat", json=payload, headers={"X-AI-API-Key": "test-secret"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello", "intent": "fitness", "history": []})
        self.assertEqual(graph.invoke.call_args.kwargs["config"]["configurable"]["thread_id"], "thread-one")


class ConversationMemoryTests(unittest.TestCase):
    def test_neon_sqlalchemy_url_is_accepted_by_psycopg(self):
        with patch.dict(os.environ, {"CHECKPOINT_DATABASE_URL": "postgresql+psycopg://example/db"}):
            self.assertEqual(checkpoint_url(), "postgresql://example/db")

    def test_vercel_uses_request_scoped_persistent_checkpointer(self):
        from langgraph.checkpoint.postgres import PostgresSaver

        builder = MagicMock()
        with patch.dict(os.environ, {"VERCEL": "1", "CHECKPOINT_DATABASE_URL": "postgresql://example/db"}):
            with patch.object(PostgresSaver, "from_conn_string") as connect:
                with conversation_graph(builder, object()) as graph:
                    self.assertIs(graph, builder.compile.return_value)
                    builder.compile.assert_called_once_with(
                        checkpointer=connect.return_value.__enter__.return_value
                    )
                    connect.return_value.__exit__.assert_not_called()
                connect.return_value.__exit__.assert_called_once()

    def test_local_development_keeps_in_memory_graph(self):
        local_graph = object()
        with patch.dict(os.environ, {"VERCEL": "0", "CHECKPOINT_DATABASE_URL": ""}):
            with conversation_graph(MagicMock(), local_graph) as graph:
                self.assertIs(graph, local_graph)


if __name__ == "__main__":
    unittest.main()
