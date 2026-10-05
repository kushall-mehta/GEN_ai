from django import forms
from .models import User #out user


class RegisterForm(forms.ModelForm): #it's reg form from which user will enter the reg logic

    password = forms.CharField(
        widget=forms.PasswordInput#it hides the user password
    )

    class Meta: #for info This form is connected to the User model.
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]