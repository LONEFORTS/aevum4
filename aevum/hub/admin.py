from django.contrib import admin
from .models import (Note, NoteFile, CodeSnippet, Task, Event,
                     FocusSession, Achievement, Tag, Profile, SharedLink)
for m in [Note, NoteFile, CodeSnippet, Task, Event, FocusSession, Achievement, Tag, Profile, SharedLink]:
    admin.site.register(m)
