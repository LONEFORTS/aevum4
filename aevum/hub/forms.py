from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Note, CodeSnippet, Task, Event, Profile

TAG_WIDGET = forms.TextInput(attrs={"class":"form-control","placeholder":"comma,separated,tags"})

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class":"form-control"}))
    class Meta:
        model = User
        fields = ("username","email","password1","password2")
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        for f in self.fields.values():
            if not f.widget.attrs.get("class"):
                f.widget.attrs["class"] = "form-control"

class NoteForm(forms.ModelForm):
    tag_names = forms.CharField(required=False, widget=TAG_WIDGET)
    class Meta:
        model = Note
        fields = ("title","content","visibility","pinned")
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "content": forms.Textarea(attrs={"class":"form-control","rows":8}),
            "visibility": forms.Select(attrs={"class":"form-select"}),
        }

class CodeSnippetForm(forms.ModelForm):
    class Meta:
        model = CodeSnippet
        fields = ("title","language","description","code","labels_csv","visibility")
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "language": forms.Select(attrs={"class":"form-select"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "code": forms.Textarea(attrs={"class":"form-control","rows":14,"style":"font-family:monospace"}),
            "labels_csv": forms.TextInput(attrs={"class":"form-control","placeholder":"sorting,recursive,demo"}),
            "visibility": forms.Select(attrs={"class":"form-select"}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title","description","status","priority","due_date")
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "status": forms.Select(attrs={"class":"form-select"}),
            "priority": forms.Select(attrs={"class":"form-select"}),
            "due_date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title","date","event_type","color","description")
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "event_type": forms.Select(attrs={"class":"form-select"}),
            "color": forms.Select(attrs={"class":"form-select"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

class FocusForm(forms.Form):
    duration_min = forms.IntegerField(min_value=5, max_value=120, initial=25,
        widget=forms.NumberInput(attrs={"class":"form-control"}))

class ShareSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("public_profile_enabled","public_bio","public_show_notes","public_show_snippets","github_username","github_token")

class GithubRepoForm(forms.Form):
    repo_owner = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"username"}))
    repo_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"repo-name"}))
