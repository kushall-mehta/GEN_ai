from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from state import FitnessState

# from nodes.router import *
from nodes.router import router_node, route_intent

from nodes.bmi import bmi_node
from nodes.diet import diet_node
from nodes.workout import workout_node
from nodes.fitness import fitness_node

from langgraph.checkpoint.memory import MemorySaver


def message_node(state):
    return {
        "messages": [
            HumanMessage(content=state["message"])
        ]
    }


def save_response_node(state):
    return {
        "messages": [
            AIMessage(content=state["response"])
        ]
    }


# CREATE GRAPH

graph_builder = StateGraph(FitnessState)


# ADD NODES

graph_builder.add_node(
    "add_user_message",
    message_node
)

graph_builder.add_node(
    "router",
    router_node
)

graph_builder.add_node(
    "diet",
    diet_node
)

graph_builder.add_node(
    "workout",
    workout_node
)

graph_builder.add_node(
    "fitness",
    fitness_node
)

graph_builder.add_node(
    "bmi",
    bmi_node
)

graph_builder.add_node(
    "save_response",
    save_response_node
)

# START → ADD USER MESSAGE

graph_builder.add_edge(
    START,
    "add_user_message"
)

# ADD USER MESSAGE → ROUTER

graph_builder.add_edge(
    "add_user_message",
    "router"
)


# ROUTER → SELECTED NODE

graph_builder.add_conditional_edges(
    "router",

    # WHERE to start deciding
    route_intent,

    # HOW to decide
    # route_intent looks at the state
    # and tells LangGraph which route was selected.

    {
        "diet": "diet",
        "workout": "workout",
        "fitness": "fitness",
        "bmi": "bmi"
    }
)


# SELECTED NODE → SAVE RESPONSE

# Diet → Save response
graph_builder.add_edge(
    "diet",
    "save_response"
)

# Workout → Save response
graph_builder.add_edge(
    "workout",
    "save_response"
)

# Fitness → Save response
graph_builder.add_edge(
    "fitness",
    "save_response"
)

# BMI → Save response
graph_builder.add_edge(
    "bmi",
    "save_response"
)

# SAVE RESPONSE → END

graph_builder.add_edge(
    "save_response",
    END
)


# MEMORY

memory = MemorySaver()


# COMPILE GRAPH

graph = graph_builder.compile(
    checkpointer=memory
)


# SHOW GRAPH AS MERMAID

print(graph.get_graph().draw_mermaid())

# --------------------------------------------------
# CONVERSATION FLOW
# --------------------------------------------------

# First request
#
# messages = []
#
#        ↓ message_node
#
# messages = [
#     HumanMessage("Give me a chest workout")
# ]
#
#        ↓
# checkpoint
#
#
# Second request with SAME session_id
#
#        ↓ message_node
#
# messages = [
#     HumanMessage("Give me a chest workout"),
#     HumanMessage("Make it easier")
# ]
#
#
# Then router can look at the previous USER message
# and keep the conversation in the workout branch.