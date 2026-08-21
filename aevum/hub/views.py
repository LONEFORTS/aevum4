"""Aevum — all views. Mobile-first, premium dark UI."""
import os, secrets, datetime as dt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import (Note, NoteFile, CodeSnippet, Task, Event, FocusSession,
                     Achievement, Tag, Profile, SharedLink)
from .forms import (RegisterForm, NoteForm, CodeSnippetForm, TaskForm,
                    EventForm, FocusForm, ShareSettingsForm, GithubRepoForm)
from .github_api import push_snippet

# ---------- AEVUM ACHIEVEMENT ENGINE ----------
ACHIEVEMENT_RULES = [
    ("first_note",        "First Note",       "📝", lambda u: u.notes.count()   >= 1),
    ("first_snippet",     "First Snippet",    "💻", lambda u: u.snippets.count()>= 1),
    ("first_task_done",   "First Task Done",  "✅", lambda u: u.tasks.filter(status="done").count() >= 1),
    ("focus_5",           "Five Focus Sessions", "🧠", lambda u: u.focus_sessions.count() >= 5),
    ("streak_3",          "3-Day Streak",     "🔥", lambda _u: True),  # computed below
    ("note_10",           "Ten Notes",        "📚", lambda u: u.notes.count()   >= 10),
    ("snippet_5",         "Five Snippets",    "🌟", lambda u: u.snippets.count()>= 5),
    ("early_adopter",     "Early Adopter",    "🚀", lambda _u: True),
]

def award_achievements(user):
    for code, title, icon, rule in ACHIEVEMENT_RULES:
        try:
            if code == "streak_3":
                # consecutive 3-day activity streak
                days = set([fs.started_at.date() for fs in user.focus_sessions.all()]) \
                     | set([n.created_at.date()    for n in user.notes.all()]) \
                     | set([s.created_at.date()    for s in user.snippets.all()])
                if not (max(days) - dt.timedelta(days=2) in days and max(days) - dt.timedelta(days=1) in days):
                    continue
            if code == "early_adopter":
                pass
            elif not rule(user):
                continue
            Achievement.objects.get_or_create(user=user, code=code, defaults={"title": title, "icon": icon})
        except Exception:
            pass

def get_or_make_profile(user):
    p, _ = Profile.objects.get_or_create(user=user)
    return p

# ---------- auth ----------
def register(request):
    if request.method == "POST":
        f = RegisterForm(request.POST)
        if f.is_valid():
            u = f.save()
            get_or_make_profile(u)
            login(request, u)
            Achievement.objects.get_or_create(user=u, code="early_adopter", defaults={"title":"Early Adopter","icon":"🚀"})
            return redirect("dashboard")
    else:
        f = RegisterForm()
    return render(request, "registration/register.html", {"form": f})

def custom_login(request):
    if request.method == "POST":
        u = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if u:
            login(request, u); return redirect("dashboard")
        return render(request, "registration/login.html", {"error":"Invalid credentials"})
    return render(request, "registration/login.html")

# ---------- landing / dashboard ----------
def landing(request):
    if request.user.is_authenticated: return redirect("dashboard")
    return render(request, "landing.html")

@login_required
def dashboard(request):
    user = request.user
    notes = user.notes.all()
    snippets = user.snippets.all()
    tasks = user.tasks.all()
    events = user.events.all()
    focus_today = user.focus_sessions.filter(started_at__date=timezone.now().date())
    total_focus_min = sum((s.duration_min or 0) for s in user.focus_sessions.all())
    # Heatmap: 49 days (7 weeks), aggregated
    heatmap = {}
    today = timezone.now().date()
    for i in range(49):
        d = today - dt.timedelta(days=48-i)
        heatmap[d.isoformat()] = (
            notes.filter(created_at__date=d).count() * 2 +
            snippets.filter(created_at__date=d).count() * 3 +
            user.focus_sessions.filter(started_at__date=d).count()
        )
    achievements = user.achievements.all()[:8]
    upcoming_events = events.filter(date__gte=today).order_by("date")[:5]
    ctx = {
        "notes_count": notes.count(),
        "snippets_count": snippets.count(),
        "tasks_count": tasks.count(),
        "events_count": events.count(),
        "focus_today": focus_today.count(),
        "total_focus_min": total_focus_min,
        "tasks_done": tasks.filter(status="done").count(),
        "now": timezone.now(),
        "heatmap": heatmap,
        "achievements": achievements,
        "upcoming_events": upcoming_events,
    }
    return render(request, "dashboard.html", ctx)

