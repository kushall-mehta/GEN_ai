from django.urls import path
from .views import *


urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("protected/",protected_page,name="protected"),
    path("user-dashboard/", user_dashboard, name="user_dashboard"),
    path("trainer-dashboard/", trainer_dashboard, name="trainer_dashboard"),
    #path("profile/", views.fitness_profile, name="fitness_profile"),
]