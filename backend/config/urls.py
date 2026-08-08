from django.contrib import admin
from django.urls import include, path
from apps.common.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health_check"),
    path("api/v1/health/", HealthCheckView.as_view(), name="health_check_v1"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/users/", include("apps.accounts.user_urls")),
]
