from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from fitness.models import FitnessProfile


def get_profile(user):
    """Return the user's fitness profile, or None if they have not created one yet."""
    try:
        return user.fitness_profile
    except FitnessProfile.DoesNotExist:
        return None


def profile_required(view):
    """Allow access only when the user has completed their fitness profile."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if get_profile(request.user) is None:
            messages.info(
                request,
                "Complete your fitness profile to unlock your coach."
            )
            return redirect("fitness_profile")

        return view(request, *args, **kwargs)

    return wrapper