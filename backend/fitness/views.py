import re
import uuid

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

from .forms import FitnessProfileForm
from .models import FitnessProfile, WorkoutPlan


def _workout_title(content):
    for line in content.splitlines():
        title = re.sub(r"^#+\s*", "", line).strip(" \t*#")
        if title:
            return title[:150]
    return "AI-generated workout plan"


def _save_pending_workout(request):
    pending_workout = request.session.get("pending_workout")
    if not isinstance(pending_workout, dict):
        messages.error(request, "There is no workout waiting to be saved.")
        return redirect("fitness_chat")

    title = pending_workout.get("title")
    content = pending_workout.get("content")
    if not isinstance(title, str) or not isinstance(content, str):
        request.session.pop("pending_workout", None)
        messages.error(request, "The workout could not be saved. Please generate it again.")
        return redirect("fitness_chat")

    WorkoutPlan.objects.create(
        user=request.user,
        title=title,
        exercises=content,
        schedule="",
    )
    request.session.pop("pending_workout", None)
    messages.success(request, "Workout saved to your workout plans.")
    return redirect("workout_plans")


@login_required
def fitness_profile(request):

    try:
        profile = FitnessProfile.objects.get(
            user=request.user
        )

        return render(
            request,
            "fitness/view_profile.html",
            {"profile": profile}
        )

    except FitnessProfile.DoesNotExist:

        if request.method == "POST":
            form = FitnessProfileForm(request.POST)

            if form.is_valid():
                profile = form.save(commit=False) #create obj without saving it in db
                profile.user = request.user #the should automatically called like connects with the logged in user
                profile.save()

                return redirect("fitness_profile")

        else:
            form = FitnessProfileForm()

        return render(
            request,
            "fitness/create_profile.html",
            {"form": form}
        )
@login_required
def fitness_chat(request):
    try:
        profile = FitnessProfile.objects.get(
            user=request.user
        )
    except FitnessProfile.DoesNotExist:
        return redirect("fitness_profile")

    if request.method == "POST":
        workout_action = request.POST.get("workout_action")
        if workout_action == "save":
            return _save_pending_workout(request)
        if workout_action == "discard":
            request.session.pop("pending_workout", None)
            messages.info(request, "Workout was not saved.")
            return redirect("fitness_chat")

        message = request.POST.get("message", "").strip()
        pending_workout = request.session.get("pending_workout")
        if pending_workout and re.match(
            r"^(yes|yeah|yep|sure|okay|ok|please save)\b",
            message,
            flags=re.IGNORECASE,
        ):
            return _save_pending_workout(request)
        if pending_workout and re.match(
            r"^(no|nope|nah|not now)\b",
            message,
            flags=re.IGNORECASE,
        ):
            request.session.pop("pending_workout", None)
            messages.info(request, "Workout was not saved.")
            return redirect("fitness_chat")
        if pending_workout:
            request.session.pop("pending_workout", None)

        # Create a session ID for this user's conversation.
        session_id = request.session.get("fitness_session_id")

        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["fitness_session_id"] = session_id

        # Send user message + fitness profile to FastAPI
        response = requests.post(
            settings.AI_API_URL,

            json={
                "session_id": session_id,
                "message": message,
                "age": profile.age,
                "height": profile.height,
                "weight": profile.weight,
                "goal": profile.goal,
                "activity_level": profile.activity_level,
                "experience_level": profile.experience_level,
            }
        )

        data = response.json()
        answer = data.get("message")
        if data.get("intent") == "workout" and isinstance(answer, str):
            request.session["pending_workout"] = {
                "title": _workout_title(answer),
                "content": answer,
            }

        return render(
            request,
            "fitness/chat.html",
            {
                "profile": profile,
                "response": answer,
                "history": data.get("history", []),
                "pending_workout": request.session.get("pending_workout"),
            }
        )

    return render(
        request,
        "fitness/chat.html",
        {
            "profile": profile,
            "pending_workout": request.session.get("pending_workout"),
        }
    )
@login_required
def workout_plans(request):
    plans = WorkoutPlan.objects.filter(user=request.user)

    return render(
        request,
        "fitness/workout_plans.html",
        {"plans": plans}
    )