"""Shared state of the LangGraph workflow.
It carries the user's message, conversation history,
fitness profile data, and the final response between nodes.
"""

from typing import TypedDict , Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class FitnessState(TypedDict):
    message: str
    #messages: list[BaseMessage] #We want LangGraph to automatically append new messages to the existing history
    messages: Annotated[list[BaseMessage], add_messages] #When a new message comes in, add it to the existing conversation history

    intent: str
    response: str

    age: int
    height: float
    weight: float
    goal: str
    activity_level: str
    experience_level: str


def format_chat_history(messages: list[BaseMessage]) -> str:
    # The latest message is the current question, which is included separately.
    previous_messages = messages[-7:-1]
    return "\n".join(
        f"{'User' if message.type == 'human' else 'Assistant'}: {message.content}"
        for message in previous_messages
    )

#
# 100 messages stored # messages[-7:-1] #only 6 message shown
def build_retrieval_query(messages: list[BaseMessage], question: str) -> str:
    # Add recent user questions so short follow-ups retrieve the right knowledge.
    previous_questions = [
        str(message.content)
        for message in messages[:-1]
        if message.type == "human"
    ][-2:]
    return "\n".join((*previous_questions, question))