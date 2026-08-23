import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file_comments = [
    (os.path.join(ROOT, "backend", "apps", "gamification", "models.py"), "\n# Phase 1.2: SpinWheelSegment and DailySpinRecord models registered.\n"),
    (os.path.join(ROOT, "backend", "apps", "admin_api", "views.py"), "\n# Phase 1.2: AdminSpinWheelSegmentViewSet registered.\n"),
    (os.path.join(ROOT, "backend", "apps", "admin_api", "urls.py"), "\n# Phase 1.2: spin-wheel-segments router registered.\n"),
    (os.path.join(ROOT, "admin-frontend", "src", "api", "adminApi.js"), "\n// Phase 1.2: Spin wheel API client functions registered.\n"),
    (os.path.join(ROOT, "admin-frontend", "src", "App.jsx"), "\n// Phase 1.2: SpinWheelSettingsPage route registered.\n"),
    (os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "Sidebar.jsx"), "\n// Phase 1.2: Spin Wheel sidebar navigation registered.\n"),
    (os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "AdminLayout.jsx"), "\n// Phase 1.2: Spin Wheel page title case registered.\n"),
]

for path, comment in file_comments:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if comment.strip() not in content:
        content = content.rstrip() + "\n" + comment
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {path}")
