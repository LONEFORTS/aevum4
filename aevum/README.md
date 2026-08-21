# Aevum — Student Management System (Capstone)

Legendary black edition. X-grade design: true-black canvas, serif-italic display type,
cinematic starfield auth page, 3-column app shell, staggered entrance motion.
Django 4.2 + DRF + SQLite · phone-first workflow (Codespaces-ready).

## Features
- Cinematic login/register — animated starfield with meteors, italic serif wordmark
- X-style app shell: left sidebar (desktop), bottom tab bar (mobile), right search/API rail
- Dashboard: 49-day activity heatmap, serif stat cards, badges, upcoming events 
- Notes: CRUD, tags, file attachments, pin, public/private visibility
- Code Vault: language-tagged snippets, dark editor-styled viewer
- One-tap GitHub publish for snippets (GitHub Contents API + personal access token)
- Kanban board (To do / Doing / Done) with instant status moves
- Calendar: month grid with color-coded event chips
- Focus timer (Pomodoro) with session log and today counter
- Achievements engine: 8 auto-awarded badges
- Public shareable profile at /u/<username>/ with copy-link button
- Global search across notes, snippets and tasks
- REST API: /api/notes/ /api/snippets/ /api/tasks/ /api/events/ /api/focus/ /api/stats/

## Quick start
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Deploy from your phone (no laptop, no Termux)
1. Create a GitHub repo, upload these files (web upload works on phone).
2. Repo page → Code → Codespaces → Create codespace.
3. In the Codespaces terminal:
   `pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`
4. Ports tab → port 8000 → right-click → Make Public → copy the URL.
   That URL is your external-checker / evaluator link.

## GitHub publishing from Aevum
1. github.com → Settings → Developer settings → Personal access tokens (classic) → scope `repo`.
2. Aevum → Share → paste GitHub username + token → Save.
3. Code Vault → open a snippet → Publish to GitHub → enter owner + repo.

## Test
```bash
python inprocess_test.py   # full in-process E2E suite (no server needed)
```
