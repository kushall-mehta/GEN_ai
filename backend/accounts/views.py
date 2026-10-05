from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import trainer_required , user_required

from .forms import RegisterForm
from .profile_utils import get_profile


# REGISTER

def register(request):

    if request.method == "POST":

        # We call our form class here
        form = RegisterForm(request.POST)

        if form.is_valid():

            # We temporarily create the User object without saving it yet.
            # We did it because we need to process the password first.
            user = form.save(commit=False)

            # It will hash the password before saving it.
            user.set_password(
                form.cleaned_data["password"]
            )

            user.save()

            # It creates an authenticated session
            # so the user doesn't have to log in again.
            login(request, user)

            return redirect("home")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


# LOGIN

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # Checks whether the username and password
        # match a Django User object.
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.role == "trainer":
                return redirect("trainer_dashboard")
            return redirect("user_dashboard")
        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Invalid username or password"}
            )

    return render(
        request,
        "accounts/login.html"
    )
# LOGOUT
def logout_view(request):

    logout(request)

    return redirect("home")


# HOME

def home(request):

    return render(
        request,
        "accounts/home.html"
    )

# PROTECTED PAGE


@login_required
def protected_page(request):

    return render(
        request,
        "accounts/protected.html"
    )

# USER ROLE CHECK

@user_required
def user_dashboard(request):
    profile = get_profile(request.user)

    return render(
        request,
        "accounts/user_dashboard.html",
        {"profile": profile}
    )

@trainer_required
def trainer_dashboard(request):

    return render(
        request,
        "accounts/trainer_dashboard.html"
    )
