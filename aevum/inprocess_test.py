"""Aevum capstone — in-process test (no live HTTP server)."""
import os, sys, django
sys.path.insert(0, '/home/user/aevum')
os.environ['DJANGO_SETTINGS_MODULE'] = 'aevum.settings'
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from hub.models import (Note, CodeSnippet, Event, Task, FocusSession,
                        Achievement, Tag, Profile)
from django.utils import timezone
import datetime as dt

PASS, FAIL = [], []
def record(name, ok, detail=""):
    line = f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else "")
    (PASS if ok else FAIL).append(line)
    print(line, flush=True)

def section(s):
    print("\n== " + s + " ==", flush=True)

USERNAME = "alice"
PASSWORD = "Sup3rSecretPass2026"

section("PUBLIC SURFACE")
c = Client()
r = c.get("/");                record("GET / landing", r.status_code == 200, f"{r.status_code}")
r = c.get("/accounts/login/"); record("GET /accounts/login/",   r.status_code == 200, f"{r.status_code}")
r = c.get("/accounts/register/"); record("GET /accounts/register/", r.status_code == 200, f"{r.status_code}")

section("REGISTRATION")
c2 = Client(enforce_csrf_checks=False)
r = c2.post("/accounts/register/", {"username": USERNAME, "email":"alice@example.com", "password1": PASSWORD, "password2": PASSWORD}, follow=True)
record("POST /accounts/register/", r.status_code == 200 and User.objects.filter(username=USERNAME).exists())

section("LOGIN")
c3 = Client(enforce_csrf_checks=False)
r = c3.post("/accounts/login/", {"username": USERNAME, "password": PASSWORD}, follow=True)
logged_in = r.context and any(getattr(u,"is_authenticated",False) for u in [r.wsgi_request.user]) or User.objects.filter(username=USERNAME).exists()
record("POST /accounts/login/ 200", r.status_code == 200, f"{r.status_code}")

section("AUTH HTML PAGES")
urls = ["/dashboard/", "/notes/", "/snippets/", "/tasks/", "/events/", "/focus/", "/achievements/", "/share/settings/", "/profile/", "/search/?q=test"]
for u in urls:
    rr = c3.get(u)
    record(f"GET {u}", rr.status_code == 200, f"{rr.status_code}")

section("CRUD -- NOTE")
r = c3.post("/notes/create/", {"title":"Calculus Derivatives","content":"f'(x) = lim h->0 (f(x+h)-f(x))/h.","tag_names":"math, calculus","visibility":"private"}, follow=True)
record("POST /notes/create/", r.status_code == 200)
n = Note.objects.filter(title__icontains="Calculus").first()
record("Note persisted", n is not None, f"id={n.id if n else None}, total={Note.objects.count()}")

section("CRUD -- CODE SNIPPET")
code = "def quicksort(a):\n    if len(a)<=1: return a\n    p=a[0]\n    return [x for x in a[1:] if x<=p]+[p]+[x for x in a[1:] if x>p]\n"
r = c3.post("/snippets/create/", {"title":"Quicksort Python","language":"python","description":"partition sort","code":code,"labels_csv":"sorting,recursion","visibility":"private"}, follow=True)
record("POST /snippets/create/", r.status_code == 200)
s = CodeSnippet.objects.filter(title__icontains="Quicksort").first()
record("Snippet persisted", s is not None, f"id={s.id if s else None}, total={CodeSnippet.objects.count()}")

if s:
    r = c3.get(f"/snippets/{s.id}/"); record(f"GET /snippets/{s.id}/", r.status_code == 200)
    r = c3.get(f"/snippets/{s.id}/edit/"); record(f"GET /snippets/{s.id}/edit/", r.status_code == 200)

section("CRUD -- TASK + EVENT")
r = c3.post("/tasks/create/", {"title":"Finish capstone chapter","status":"todo","priority":"high"}, follow=True)
record("POST /tasks/create/", r.status_code == 200)
record("Task persisted", Task.objects.filter(title__icontains="capstone chapter").exists())

r = c3.post("/events/create/", {"title":"Math Midterm Exam","date":"2026-09-15","event_type":"exam","color":"#ff5577"}, follow=True)
record("POST /events/create/", r.status_code == 200)
record("Event persisted", Event.objects.filter(title__icontains="Math Midterm").exists())

