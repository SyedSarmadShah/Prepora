from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTestCase(APITestCase):
    def test_health_check_endpoint_returns_200_and_healthy_status(self):
        """
        Verify GET /api/health/ returns HTTP 200 OK and {"status": "healthy"}.
        """
        url = reverse("health_check")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_health_check_v1_endpoint_returns_200_and_healthy_status(self):
        """
        Verify GET /api/v1/health/ returns HTTP 200 OK and {"status": "healthy"}.
        """
        url = reverse("health_check_v1")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "healthy"})