# ---------- notes ----------
@login_required
def notes_list(request):
    q = request.GET.get("q","")
    qs = request.user.notes.all()
    if q: qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(tags__name__icontains=q)).distinct()
    return render(request, "notes/list.html", {"notes": qs.order_by("-pinned","-updated_at"), "q": q})

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    return render(request, "notes/detail.html", {"note": note})

@login_required
def note_create(request):
    if request.method == "POST":
        f = NoteForm(request.POST)
        if f.is_valid():
            n = f.save(commit=False); n.owner = request.user; n.save()
            for t in (request.POST.get("tag_names","") or "").split(","):
                t = t.strip()
                if t:
                    obj, _ = Tag.objects.get_or_create(name=t); n.tags.add(obj)
            for fi in request.FILES.getlist("files"):
                NoteFile.objects.create(note=n, file=fi, original_name=fi.name)
            award_achievements(request.user)
            messages.success(request, "Note created.")
            return redirect("notes_list")
    else:
        f = NoteForm()
    return render(request, "notes/form.html", {"form": f, "mode": "create"})

@login_required
def note_edit(request, pk):
    n = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == "POST":
        f = NoteForm(request.POST, instance=n)
        if f.is_valid():
            f.save(); messages.success(request, "Note updated."); return redirect("notes_list")
    else:
        f = NoteForm(instance=n)
    return render(request, "notes/form.html", {"form": f, "mode": "edit", "note": n})

@login_required
def note_delete(request, pk):
    n = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == "POST":
        n.delete(); messages.success(request, "Note deleted."); return redirect("notes_list")
    return render(request, "confirm_delete.html", {"obj": n, "back": "notes_list", "label": "Note"})

# ---------- code snippets ----------
@login_required
def snippets_list(request):
    q = request.GET.get("q","")
    lang = request.GET.get("lang","")
    qs = request.user.snippets.all()
    if q:   qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(code__icontains=q))
    if lang:qs = qs.filter(language=lang)
    return render(request, "snippets/list.html", {"snippets": qs, "q": q, "lang": lang, "languages": CodeSnippet.LANGS})

@login_required
def snippet_detail(request, pk):
    s = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    award_achievements(request.user)
    return render(request, "snippets/detail.html", {"snippet": s, "languages": CodeSnippet.LANGS})

@login_required
def snippet_create(request):
    if request.method == "POST":
        f = CodeSnippetForm(request.POST)
        if f.is_valid():
            s = f.save(commit=False); s.owner = request.user
            slug = s.title.lower().replace(" ","-")[:50] or "snippet"
            base = slug; i = 2
            while CodeSnippet.objects.filter(owner=request.user, title__startswith=slug).exists():
                slug = f"{base}-{i}"; i += 1
            s.slug = slug  # type: ignore
            s.save()
            award_achievements(request.user)
            messages.success(request, "Snippet saved.")
            return redirect("snippet_detail", pk=s.pk)
    else:
        f = CodeSnippetForm()
    return render(request, "snippets/form.html", {"form": f, "mode": "create", "languages": CodeSnippet.LANGS})

