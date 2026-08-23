import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vewra_backend.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.gamification.models import StreakSettings, DailyLoginStreak
from apps.accounts.services.streak_service import process_daily_streak
from apps.gamification.services.streak_service import get_streak_status, claim_daily_streak

User = get_user_model()

def run_tests():
    print("======================================================================")
    print("RUNNING PHASE 1.1: DYNAMIC DAILY STREAK SETTINGS TEST SUITE")
    print("======================================================================")

    # 1. Singleton & Model Validation
    print("\n--- 1. Testing StreakSettings Singleton & Model ---")
    s1 = StreakSettings.load()
    s1.day_1_coins = 7
    s1.day_7_coins = 77
    s1.mystery_box_day = 6
    s1.streak_reset_days = 2
    s1.save()

    # Attempt to create another instance
    s2 = StreakSettings(day_1_coins=99)
    s2.save()

    count = StreakSettings.objects.count()
    assert count == 1, f"Expected exactly 1 StreakSettings instance, got {count}"
    loaded = StreakSettings.load()
    assert loaded.day_1_coins == 99, f"Expected s2 to update singleton to 99, got {loaded.day_1_coins}"
    print(f" [PASS] Singleton strictly enforced (1 record in DB: ID={loaded.id})")

    # 2. Admin API Endpoint
    print("\n--- 2. Testing Admin API Endpoint (/api/v1/admin/gamification-settings/) ---")
    admin_user, _ = User.objects.get_or_create(username='admin_streak_tester', is_staff=True, is_superuser=True)
    regular_user, _ = User.objects.get_or_create(username='regular_streak_tester', is_staff=False)

    # Test unauthorized access
    client = APIClient()
    client.force_authenticate(user=regular_user)
    res_forbidden = client.get('/api/v1/admin/gamification-settings/')
    assert res_forbidden.status_code == 403, f"Expected 403 for non-staff, got {res_forbidden.status_code}"
    print(" [PASS] Non-admin access correctly rejected with 403 Forbidden")

    # Test Admin GET
    client.force_authenticate(user=admin_user)
    res_get = client.get('/api/v1/admin/gamification-settings/')
    assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}"
    assert res_get.data['day_1_coins'] == 99
    print(" [PASS] Admin GET returned streak configuration:", res_get.data)

    # Test Admin PUT update
    update_payload = {
        'day_1_coins': 12,
        'day_2_coins': 20,
        'day_3_coins': 28,
        'day_4_coins': 36,
        'day_5_coins': 48,
        'day_6_coins': 60,
        'day_7_coins': 88,
        'mystery_box_day': 7,
        'streak_reset_days': 1,
    }
    res_put = client.put('/api/v1/admin/gamification-settings/', update_payload, format='json')
    assert res_put.status_code == 200, f"Expected 200, got {res_put.status_code}"
    assert res_put.data['day_1_coins'] == 12
    assert res_put.data['day_7_coins'] == 88
    print(" [PASS] Admin PUT successfully updated gamification settings")

    # 3. Dynamic Streak Processing
    print("\n--- 3. Testing Dynamic Streak Calculation in Services ---")
    test_player, _ = User.objects.get_or_create(username='streak_player_1')
    DailyLoginStreak.objects.filter(user=test_player).delete()

    # Day 1 claim
    claim1 = process_daily_streak(test_player)
    assert claim1['streak_day'] == 1
    assert claim1['coins_awarded'] == 12, f"Expected 12 coins from updated settings, got {claim1['coins_awarded']}"
    assert claim1['has_mystery_box'] is False
    print(f" [PASS] Day 1 claimed dynamic reward: +{claim1['coins_awarded']} Coins (matched setting 12)")

    # Status calendar representation
    status_data = get_streak_status(test_player)
    assert status_data['calendar'][0]['coins'] == 12.0
    assert status_data['calendar'][6]['coins'] == 88.0
    assert status_data['calendar'][6]['has_mystery_box'] is True
    print(f" [PASS] Calendar status dynamically mapped from DB: Day 1 = {status_data['calendar'][0]['coins']}c, Day 7 = {status_data['calendar'][6]['coins']}c")

    # Reset settings back to standard defaults for clean baseline
    std = StreakSettings.load()
    std.day_1_coins = 5
    std.day_2_coins = 10
    std.day_3_coins = 15
    std.day_4_coins = 20
    std.day_5_coins = 30
    std.day_6_coins = 40
    std.day_7_coins = 50
    std.mystery_box_day = 7
    std.streak_reset_days = 1
    std.save()

    print("\n======================================================================")
    print("SUCCESS: ALL PHASE 1.1 DYNAMIC STREAK TESTS PASSED (100%)")
    print("======================================================================")

if __name__ == '__main__':
    run_tests()
