from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Role, UserRole

User = get_user_model()


class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("accounts:login")
        self.password = "ValidPassword123!"
        self.user = User.objects.create_user(
            email="sarmad@prepora.com",
            password=self.password,
            first_name="Sarmad",
            last_name="Shah",
        )

    def test_successful_login(self):
        """
        Verify that POSTing valid email and password returns HTTP 200 OK
        with access token, refresh token, and non-sensitive user metadata.
        """
        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token presence
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(len(response.data["access"]) > 0)
        self.assertTrue(len(response.data["refresh"]) > 0)

        # Check user structure
        self.assertIn("user", response.data)
        user_info = response.data["user"]
        self.assertEqual(user_info["id"], str(self.user.id))
        self.assertEqual(user_info["email"], "sarmad@prepora.com")
        self.assertEqual(user_info["first_name"], "Sarmad")
        self.assertEqual(user_info["last_name"], "Shah")
        self.assertEqual(user_info["is_verified"], False)
        self.assertIn("roles", user_info)
        self.assertIsInstance(user_info["roles"], list)

    def test_login_returns_assigned_roles(self):
        """
        Verify that login response user metadata includes assigned RBAC role codes.
        """
        role = Role.objects.create(name="Student", code="STUDENT")
        UserRole.objects.create(user=self.user, role=role)

        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("roles", response.data["user"])
        self.assertEqual(response.data["user"]["roles"], ["STUDENT"])

    def test_wrong_password_fails(self):
        """
        Verify that supplying an incorrect password returns HTTP 401 Unauthorized.
        """
        payload = {
            "email": "sarmad@prepora.com",
            "password": "WrongPassword123!",
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_unknown_email_fails(self):
        """
        Verify that supplying a non-existent email returns HTTP 401 Unauthorized.
        """
        payload = {
            "email": "nonexistent@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_inactive_user_fails(self):
        """
        Verify that an inactive user account is rejected with HTTP 401 Unauthorized.
        """
        self.user.is_active = False
        self.user.save()

        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_jwt_token_generation(self):
        """
        Verify that the generated JWT access token is valid and decodes to the correct user_id.
        """
        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token_str = response.data["access"]
        token = AccessToken(access_token_str)
        self.assertEqual(token["user_id"], str(self.user.id))

    def test_password_never_returned(self):
        """
        Verify that password is never exposed in the login response payload.
        """
        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password", response.data["user"])

    def test_last_login_updated(self):
        """
        Verify that user's last_login timestamp is updated upon successful login.
        """
        self.assertIsNone(self.user.last_login)

        payload = {
            "email": "sarmad@prepora.com",
            "password": self.password,
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)
