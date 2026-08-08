from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile

User = get_user_model()


class UserProfileTests(APITestCase):
    def setUp(self):
        self.profile_url = reverse("users:user_profile")
        self.user = User.objects.create_user(
            email="sarmad_profile@prepora.com",
            password="SecurePassword123!",
            first_name="Sarmad",
            last_name="Shah",
        )
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.profile.target_exam = "PMA Long Course"
        self.profile.phone_number = "+923001234567"
        self.profile.save()

        self.other_user = User.objects.create_user(
            email="other_user@prepora.com",
            password="SecurePassword123!",
            first_name="Other",
            last_name="User",
        )
        self.other_profile, _ = UserProfile.objects.get_or_create(user=self.other_user)
        self.other_profile.target_exam = "PAF GDP Course"
        self.other_profile.phone_number = "+923009876543"
        self.other_profile.save()

        self.token = RefreshToken.for_user(self.user).access_token
        self.auth_header = f"Bearer {self.token}"

    def test_authenticated_user_can_retrieve_profile(self):
        """
        1. Authenticated user can retrieve their profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "sarmad_profile@prepora.com")

    def test_unauthenticated_user_receives_401(self):
        """
        2. Unauthenticated user receives HTTP 401.
        """
        response_get = self.client.get(self.profile_url)
        self.assertEqual(response_get.status_code, status.HTTP_401_UNAUTHORIZED)

        response_patch = self.client.patch(self.profile_url, {"first_name": "NewName"})
        self.assertEqual(response_patch.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_update_profile(self):
        """
        3. Authenticated user can update their own profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        payload = {
            "first_name": "SarmadUpdated",
            "last_name": "ShahUpdated",
            "target_exam": "ISSB Initial Test",
            "phone_number": "+923111111111",
        }
        response = self.client.patch(self.profile_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "SarmadUpdated")
        self.assertEqual(self.user.last_name, "ShahUpdated")
        self.assertEqual(self.profile.target_exam, "ISSB Initial Test")
        self.assertEqual(self.profile.phone_number, "+923111111111")

    def test_patch_supports_partial_updates(self):
        """
        4. PATCH supports partial updates.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        payload = {"target_exam": "PAF Aeronautical Engineering"}
        response = self.client.patch(self.profile_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.profile.target_exam, "PAF Aeronautical Engineering")
        # Ensure unspecified fields were not wiped out
        self.assertEqual(self.user.first_name, "Sarmad")
        self.assertEqual(self.profile.phone_number, "+923001234567")

    def test_user_information_returned_correctly(self):
        """
        5. User information is returned correctly.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["email"], "sarmad_profile@prepora.com")
        self.assertEqual(response.data["first_name"], "Sarmad")
        self.assertEqual(response.data["last_name"], "Shah")
        self.assertEqual(response.data["is_verified"], False)

    def test_user_profile_information_returned_correctly(self):
        """
        6. UserProfile information is returned correctly.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["target_exam"], "PMA Long Course")
        self.assertEqual(response.data["phone_number"], "+923001234567")
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_password_never_returned(self):
        """
        7. Password is never returned in GET or PATCH responses.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response_get = self.client.get(self.profile_url)
        self.assertNotIn("password", response_get.data)

        response_patch = self.client.patch(self.profile_url, {"first_name": "NewName"})
        self.assertNotIn("password", response_patch.data)

    def test_user_cannot_modify_protected_fields(self):
        """
        8. User cannot modify protected fields (email, id, is_staff, is_superuser, is_active).
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        payload = {
            "email": "hacked_email@prepora.com",
            "id": "00000000-0000-0000-0000-000000000000",
            "is_staff": True,
            "is_superuser": True,
            "is_active": False,
            "first_name": "ValidNameChange",
        }
        response = self.client.patch(self.profile_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "sarmad_profile@prepora.com")
        self.assertNotEqual(str(self.user.id), "00000000-0000-0000-0000-000000000000")
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.first_name, "ValidNameChange")

    def test_profile_endpoint_does_not_accept_another_user_id(self):
        """
        9. Profile endpoint does not accept another user's ID to fetch/modify another user's profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)

        # Attempt to pass other_user's ID in query parameter or payload
        url_with_param = f"{self.profile_url}?user_id={self.other_user.id}"
        response_get = self.client.get(url_with_param)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        # Must STILL return authenticated user's email, NOT other_user's email
        self.assertEqual(response_get.data["email"], "sarmad_profile@prepora.com")

        payload = {
            "user_id": str(self.other_user.id),
            "first_name": "AttemptHackedName",
        }
        response_patch = self.client.patch(self.profile_url, payload, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)

        # Ensure other_user profile was untouched
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.first_name, "Other")

    def test_invalid_profile_data_returns_400(self):
        """
        10. Invalid profile data (e.g. phone_number exceeding 20 chars) returns HTTP 400.
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        payload = {
            "phone_number": "1" * 25,  # Exceeds max_length=20
        }
        response = self.client.patch(self.profile_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = [detail["field"] for detail in response.data["error"]["details"]]
        self.assertIn("phone_number", error_fields)
