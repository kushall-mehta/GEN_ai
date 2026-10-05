from django.db import models
from django.conf import settings

class TrainerProfile(models.Model):

    user = models.OneToOneField(#one haves only one trainer
        settings.AUTH_USER_MODEL,#we have created a user model and reg it to setting.py so we make one to one feild here w the trainer
        on_delete=models.CASCADE,
        related_name="trainer_profile"
    )

    specialization = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.user.username


#
# class FitnessProfile(models.Model): ##profile the user profile
#
#     user = models.OneToOneField( #a user haves only one profile
#         settings.AUTH_USER_MODEL, #Main user
#         on_delete=models.CASCADE,
#         related_name="fitness_profile"
#     )
#
#     age = models.PositiveIntegerField() #age should not be negative
#
#     height = models.FloatField()
#
#     weight = models.FloatField()
#
#     goal = models.CharField(
#         max_length=100
#     )
#
#     activity_level = models.CharField(
#         max_length=50
#     )
#
#     trainer = models.ForeignKey( #we assign  trainer to the user
#         TrainerProfile,
#         on_delete=models.SET_NULL,
#         null=True, #If Trainer A's profile is deleted, we don't want the users' fitness profiles to disappear.
#         blank=True,
#         related_name="clients"
#     )
#
#     def __str__(self):
#         return f"{self.user.username} - Fitness Profile"
#


class FitnessProfile(models.Model):
    """
    "muscle_gain" → stored in the database
    "Muscle Gain" → shown to the user
    """
    GOAL_CHOICES = (
        ("weight_loss", "Weight Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("fat_loss", "Fat Loss"),
        ("strength", "Strength"),
        ("general_fitness", "General Fitness"),
    )

    ACTIVITY_CHOICES = (
        ("sedentary", "Sedentary"),
        ("light", "Lightly Active"),
        ("moderate", "Moderately Active"),
        ("very_active", "Very Active"),
    )

    EXPERIENCE_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("elite", "Elite"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fitness_profile"
    )

    age = models.PositiveIntegerField()
    height = models.FloatField()
    weight = models.FloatField()

    goal = models.CharField(
        max_length=30,
        choices=GOAL_CHOICES
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients"
    )

    def __str__(self):
        return f"{self.user.username} - Fitness Profile"



class WorkoutPlan(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_plans"
    )

    trainer = models.ForeignKey(
        TrainerProfile, #we load trainer profile here
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workout_plans"
    )


    title = models.CharField(
        max_length=150
    )

    exercises = models.TextField()

    schedule = models.TextField(blank=True)

    trainer_notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"
