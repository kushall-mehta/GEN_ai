def router_node(state):

    message = state["message"].lower()


    # Keep the original routing checks here as a reference.
    # Route nutrition questions before workout questions when both topics are mentioned.

    diet_keywords = (
        "diet",
        "food",
        "nutrition",
        "eat",
        "eating",
        "meal",
        "breakfast",
        "lunch",
        "dinner",
        "protein",
        "calorie",
    )


    if any(keyword in message for keyword in diet_keywords):
        return {"intent": "diet"}


    # Common workout terms also route to the workout node,
    # even if "workout" or "exercise" is not explicitly used.

    workout_keywords = (
        "workout",
        "exercise",
        "training",
        "train",
        "gym",
        "strength",
        "cardio",
        "warm-up",
        "warm up",
        "cool-down",
        "cool down",
        "stretching",
        "flexibility",
        "recovery",
        "muscle",
        "lifting",
        "weights",
        "squat",
        "deadlift",
        "push-up",
        "push up",
        "reps",
        "sets",
    )


    if any(keyword in message for keyword in workout_keywords):
        return {"intent": "workout"}


    if "bmi" in message:
        return {"intent": "bmi"}


    # --------------------------------------------------
    # SHORT FOLLOW-UP MESSAGES
    # --------------------------------------------------
    #
    # Example:
    #
    # User:
    # "Give me a chest workout"
    #
    # Assistant:
    # ...
    #
    # User:
    # "Make it easier"
    #
    # "Make it easier" does not contain "workout".
    # So we check the previous USER message.
    #

    previous_messages = state.get("messages", [])[:-1]


    # Check previous USER messages from newest to oldest.

    for previous_message in reversed(previous_messages):

        # Ignore assistant messages.
        if previous_message.type != "human":
            continue


        previous_text = str(
            previous_message.content
        ).lower()


        if any(
            keyword in previous_text
            for keyword in diet_keywords
        ):
            return {"intent": "diet"}


        if any(
            keyword in previous_text
            for keyword in workout_keywords
        ):
            return {"intent": "workout"}


        if "bmi" in previous_text:
            return {"intent": "bmi"}


    # If no previous topic can be identified,
    # use the general fitness node.

    return {"intent": "fitness"}


def route_intent(state):

    return state["intent"]


# --------------------------------------------------
# CONVERSATION EXAMPLE
# --------------------------------------------------

# "Give me a chest workout"
#         ↓
# workout
#
# "Make it easier"
#         ↓
# no keyword
#         ↓
# check messages
#         ↓
# previous USER message
#         ↓
# "Give me a chest workout"
#         ↓
# workout