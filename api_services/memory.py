"""Database-backed conversation memory for stateless Vercel instances."""

import os
from contextlib import contextmanager


def checkpoint_url():
    value = os.getenv("CHECKPOINT_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    value = value.replace("postgresql+psycopg://", "postgresql://", 1)
    if not value.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("Set CHECKPOINT_DATABASE_URL to a Neon PostgreSQL connection URL.")
    return value


@contextmanager
def conversation_graph(builder, local_graph):
    if os.getenv("VERCEL") == "1" or os.getenv("CHECKPOINT_DATABASE_URL"):
        from langgraph.checkpoint.postgres import PostgresSaver

        # A connection belongs to this request and closes after all checkpoints flush.
        # Run setup_memory.py once before deploying, using a direct Neon connection.
        with PostgresSaver.from_conn_string(checkpoint_url()) as checkpointer:
            yield builder.compile(checkpointer=checkpointer)
    else:
        yield local_graph