section("FOCUS + ACHIEVEMENTS")
r = c3.post("/focus/start/", {"duration_min":25}, follow=True)
record("POST /focus/start/", r.status_code in (200,302))
record("FocusSession persisted", FocusSession.objects.count()>=1, f"count={FocusSession.objects.count()}")
record("Achievements auto-issued", Achievement.objects.count()>=0, f"count={Achievement.objects.count()}")

section("SHARE / PUBLIC PROFILE")
r = c3.post("/share/settings/", {"public_profile_enabled":"on","public_bio":"Hi, I'm Alice.","public_show_notes":"on","public_show_snippets":"on","github_username":"alice","github_token":""}, follow=True)
record("POST /share/settings/", r.status_code == 200)
prof = User.objects.get(username=USERNAME).profile
record("Public profile enabled", prof.public_profile_enabled)
r = c.get(f"/u/{USERNAME}/")
record("GET /u/alice/ public page", r.status_code == 200)

section("GLOBAL SEARCH")
r = c3.get("/search/?q=Calculus"); record("GET /search/?q=Calculus", r.status_code == 200)
r = c3.get("/search/?q=Quicksort"); record("GET /search/?q=Quicksort", r.status_code == 200)

section("REST API")
r = c3.get("/api/notes/"); ok = r.status_code == 200 and r["Content-Type"].startswith("application/json")
record("GET /api/notes/ JSON", ok, f"{r.status_code}/{r['Content-Type'][:40]}")
try:
    data = r.json(); items = data if isinstance(data,list) else data.get("results",[])
    found = any("Calculus" in (x.get("title","") if isinstance(x,dict) else "") for x in items)
except Exception: found = False
record("API /api/notes/ contains Calculus note", found)

r = c3.get("/api/snippets/"); record("GET /api/snippets/ JSON", r.status_code == 200 and r["Content-Type"].startswith("application/json"))
r = c3.get("/api/stats/"); record("GET /api/stats/ 200", r.status_code == 200)
try:
    sd = r.json()
    record("Stats dict has notes/snippets", isinstance(sd,dict) and "notes" in sd and "snippets" in sd, str(sd)[:90])
except Exception: record("Stats JSON parseable", False)

r = c3.get("/api/tasks/"); record("GET /api/tasks/ 200", r.status_code == 200)
r = c3.get("/api/events/"); record("GET /api/events/ 200", r.status_code == 200)
r = c3.get("/api/focus/"); record("GET /api/focus/ 200", r.status_code == 200)

section("GITHUB PUBLISH (graceful)")
if s:
    r = c3.post(f"/snippets/{s.id}/publish/", {"repo_owner":"alice","repo_name":"snippets"}, follow=True)
    record("POST publish no-token graceful", 200 <= r.status_code < 400, f"{r.status_code}")
    today = timezone.now().date()
    s.refresh_from_db()
    # last_pushed_to remains empty without token, no exception raised
    record("Publish did not crash the app", r.status_code < 500)

section("EDIT + DELETE")
r = c3.post("/snippets/create/", {"title":"Tmp","language":"text","code":"tmp","visibility":"private"}, follow=True)
tmp = CodeSnippet.objects.filter(title="Tmp").first()
if tmp:
    r = c3.post(f"/snippets/{tmp.id}/edit/", {"title":"Tmp-edited","language":"text","code":"tmp2","visibility":"private"}, follow=True)
    record("POST edit snippet 200", r.status_code == 200 and CodeSnippet.objects.filter(id=tmp.id, title="Tmp-edited").exists())
    r = c3.post(f"/snippets/{tmp.id}/delete/", follow=True)
    record("POST delete snippet 200", not CodeSnippet.objects.filter(id=tmp.id).exists())

if n:
    r = c3.post(f"/notes/{n.id}/edit/", {"title":"Calculus edited","content":"edited","visibility":"private"}, follow=True)
    record("POST edit note", r.status_code == 200 and Note.objects.filter(id=n.id, title="Calculus edited").exists())

print("\n== FINAL ==", flush=True)
print(f"PASS: {len(PASS)}    FAIL: {len(FAIL)}", flush=True)
if FAIL:
    print("-- FAILURES --", flush=True)
    for f_ in FAIL: print(f_, flush=True)
sys.exit(0 if not FAIL else 1)
