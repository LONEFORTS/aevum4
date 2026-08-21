from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter()
router.register("notes",    views.NoteViewSet,      basename="note")
router.register("snippets", views.CodeSnippetViewSet,basename="snippet")
router.register("tasks",    views.TaskViewSet,      basename="task")
router.register("events",   views.EventViewSet,     basename="event")
router.register("focus",    views.FocusViewSet,     basename="focus")
urlpatterns = [
    path("", include(router.urls)),
    path("stats/", views.stats, name="api-stats"),
]
