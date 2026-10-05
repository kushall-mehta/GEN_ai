from django import forms
from .models import FitnessProfile


class FitnessProfileForm(forms.ModelForm):
    class Meta:
        model = FitnessProfile
        fields = [
            "age",
            "height",
            "weight",
            "goal",
            "activity_level",
            "experience_level",
            'trainer'
        ]