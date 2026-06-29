"""Push latest local commit's changed files via Contents API."""
import json, base64, urllib.request, pathlib, subprocess

ROOT = pathlib.Path.home() / "Desktop" / "ViroScope-OS"
url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                     capture_output=True, text=True).stdout.strip()
token = url.split("://")[1].split("@")[0]
OWNER, REPO, BRANCH = "mariontube", "ViroScope-OS", "main"

def api(method, path, data=None):
    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(api_url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()), resp.status

# Get files changed in the latest commit
files = subprocess.run(
    ["git", "-C", str(ROOT), "diff", "--name-only", "HEAD~1", "HEAD"],
    capture_output=True, text=True
).stdout.strip().split("\n")
files = [f for f in files if f]

# Also get commit message
msg = subprocess.run(
    ["git", "-C", str(ROOT), "log", "--format=%B", "-1", "HEAD"],
    capture_output=True, text=True
).stdout.strip()

print(f"Files in latest commit: {len(files)}")
for f in files:
    fpath = ROOT / f
    if not fpath.exists():
        print(f"  DEL: {f}")
        continue
    content_b64 = base64.b64encode(fpath.read_bytes()).decode()
    try:
        existing, _ = api("GET", f"/contents/{f}?ref={BRANCH}")
        file_sha = existing["sha"]
    except:
        file_sha = None
    data = {"message": msg, "content": content_b64, "branch": BRANCH}
    if file_sha:
        data["sha"] = file_sha
    result, code = api("PUT", f"/contents/{f}", data)
    status = "OK" if code in (200, 201) else f"FAIL {code}"
    print(f"  {status}: {f}")

print("Done.")
