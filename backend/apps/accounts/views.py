from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.accounts.serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    Endpoint: POST /api/v1/auth/register/
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
