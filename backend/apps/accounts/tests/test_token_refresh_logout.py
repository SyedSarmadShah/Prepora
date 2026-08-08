from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TokenRefreshAndLogoutTests(APITestCase):
    def setUp(self):
        self.refresh_url = reverse("accounts:refresh")
        self.logout_url = reverse("accounts:logout")
        self.user = User.objects.create_user(
            email="session_user@prepora.com",
            password="SecurePassword123!",
            first_name="Session",
            last_name="User",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_str = str(self.refresh)
        self.access_str = str(self.refresh.access_token)

    def test_successful_refresh(self):
        """
        Verify that POSTing a valid refresh token yields HTTP 200 OK
        with new access and rotated refresh tokens.
        """
        payload = {"refresh": self.refresh_str}
        response = self.client.post(self.refresh_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotEqual(response.data["access"], self.access_str)
        self.assertNotEqual(response.data["refresh"], self.refresh_str)

    def test_invalid_refresh_token(self):
        """
        Verify that POSTing an invalid refresh token string returns HTTP 401 Unauthorized.
        """
        payload = {"refresh": "invalid_refresh_token_string"}
        response = self.client.post(self.refresh_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_refresh_token(self):
        """
        Verify that an expired refresh token is rejected with HTTP 401 Unauthorized.
        """
        expired_token = RefreshToken.for_user(self.user)
        # Manually set exp in payload to past timestamp
        expired_token.payload["exp"] = int((timezone.now() - timedelta(days=1)).timestamp())
        expired_str = str(expired_token)

        payload = {"refresh": expired_str}
        response = self.client.post(self.refresh_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_authentication(self):
        """
        Verify that calling the logout endpoint without Bearer authentication returns HTTP 401 Unauthorized.
        """
        payload = {"refresh": self.refresh_str}
        response = self.client.post(self.logout_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_logout(self):
        """
        Verify that an authenticated user can logout by blacklisting their refresh token (HTTP 204 No Content).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_str}")
        payload = {"refresh": self.refresh_str}
        response = self.client.post(self.logout_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_blacklisted_token_cannot_be_reused(self):
        """
        Verify that once a refresh token is blacklisted during logout,
        it cannot be used to request a new access token (HTTP 401 Unauthorized).
        """
        # Step 1: Perform logout to blacklist token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_str}")
        logout_payload = {"refresh": self.refresh_str}
        logout_res = self.client.post(self.logout_url, logout_payload, format="json")
        self.assertEqual(logout_res.status_code, status.HTTP_204_NO_CONTENT)

        # Step 2: Attempt to refresh using the blacklisted token
        self.client.credentials()  # Clear auth headers
        refresh_payload = {"refresh": self.refresh_str}
        refresh_res = self.client.post(self.refresh_url, refresh_payload, format="json")
        self.assertEqual(refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)
