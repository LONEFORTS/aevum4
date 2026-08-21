from rest_framework import serializers
from hub.models import Note, CodeSnippet, Task, Event, FocusSession

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note; fields = ("id","title","content","visibility","pinned","created_at","updated_at")

class CodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippet; fields = ("id","title","language","description","code","labels_csv","visibility","last_pushed_to","last_pushed_at","created_at","updated_at")

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task; fields = ("id","title","description","status","priority","due_date","order","created_at")

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event; fields = ("id","title","date","event_type","color","description")

class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession; fields = ("id","started_at","duration_min","completed","note")
