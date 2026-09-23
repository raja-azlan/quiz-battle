from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Profile


class AccountsFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def register(self, username="alice", password="hunter22"):
        return self.client.post(
            "/api/register/", {"username": username, "password": password}, format="json"
        )

    def test_register_creates_user_and_profile(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="alice")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_rejects_duplicate_username(self):
        self.register()
        response = self.register(password="different1")
        self.assertEqual(response.status_code, 400)

    def test_login_returns_token_for_valid_credentials(self):
        self.register()
        response = self.client.post(
            "/api/login/", {"username": "alice", "password": "hunter22"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_rejects_wrong_password(self):
        self.register()
        response = self.client.post(
            "/api/login/", {"username": "alice", "password": "wrongpass"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_profile_returns_current_stats(self):
        user_id = self.register().json()["id"]
        response = self.client.get(f"/api/profile/{user_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["games_played"], 0)

    def test_update_stats_requires_internal_key(self):
        user_id = self.register().json()["id"]
        response = self.client.post(
            "/api/internal/update-stats/",
            {"user_id": user_id, "won": True},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_stats_records_a_win(self):
        user_id = self.register().json()["id"]
        response = self.client.post(
            "/api/internal/update-stats/",
            {"user_id": user_id, "won": True},
            format="json",
            HTTP_X_INTERNAL_KEY=settings.INTERNAL_API_KEY,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["wins"], 1)
        self.assertEqual(data["losses"], 0)
        self.assertEqual(data["games_played"], 1)
