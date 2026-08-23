import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_path = os.path.join(ROOT, "backend", "apps", "ai_service", "tests.py")

with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix fallback test
content = content.replace(
    'self.assertTrue(any("Flutter in 100 Seconds" in k for k in keywords))',
    'self.assertTrue(any("Flutter in 100 Seconds" in (k["query"] if isinstance(k, dict) else k) for k in keywords))'
)

# Fix gemini mock test
content = content.replace(
    'self.assertEqual(keywords[0], "Flutter in 100 Seconds Fireship")',
    'query_str = keywords[0]["query"] if isinstance(keywords[0], dict) else keywords[0]\n        self.assertEqual(query_str, "Flutter in 100 Seconds Fireship")'
)

with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated apps/ai_service/tests.py")

# Update test_phase1_2_spin_wheel.py
wheel_test_path = os.path.join(ROOT, "backend", "test_phase1_2_spin_wheel.py")
with open(wheel_test_path, "r", encoding="utf-8") as f:
    wheel_test = f.read()

wheel_test = wheel_test.replace(
    "DailySpinRecord.objects.filter(user=test_player).delete()",
    "DailySpinRecord.objects.filter(user=test_player).delete()\n    from apps.gamification.models import SpinWheelClaim\n    SpinWheelClaim.objects.filter(user=test_player).delete()"
)

with open(wheel_test_path, "w", encoding="utf-8") as f:
    f.write(wheel_test)

print("Updated test_phase1_2_spin_wheel.py")
