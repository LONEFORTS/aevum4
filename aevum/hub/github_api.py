"""GitHub content-API push for Aevum code snippets.
Uses Django settings or Profile.github_token. Never raises — returns dict."""
import base64, json
import requests as rq

API = "https://api.github.com"

def push_snippet(snippet, repo_owner, repo_name, token=None, commit_message=None):
    try:
        token = token or (snippet.owner.profile.github_token if hasattr(snippet.owner, "profile") else "")
        repo_owner = repo_owner or (snippet.owner.profile.github_username if hasattr(snippet.owner, "profile") else "")
        if not token:
            return {"ok": False, "error": "no_token", "hint": "Add a GitHub personal access token in Share settings."}
        if not (repo_owner and repo_name):
            return {"ok": False, "error": "no_repo", "hint": "Specify repo_owner and repo_name."}
        path = f"aevum/{snippet.slug}.{snippet.language}"
        url = f"{API}/repos/{repo_owner}/{repo_name}/contents/{path}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        # Get existing file SHA if present (for update)
        existing = rq.get(url, headers=headers, timeout=10)
        payload = {
            "message": commit_message or f"Aevum: push {snippet.title}",
            "content": base64.b64encode((snippet.code or "").encode("utf-8")).decode("ascii"),
            "branch": "main",
        }
        if existing.status_code == 200:
            payload["sha"] = existing.json().get("sha")
        resp = rq.put(url, headers=headers, data=json.dumps(payload), timeout=15)
        if resp.status_code in (200, 201):
            j = resp.json()
            return {"ok": True, "url": j.get("content",{}).get("html_url") or resp.url, "path": path}
        return {"ok": False, "error": "github_api", "status": resp.status_code, "detail": resp.text[:300]}
    except Exception as ex:
        return {"ok": False, "error": "exception", "detail": str(ex)[:300]}
