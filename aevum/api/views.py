from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Sum
from hub.models import Note, CodeSnippet, Task, Event, FocusSession
from .serializers import (NoteSerializer, CodeSnippetSerializer,
                          TaskSerializer, EventSerializer, FocusSessionSerializer)

class OwnerScopedViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user) if self.request.user.is_authenticated else self.queryset.none()

class NoteViewSet(OwnerScopedViewSet):
    queryset = Note.objects.all(); serializer_class = NoteSerializer

class CodeSnippetViewSet(OwnerScopedViewSet):
    queryset = CodeSnippet.objects.all(); serializer_class = CodeSnippetSerializer

class TaskViewSet(OwnerScopedViewSet):
    queryset = Task.objects.all(); serializer_class = TaskSerializer

class EventViewSet(OwnerScopedViewSet):
    queryset = Event.objects.all(); serializer_class = EventSerializer

class FocusViewSet(OwnerScopedViewSet):
    queryset = FocusSession.objects.all(); serializer_class = FocusSessionSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def stats(request):
    if not request.user.is_authenticated:
        return Response({"auth_required": True})
    owner = request.user
    return Response({
        "notes":     owner.notes.count(),
        "snippets":  owner.snippets.count(),
        "tasks":     owner.tasks.count(),
        "tasks_done":owner.tasks.filter(status="done").count(),
        "events":    owner.events.count(),
        "focus_min": int(owner.focus_sessions.aggregate(t=Sum("duration_min"))["t"] or 0),
        "achievements": owner.achievements.count(),
    })
