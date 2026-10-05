from django.http.response import HttpResponseForbidden
from django.shortcuts import redirect

"""
these functions are used to check like only user can access or only trainer can access the code 

"""
def user_required(view_func):  #this is decorator function

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "user":
            return HttpResponseForbidden(
                "Access denied"
            )

        return view_func(request, *args, **kwargs)

    return wrapper

# TRAINER ROLE CHECK

def trainer_required(view_func):#this is decorator function

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "trainer":
            return HttpResponseForbidden(
                "Access denied"
            )

        return view_func(request, *args, **kwargs)

    return wrapper