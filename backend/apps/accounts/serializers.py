from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration.
    Validates email uniqueness, applies Django password validation rules,
    hashes the password, and automatically creates a UserProfile.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name")
        extra_kwargs = {
            "email": {
                "required": True,
            },
            "first_name": {
                "required": False,
                "allow_blank": True,
            },
            "last_name": {
                "required": False,
                "allow_blank": True,
            },
        }

    def validate_password(self, value):
        """
        Validate password using Django's built-in password validation suite.
        """
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        """
        Create a new user with hashed password and ensure UserProfile is created.
        """
        email = validated_data.get("email")
        password = validated_data.get("password")
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        UserProfile.objects.get_or_create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login and JWT token issuance.
    Authenticates user via email and password, updates last login,
    and returns access/refresh JWT tokens alongside safe user fields.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")

        if not email or not password:
            raise AuthenticationFailed("Invalid credentials.")

        user = authenticate(request=request, email=email, password=password)

        if user is None or not user.is_active:
            raise AuthenticationFailed("Invalid credentials.")

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_verified": user.is_verified,
            },
        }


class UserLogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out users by blacklisting their refresh token.
    """

    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        self.refresh_token = attrs.get("refresh")
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken):
            raise AuthenticationFailed("Token is invalid or expired.")
