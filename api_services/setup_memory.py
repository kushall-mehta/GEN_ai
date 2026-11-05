"""Run once before release: python setup_memory.py (never during a request)."""

from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

from memory import checkpoint_url


def main():
    base = Path(__file__).resolve().parent
    load_dotenv(base / ".env")
    load_dotenv(base.parent / ".env")
    with PostgresSaver.from_conn_string(checkpoint_url()) as checkpointer:
        checkpointer.setup()
    print("Conversation checkpoint tables are ready.")


if __name__ == "__main__":
    main()
