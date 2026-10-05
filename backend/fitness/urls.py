from django.urls import path
from . import views


urlpatterns = [
    path("profile/", views.fitness_profile, name="fitness_profile"),
    path("workout-plans/", views.workout_plans, name="workout_plans"),
    path("chat/", views.fitness_chat, name="fitness_chat"),

]