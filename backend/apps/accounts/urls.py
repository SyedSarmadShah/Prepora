from django.urls import path

from apps.accounts.views import (
    UserLoginView,
    UserLogoutView,
    UserRegistrationView,
    UserTokenRefreshView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("refresh/", UserTokenRefreshView.as_view(), name="refresh"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
