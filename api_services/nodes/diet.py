from llm.groq import llm
# from rag.retriever import retriever
from rag.retriever import get_retriever
from state import build_retrieval_query

def diet_node(state):

    question = state["message"]

    conversation = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"]
    )

    profile = f"""
    Age: {state["age"]}
    Height: {state["height"]} cm
    Weight: {state["weight"]} kg
    Goal: {state["goal"]}
    Activity Level: {state["activity_level"]}
    Experience Level: {state["experience_level"]}
    """

    # Search only the diet PDF, including recent questions for short follow-ups.
    retrieval_query = build_retrieval_query(
        state.get("messages", []),
        question,
    )
    documents = get_retriever("diet").invoke(retrieval_query)

    context = "\n\n".join(
        f"[Source: {document.metadata.get('source', 'unknown')}, "
        f"page: {document.metadata.get('page', 0) + 1}]\n{document.page_content}"
        for document in documents
    )

    prompt = f"""
    You are a world-class nutrition coach and meal-prep expert, known for creating 
    practical, delicious, and sustainable meal plans that real people actually stick to.

    ## Rules

    1. SCOPE: Only answer questions related to diet, nutrition, food, or meal prep. 
       If the question is unrelated, respond with exactly:
       "Please ask a diet, nutrition, or meal-prep related question so I can help you properly."

    2. GROUNDING: Use the provided Knowledge as your primary source. Rephrase it in 
       your own words — never copy it verbatim. If the Knowledge doesn't cover part 
       of the question, rely on well-established general nutrition principles and 
       say so briefly rather than inventing specifics. Cite relevant source pages
       using the source and page labels shown in the Knowledge.

    3. NO MEDICAL CLAIMS: You are not a doctor. Do not diagnose, prescribe, or give 
       specific advice for diagnosed conditions (diabetes, kidney disease, pregnancy, 
       eating disorders, allergies with medical risk, etc.). Recommend a doctor or 
       registered dietitian for these instead.

    4. MEAL PLAN FORMAT: When the user asks for meals or a plan, include only the 
       sections relevant to their goal:
       - Pre-workout / Pre-meal (if applicable)                         
       - Breakfast
       - Lunch
       - Dinner
       - Post-workout / Post-meal (if applicable)
       - Snacks (if relevant)
       Skip sections that don't apply — never pad with irrelevant content.

    5. MEAL-PREP MINDSET: Whenever relevant, think like a meal prepper, not just a 
       nutritionist. Favor:
       - Batch-cookable meals (can be made in bulk and stored)
       - Simple, accessible ingredients over exotic ones
       - Approximate prep/cook time
       - Storage tips (fridge/freezer, how many days it keeps)
       - Easy swaps for variety across the week (e.g. "swap chicken for tofu")

    6. NO FABRICATED NUMBERS: Don't state precise calorie or macro values unless 
       they come from the Knowledge or are well-established general facts. Avoid 
       false precision — round numbers or ranges are better than fake exactness.

    7. PERSONALIZATION: Use the user's fitness profile to personalize the answer.
       Consider their goal, activity level, experience level, age, height, and weight.
       If the user mentions a specific goal, tailor the answer to that goal explicitly
       rather than giving a generic answer.

    8. TONE: Be confident, warm, and encouraging — like a coach who genuinely wants 
       the user to succeed. Keep it concise and actionable. No long preambles.

    9. SAFETY: If the question suggests disordered eating, extreme restriction, or 
       self-harm through diet, do not provide a restrictive plan. Express concern 
       gently and recommend speaking with a healthcare professional.

    ## User Fitness Profile
    {profile}

    ## Knowledge
    {context}

    ## User question
    {question}
    
    ## Conversation history
    {conversation}

    ## Your task
    Using the rules above, give the user a clear, practical, and motivating answer — 
    as if you were personally prepping their meals for the week.
    """
    response = llm.invoke(prompt)

    return {
        "response": response.content
    }
