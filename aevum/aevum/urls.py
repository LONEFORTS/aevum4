from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hub import views as hub_views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", hub_views.register, name="register"),
    path("", hub_views.landing, name="landing"),
    path("dashboard/", hub_views.dashboard, name="dashboard"),
    path("", include("hub.urls")),
    path("api/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
