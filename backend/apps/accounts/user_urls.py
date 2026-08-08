from django.urls import path

from apps.accounts.views import UserProfileView

app_name = "users"

urlpatterns = [
    path("me/profile/", UserProfileView.as_view(), name="user_profile"),
]
