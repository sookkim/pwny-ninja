from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>PWNY Ninja</title>
  <style>
    body { background:#0b1220; color:#e5e7eb; font-family:sans-serif;
           display:flex; justify-content:center; align-items:center; height:100vh; }
    .card { background:#0f172a; padding:32px; border-radius:16px; text-align:center; }
    .badge { margin-top:12px; display:inline-block; padding:6px 12px;
             background:#1e293b; border-radius:999px; font-size:13px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>PWNY Ninja</h1>
    <img src="/static/pwny-kr.webp"
     alt="PWNY Ninja"
     style="width:240px;margin:16px auto;display:block;">
    <p>Silent deploys. Sharp visibility.</p>
    <div class="badge">git: {{ git_sha }}</div>
  </div>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(
        HTML,
        git_sha=os.getenv("GIT_SHA", "unknown")
    )

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)