@login_required
def snippet_edit(request, pk):
    s = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    if request.method == "POST":
        f = CodeSnippetForm(request.POST, instance=s)
        if f.is_valid():
            f.save(); messages.success(request, "Snippet updated."); return redirect("snippet_detail", pk=s.pk)
    else:
        f = CodeSnippetForm(instance=s)
    return render(request, "snippets/form.html", {"form": f, "mode": "edit", "snippet": s, "languages": CodeSnippet.LANGS})

@login_required
def snippet_delete(request, pk):
    s = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    if request.method == "POST":
        s.delete(); messages.success(request, "Snippet deleted."); return redirect("snippets_list")
    return render(request, "confirm_delete.html", {"obj": s, "back": "snippets_list", "label": "Snippet"})

@login_required
def snippet_publish(request, pk):
    s = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    if request.method == "POST":
        f = GithubRepoForm(request.POST)
        if f.is_valid():
            res = push_snippet(s, f.cleaned_data["repo_owner"], f.cleaned_data["repo_name"])
            if res.get("ok"):
                s.last_pushed_to = res["url"]; s.last_pushed_at = timezone.now(); s.save()
                messages.success(request, f"Pushed to GitHub: {res['url']}")
            else:
                messages.error(request, f"Push failed: {res.get('error')} — {res.get('hint','')}")
        return redirect("snippet_detail", pk=s.pk)
    return render(request, "snippets/publish.html", {"snippet": s, "form": GithubRepoForm()})

# ---------- tasks (kanban) ----------
@login_required
def tasks_board(request):
    user = request.user
    todo   = user.tasks.filter(status="todo").order_by("order","-created_at")
    doing  = user.tasks.filter(status="doing").order_by("order","-created_at")
    done   = user.tasks.filter(status="done").order_by("order","-created_at")
    return render(request, "tasks/board.html", {"todo": todo, "doing": doing, "done": done})

@login_required
def task_move(request, pk, new_status):
    t = get_object_or_404(Task, pk=pk, owner=request.user)
    if new_status in dict(Task.STATUS): t.status = new_status
    t.save()
    award_achievements(request.user)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest": return JsonResponse({"ok":True})
    return redirect("tasks_board")

@login_required
def task_create(request):
    if request.method == "POST":
        f = TaskForm(request.POST)
        if f.is_valid():
            t = f.save(commit=False); t.owner = request.user; t.save()
            messages.success(request, "Task added."); return redirect("tasks_board")
    else:
        f = TaskForm()
    return render(request, "tasks/form.html", {"form": f})

@login_required
def task_edit(request, pk):
    t = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == "POST":
        f = TaskForm(request.POST, instance=t)
        if f.is_valid():
            f.save(); messages.success(request, "Task updated."); return redirect("tasks_board")
    else:
        f = TaskForm(instance=t)
    return render(request, "tasks/form.html", {"form": f, "task": t})

@login_required
def task_delete(request, pk):
    t = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == "POST":
        t.delete(); messages.success(request, "Task deleted."); return redirect("tasks_board")
    return render(request, "confirm_delete.html", {"obj": t, "back": "tasks_board", "label": "Task"})

# ---------- events ----------
@login_required
def events_calendar(request):
    month = request.GET.get("month")
    today = timezone.now().date()
    if month:
        try: y, m = month.split("-"); today = dt.date(int(y), int(m), 1)
        except Exception: pass
    first = today.replace(day=1)
    next_month = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    days_in_month = (next_month - first).days
    cells = []
    lead = first.weekday()  # Mon=0
    for _ in range(lead): cells.append(None)
    cursor = first
    while cursor < next_month:
        cells.append(cursor); cursor += dt.timedelta(days=1)
    month_events = {d:[] for d in cells if d}
    for e in request.user.events.filter(date__gte=first, date__lt=next_month):
        if e.date in month_events: month_events[e.date].append(e)
    return render(request, "events/calendar.html", {"month_label": first.strftime("%B %Y"), "cells": cells, "month_events": month_events, "prev": (first - dt.timedelta(days=1)).replace(day=1).strftime("%Y-%m"), "next": next_month.strftime("%Y-%m")})

