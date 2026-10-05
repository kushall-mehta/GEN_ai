from llm.groq import llm

from state import format_chat_history


def fitness_node(state):

    conversation_history = format_chat_history(
        state["messages"]
    )

    prompt = f"""
You are an AI fitness assistant.

User profile:
Age: {state["age"]}
Height: {state["height"]} cm
Weight: {state["weight"]} kg
Goal: {state["goal"]}
Activity level: {state["activity_level"]}
Experience level: {state["experience_level"]}

Previous conversation:
{conversation_history}

Current user question:
{state["message"]}

Use the user's profile and previous conversation to understand
the current question and maintain conversation continuity.

Do not ask for profile information again if it is already available.

Give a helpful and personalized fitness answer.
"""

    response = llm.invoke(prompt)

    return {
        "response": response.content
    }