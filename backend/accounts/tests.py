from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from fitness.models import FitnessProfile


class UserDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="fitness-user",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_dashboard_shows_locked_coach_without_profile(self):
        response = self.client.get(reverse("user_dashboard"))

        self.assertContains(response, "Complete it to unlock your coach")
        self.assertContains(response, "tile-locked")
        self.assertNotContains(response, "Open chat")

    def test_completed_profile_marks_all_steps_done_and_unlocks_coach(self):
        FitnessProfile.objects.create(
            user=self.user,
            age=30,
            height=170,
            weight=70,
            goal="general_fitness",
            activity_level="moderate",
            experience_level="beginner",
        )

        response = self.client.get(reverse("user_dashboard"))

        self.assertContains(response, '<li class="step done"><b>Account</b>', html=False)
        self.assertContains(response, '<li class="step done"><b>Fitness profile</b>', html=False)
        self.assertContains(response, '<li class="step done"><b>Fitness coach</b>', html=False)
        self.assertNotContains(response, "tile-locked")
        self.assertNotContains(response, "Locked until your fitness profile is complete.")
        self.assertContains(response, "Open chat")
