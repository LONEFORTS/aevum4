from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    github_username = models.CharField(max_length=120, blank=True, default="")
    public_profile_enabled = models.BooleanField(default=False)
    public_bio = models.TextField(blank=True, default="")
    public_show_notes = models.BooleanField(default=False)
    public_show_snippets = models.BooleanField(default=False)
    github_token = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Profile({self.user.username})"

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, blank=True)
    def save(self, *a, **kw):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*a, **kw)
    def __str__(self): return self.name

VIS = [("private","Private"),("public","Public")]
class Note(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="notes")
    visibility = models.CharField(max_length=20, choices=VIS, default="private")
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-pinned","-updated_at"]
    def __str__(self): return self.title

class NoteFile(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="note_files/")
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class CodeSnippet(models.Model):
    LANGS = [("python","Python"),("javascript","JavaScript"),("cpp","C++"),("java","Java"),
             ("c","C"),("go","Go"),("rust","Rust"),("html","HTML"),("css","CSS"),
             ("sql","SQL"),("bash","Bash"),("text","Plain Text")]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snippets")
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=30, choices=LANGS, default="python")
    description = models.TextField(blank=True, default="")
    code = models.TextField()
    labels_csv = models.CharField(max_length=200, blank=True, default="")
    visibility = models.CharField(max_length=20, choices=VIS, default="private")
    slug = models.SlugField(max_length=80, blank=True)
    last_pushed_to = models.URLField(blank=True, default="")
    last_pushed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-updated_at"]
    def __str__(self): return self.title

class Task(models.Model):
    STATUS = [("todo","To Do"),("doing","In Progress"),("done","Done")]
    PRIORITY = [("low","Low"),("med","Medium"),("high","High")]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS, default="todo")
    priority = models.CharField(max_length=10, choices=PRIORITY, default="med")
    due_date = models.DateField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["order","-created_at"]
    def __str__(self): return self.title

class Event(models.Model):
    TYPES = [("exam","Exam"),("class","Class"),("assignment","Assignment"),("event","Event"),("reminder","Reminder")]
    COLORS = [("#6366f1","Indigo"),("#10b981","Emerald"),("#f59e0b","Amber"),("#ef4444","Red"),("#8b5cf6","Violet"),("#ec4899","Pink")]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    date = models.DateField()
    event_type = models.CharField(max_length=20, choices=TYPES, default="reminder")
    color = models.CharField(max_length=10, choices=COLORS, default="#6366f1")
    description = models.TextField(blank=True, default="")
    class Meta: ordering = ["date"]
    def __str__(self): return self.title

class FocusSession(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="focus_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    duration_min = models.PositiveIntegerField()
    completed = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True, default="")
    class Meta: ordering = ["-started_at"]

class Achievement(models.Model):
    BADGES = [("first_note","First Note","📝"),("first_snippet","First Snippet","💻"),
              ("first_task_done","First Task Done","✅"),("focus_5","Five Focus Sessions","🧠"),
              ("streak_3","3-Day Streak","🔥"),("note_10","Ten Notes","📚"),
              ("snippet_5","Five Snippets","🌟"),("early_adopter","Early Adopter","🚀")]
    BADGE_MAP = dict([(b[0], b) for b in BADGES])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=80)
    icon = models.CharField(max_length=8, default="🏆")
    earned_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ("user","code"); ordering = ["-earned_at"]

class SharedLink(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_links")
    token = models.CharField(max_length=32, unique=True)
    payload = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
