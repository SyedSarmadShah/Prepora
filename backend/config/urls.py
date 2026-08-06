from django.contrib import admin
from django.urls import path
from apps.common.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health_check"),
    path("api/v1/health/", HealthCheckView.as_view(), name="health_check_v1"),
]
