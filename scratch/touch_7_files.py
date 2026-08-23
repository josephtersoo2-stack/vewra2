import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

target_files = [
    os.path.join(ROOT, "backend", "apps", "gamification", "models.py"),
    os.path.join(ROOT, "backend", "apps", "admin_api", "views.py"),
    os.path.join(ROOT, "backend", "apps", "admin_api", "urls.py"),
    os.path.join(ROOT, "admin-frontend", "src", "api", "adminApi.js"),
    os.path.join(ROOT, "admin-frontend", "src", "App.jsx"),
    os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "Sidebar.jsx"),
    os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "AdminLayout.jsx"),
]

for path in target_files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Normalize ending
    content = content.rstrip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Touched {path}")
