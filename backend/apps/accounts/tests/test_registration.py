from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserProfile

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("accounts:register")
        self.valid_payload = {
            "email": "student@prepora.com",
            "password": "SecurePassword123!",
            "first_name": "Sarmad",
            "last_name": "Shah",
        }

    def test_successful_registration(self):
        """
        Verify that POSTing valid payload returns 201 Created, creates User and UserProfile,
        hashes password, and does NOT expose password in output.
        """
        response = self.client.post(self.register_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check response structure
        self.assertEqual(response.data["email"], "student@prepora.com")
        self.assertEqual(response.data["first_name"], "Sarmad")
        self.assertEqual(response.data["last_name"], "Shah")
        self.assertNotIn("password", response.data)

        # Verify database record creation
        user = User.objects.filter(email="student@prepora.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Sarmad")
        self.assertEqual(user.last_name, "Shah")

        # Verify password hashing
        self.assertTrue(user.check_password("SecurePassword123!"))
        self.assertNotEqual(user.password, "SecurePassword123!")

        # Verify automatic UserProfile creation
        profile = UserProfile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)

    def test_registration_duplicate_email_fails(self):
        """
        Verify that registering with an already existing email returns 400 Bad Request.
        """
        User.objects.create_user(
            email="student@prepora.com",
            password="InitialPassword123!",
        )

        response = self.client.post(self.register_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = [detail["field"] for detail in response.data["error"]["details"]]
        self.assertIn("email", error_fields)

    def test_registration_weak_password_fails(self):
        """
        Verify that Django password validation rejects overly simple passwords with 400 Bad Request.
        """
        payload = {
            "email": "weakpass@prepora.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = [detail["field"] for detail in response.data["error"]["details"]]
        self.assertIn("password", error_fields)

    def test_registration_missing_email_fails(self):
        """
        Verify that missing required email field returns 400 Bad Request.
        """
        payload = {
            "password": "SecurePassword123!",
            "first_name": "NoEmail",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = [detail["field"] for detail in response.data["error"]["details"]]
        self.assertIn("email", error_fields)

    def test_registration_endpoint_paths(self):
        """
        Verify /api/v1/auth/register/ endpoint works.
        """
        response = self.client.post("/api/v1/auth/register/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "student@prepora.com")
