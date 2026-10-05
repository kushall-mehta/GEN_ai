from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import FitnessProfile, WorkoutPlan


class WorkoutSaveFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="workout-user",
            password="test-password",
        )
        FitnessProfile.objects.create(
            user=self.user,
            age=30,
            height=175,
            weight=75,
            goal="general_fitness",
            activity_level="moderate",
            experience_level="beginner",
        )
        self.client.force_login(self.user)

    @override_settings(AI_API_URL="http://ai-api:8081/chat")
    @patch("fitness.views.requests.post")
    def test_generated_workout_can_be_saved_by_replying_yes(self, post_request):
        workout = "## Beginner strength workout\n\nSquats: 3 sets of 8 reps."
        post_request.return_value.json.return_value = {
            "message": workout,
            "intent": "workout",
            "history": [
                {"role": "user", "content": "Build me a workout plan."},
                {"role": "assistant", "content": workout},
            ],
        }

        response = self.client.post(
            reverse("fitness_chat"),
            {"message": "Build me a workout plan."},
        )

        self.assertEqual(post_request.call_args.args[0], "http://ai-api:8081/chat")
        self.assertContains(response, "Would you like to save this workout")
        self.assertIn("pending_workout", self.client.session)

        response = self.client.post(
            reverse("fitness_chat"),
            {"message": "Yes, please"},
        )

        self.assertRedirects(response, reverse("workout_plans"))
        plan = WorkoutPlan.objects.get(user=self.user)
        self.assertEqual(plan.title, "Beginner strength workout")
        self.assertEqual(plan.exercises, workout)
        self.assertEqual(plan.schedule, "")
        self.assertNotIn("pending_workout", self.client.session)

        response = self.client.get(reverse("workout_plans"))
        self.assertContains(response, "Beginner strength workout")
        self.assertContains(response, "Squats: 3 sets of 8 reps.")

    @patch("fitness.views.requests.post")
    def test_declining_does_not_save_the_workout(self, post_request):
        workout = "## Full-body workout\n\nBodyweight squats."
        post_request.return_value.json.return_value = {
            "message": workout,
            "intent": "workout",
            "history": [
                {"role": "user", "content": "Give me a workout"},
                {"role": "assistant", "content": workout},
            ],
        }

        self.client.post(
            reverse("fitness_chat"),
            {"message": "Give me a workout"},
        )
        response = self.client.post(
            reverse("fitness_chat"),
            {"message": "No, thanks"},
        )

        self.assertRedirects(response, reverse("fitness_chat"))
        self.assertFalse(WorkoutPlan.objects.filter(user=self.user).exists())
        self.assertNotIn("pending_workout", self.client.session)
