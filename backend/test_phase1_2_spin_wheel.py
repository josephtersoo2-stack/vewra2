import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vewra_backend.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.gamification.models import SpinWheelSegment, DailySpinRecord
from apps.gamification.services.spin_service import process_daily_spin, get_spin_status
from apps.wallet.models import Wallet, WalletTransaction

User = get_user_model()

def run_tests():
    print("======================================================================")
    print("RUNNING PHASE 1.2: DYNAMIC DAILY SPIN WHEEL TEST SUITE")
    print("======================================================================")

    # 1. Admin API Endpoints & Permissions
    print("\n--- 1. Testing Admin API Permissions & CRUD Operations ---")
    admin_user, _ = User.objects.get_or_create(username='admin_spin_tester', is_staff=True, is_superuser=True)
    regular_user, _ = User.objects.get_or_create(username='regular_spin_tester', is_staff=False)

    client = APIClient()

    # Test non-admin rejected with 403
    client.force_authenticate(user=regular_user)
    res_forbidden = client.get('/api/v1/admin/spin-wheel-segments/')
    assert res_forbidden.status_code == 403, f"Expected 403 for non-staff, got {res_forbidden.status_code}"
    print(" [PASS] Non-admin access correctly rejected with 403 Forbidden")

    # Test Admin reset_defaults
    client.force_authenticate(user=admin_user)
    res_reset = client.post('/api/v1/admin/spin-wheel-segments/reset_defaults/')
    assert res_reset.status_code == 200, f"Expected 200 on reset_defaults, got {res_reset.status_code}"
    assert res_reset.data['count'] == 12, f"Expected 12 segments after reset, got {res_reset.data['count']}"
    print(f" [PASS] reset_defaults created standard 12-segment wheel (Count: {res_reset.data['count']})")

    # Test Admin GET list
    res_list = client.get('/api/v1/admin/spin-wheel-segments/')
    assert res_list.status_code == 200
    assert len(res_list.data) == 12
    print(f" [PASS] Admin GET returned {len(res_list.data)} ordered segments")

    # Test Admin POST create custom segment
    custom_payload = {
        'label': 'Super Diamond Bonus',
        'reward_coins': 777,
        'weight': 3,
        'color': '#38BDF8',
        'order': 13,
        'is_active': True,
    }
    res_create = client.post('/api/v1/admin/spin-wheel-segments/', custom_payload, format='json')
    assert res_create.status_code == 201, f"Expected 201 Created, got {res_create.status_code}"
    new_segment_id = res_create.data['id']
    assert res_create.data['reward_coins'] == 777
    print(f" [PASS] Admin POST created new segment ID={new_segment_id} ('{res_create.data['label']}')")

    # Test Admin PATCH update segment
    res_patch = client.patch(f'/api/v1/admin/spin-wheel-segments/{new_segment_id}/', {'reward_coins': 888}, format='json')
    assert res_patch.status_code == 200
    assert res_patch.data['reward_coins'] == 888
    print(f" [PASS] Admin PATCH updated segment ID={new_segment_id} reward to {res_patch.data['reward_coins']}c")

    # Test Admin DELETE segment
    res_del = client.delete(f'/api/v1/admin/spin-wheel-segments/{new_segment_id}/')
    assert res_del.status_code == 204
    assert not SpinWheelSegment.objects.filter(id=new_segment_id).exists()
    print(f" [PASS] Admin DELETE deleted segment ID={new_segment_id}")

    # 2. Dynamic Weighted RNG & Spin Service Execution
    print("\n--- 2. Testing Spin Service Execution & Wallet Credit ---")
    test_player, _ = User.objects.get_or_create(username='spin_winner_player_1')
    today = timezone.now().date()
    DailySpinRecord.objects.filter(user=test_player).delete()
    from apps.gamification.models import SpinWheelClaim
    SpinWheelClaim.objects.filter(user=test_player).delete()
    
    # Initialize clean wallet
    wallet, _ = Wallet.objects.get_or_create(user=test_player)
    wallet.balance = 100
    wallet.save()

    # Initial status check
    status_data = get_spin_status(test_player)
    assert status_data['can_spin'] is True
    assert len(status_data['segments']) == 12
    print(f" [PASS] get_spin_status confirmed can_spin=True with {len(status_data['segments'])} active segments")

    # Execute daily spin
    spin_result = process_daily_spin(test_player)
    assert spin_result['success'] is True
    assert spin_result['already_spun'] is False
    assert spin_result['coins_won'] > 0
    assert spin_result['wallet_balance'] == 100 + spin_result['coins_won']
    print(f" [PASS] process_daily_spin won '{spin_result['segment_won']['label']}' (+{spin_result['coins_won']} Coins, New Balance: {spin_result['wallet_balance']})")

    # Verify Wallet Transaction record
    tx = WalletTransaction.objects.filter(wallet=wallet, transaction_type='daily_spin').latest('created_at')
    assert tx.description == "Daily Spin Wheel Win"
    assert tx.amount == spin_result['coins_won']
    print(f" [PASS] WalletTransaction created: '{tx.description}' amount=+{tx.amount}")

    # Verify 1-spin-per-day enforcement
    print("\n--- 3. Testing 1-Spin-Per-Day Enforcement ---")
    second_spin = process_daily_spin(test_player)
    assert second_spin['already_spun'] is True
    assert second_spin['success'] is False
    assert second_spin['message'] == 'Come back tomorrow!'
    print(f" [PASS] Duplicate spin blocked: '{second_spin['message']}'")

    status_after = get_spin_status(test_player)
    assert status_after['can_spin'] is False
    print(" [PASS] get_spin_status confirmed can_spin=False after spin")

    # Reset wheel defaults at test completion
    client.post('/api/v1/admin/spin-wheel-segments/reset_defaults/')

    print("\n======================================================================")
    print("SUCCESS: ALL PHASE 1.2 DYNAMIC SPIN WHEEL TESTS PASSED (100%)")
    print("======================================================================")

if __name__ == '__main__':
    run_tests()
