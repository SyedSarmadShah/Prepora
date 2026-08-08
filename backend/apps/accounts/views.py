from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.serializers import (
    UserLoginSerializer,
    UserLogoutSerializer,
    UserRegistrationSerializer,
)


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


class UserLoginView(generics.GenericAPIView):
    """
    API view for user authentication / login.
    Endpoint: POST /api/v1/auth/login/
    """

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserTokenRefreshView(TokenRefreshView):
    """
    API view for refreshing JWT access and refresh tokens.
    Endpoint: POST /api/v1/auth/refresh/
    """

    pass


class UserLogoutView(generics.GenericAPIView):
    """
    API view for user logout.
    Endpoint: POST /api/v1/auth/logout/
    Blacklists the provided refresh token and invalidates session.
    Requires authentication.
    """

    serializer_class = UserLogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
