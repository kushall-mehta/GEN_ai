from llm.groq import llm
from scope_policy import classify_request, SUPPORTED


def router_node(state):
    intent = classify_request(state["message"], state.get("last_supported_intent"), llm)
    return {
        "intent": intent,
        "last_supported_intent": intent if intent in SUPPORTED else "",
    }


def route_intent(state):
    return state["intent"]