@login_required
def event_create(request):
    if request.method == "POST":
        f = EventForm(request.POST)
        if f.is_valid():
            e = f.save(commit=False); e.owner = request.user; e.save()
            messages.success(request, "Event added."); return redirect("events_calendar")
    else:
        f = EventForm()
    return render(request, "events/form.html", {"form": f})

# ---------- focus ----------
@login_required
def focus_timer(request):
    sessions = request.user.focus_sessions.all()[:20]
    return render(request, "focus/timer.html", {"sessions": sessions, "form": FocusForm(), "today_min": sum(s.duration_min for s in request.user.focus_sessions.filter(started_at__date=timezone.now().date()))})

@login_required
def focus_start(request):
    if request.method == "POST":
        f = FocusForm(request.POST)
        if f.is_valid():
            FocusSession.objects.create(owner=request.user, duration_min=f.cleaned_data["duration_min"])
            award_achievements(request.user)
            messages.success(request, f"Focus session recorded: {f.cleaned_data['duration_min']} min.")
        return redirect("focus_timer")

# ---------- achievements ----------
@login_required
def achievements(request):
    award_achievements(request.user)
    earned = list(request.user.achievements.all())
    earned_codes = {a.code for a in earned}
    locked = [t for t in ACHIEVEMENT_RULES if t[0] not in earned_codes]
    return render(request, "achievements.html", {"earned": earned, "locked": locked})

# ---------- search ----------
@login_required
def search(request):
    q = (request.GET.get("q") or "").strip()
    notes = request.user.notes.filter(Q(title__icontains=q)|Q(content__icontains=q)) if q else request.user.notes.none()
    snippets = request.user.snippets.filter(Q(title__icontains=q)|Q(code__icontains=q)) if q else request.user.snippets.none()
    tasks = request.user.tasks.filter(Q(title__icontains=q)|Q(description__icontains=q)) if q else request.user.tasks.none()
    return render(request, "search.html", {"q": q, "notes": notes, "snippets": snippets, "tasks": tasks, "total": notes.count()+snippets.count()+tasks.count()})

# ---------- profile ----------
@login_required
def profile(request):
    p = get_or_make_profile(request.user)
    return render(request, "profile.html", {"profile": p, "stats": {"notes":request.user.notes.count(),"snippets":request.user.snippets.count(),"tasks":request.user.tasks.count(),"events":request.user.events.count(),"focus":request.user.focus_sessions.count()}})

# ---------- share ----------
@login_required
def share_settings(request):
    p = get_or_make_profile(request.user)
    if request.method == "POST":
        f = ShareSettingsForm(request.POST, instance=p)
        if f.is_valid():
            f.is_valid()
            update = f.cleaned_data
            p.public_profile_enabled = update["public_profile_enabled"]
            p.public_bio            = update["public_bio"]
            p.public_show_notes     = update["public_show_notes"]
            p.public_show_snippets  = update["public_show_snippets"]
            if update.get("github_username"): p.github_username = update["github_username"]
            if update.get("github_token"):    p.github_token = update["github_token"]
            p.save()
            messages.success(request, "Settings saved.")
            return redirect("share_settings")
    else:
        f = ShareSettingsForm(instance=p)
    public_url = request.build_absolute_uri(f"/u/{request.user.username}/")
    return render(request, "share/settings.html", {"form": f, "public_url": public_url, "profile": p})

def public_profile(request, username):
    u = get_object_or_404(User, username=username)
    p = get_or_make_profile(u)
    if not p.public_profile_enabled:
        return render(request, "share/public.html", {"private": True, "owner": u})
    ctx = {"private": False, "owner": u, "profile": p}
    if p.public_show_notes:
        ctx["notes"] = u.notes.filter(visibility="public").order_by("-updated_at")
    if p.public_show_snippets:
        ctx["snippets"] = u.snippets.filter(visibility="public").order_by("-updated_at")
    return render(request, "share/public.html", ctx)
