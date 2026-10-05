from django.contrib import admin
from .models import FitnessProfile , WorkoutPlan , TrainerProfile


admin.site.register(TrainerProfile)
admin.site.register(FitnessProfile)
admin.site.register(WorkoutPlan)
