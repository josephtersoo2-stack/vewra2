import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.gamification.models import SpinWheelSegment, DailySpinRecord, UserProfile
from apps.wallet.models import Wallet, WalletTransaction
from apps.xp_badges.integration import on_daily_spin

DEFAULT_12_SEGMENTS = [
    {'order': 1, 'label': '5 Coins', 'reward_coins': 5, 'weight': 25, 'color': '#4F46E5', 'is_active': True},
    {'order': 2, 'label': '10 Coins', 'reward_coins': 10, 'weight': 20, 'color': '#6366F1', 'is_active': True},
    {'order': 3, 'label': '15 Coins', 'reward_coins': 15, 'weight': 15, 'color': '#8B5CF6', 'is_active': True},
    {'order': 4, 'label': '25 Coins', 'reward_coins': 25, 'weight': 12, 'color': '#EC4899', 'is_active': True},
    {'order': 5, 'label': '50 Coins', 'reward_coins': 50, 'weight': 8, 'color': '#F43F5E', 'is_active': True},
    {'order': 6, 'label': '100 Coins', 'reward_coins': 100, 'weight': 5, 'color': '#EF4444', 'is_active': True},
    {'order': 7, 'label': '5 Coins', 'reward_coins': 5, 'weight': 5, 'color': '#F59E0B', 'is_active': True},
    {'order': 8, 'label': '200 Coins', 'reward_coins': 200, 'weight': 4, 'color': '#10B981', 'is_active': True},
    {'order': 9, 'label': '10 Coins', 'reward_coins': 10, 'weight': 3, 'color': '#06B6D4', 'is_active': True},
    {'order': 10, 'label': '500 Coins', 'reward_coins': 500, 'weight': 1, 'color': '#3B82F6', 'is_active': True},
    {'order': 11, 'label': '20 Coins', 'reward_coins': 20, 'weight': 1, 'color': '#A855F7', 'is_active': True},
    {'order': 12, 'label': '1,000 Coins Jackpot!', 'reward_coins': 1000, 'weight': 1, 'color': '#EAB308', 'is_active': True},
]


def ensure_default_segments():
    """
    Seeds default 12 segments if none exist in the database.
    """
    if not SpinWheelSegment.objects.exists():
        for item in DEFAULT_12_SEGMENTS:
            SpinWheelSegment.objects.create(**item)


def get_spin_status(user) -> dict:
    """
    Phase 1.2: Returns current daily spin status and active wheel segments.
    """
    ensure_default_segments()
    today = timezone.now().date()

    has_spun = DailySpinRecord.objects.filter(user=user, spin_date=today).exists()

    segments = list(SpinWheelSegment.objects.filter(is_active=True).order_by('order'))
    if not segments:
        ensure_default_segments()
        segments = list(SpinWheelSegment.objects.filter(is_active=True).order_by('order'))

    return {
        'can_spin': not has_spun,
        'today_date': today.isoformat(),
        'segments': [
            {
                'id': s.id,
                'segment': s.order,
                'order': s.order,
                'label': s.label,
                'reward_coins': s.reward_coins,
                'value': str(s.reward_coins),
                'weight': s.weight,
                'color': s.color,
                'is_active': s.is_active,
            }
            for s in segments
        ]
    }


def process_daily_spin(user) -> dict:
    """
    Phase 1.2: Executes dynamic daily spin with weighted random probability and 1-spin-per-day enforcement.
    """
    ensure_default_segments()
    today = timezone.now().date()

    # Check 1 spin per day
    if DailySpinRecord.objects.filter(user=user, spin_date=today).exists():
        return {
            'already_spun': True,
            'success': False,
            'message': 'Come back tomorrow!'
        }

    # Fetch active segments
    segments = list(SpinWheelSegment.objects.filter(is_active=True).order_by('order'))
    if not segments:
        ensure_default_segments()
        segments = list(SpinWheelSegment.objects.filter(is_active=True).order_by('order'))

    # Weighted random selection
    weights = [max(1, s.weight) for s in segments]
    chosen_segment = random.choices(segments, weights=weights, k=1)[0]

    with transaction.atomic():
        # Create record
        record = DailySpinRecord.objects.create(
            user=user,
            spin_date=today,
            segment_won=chosen_segment,
            coins_won=chosen_segment.reward_coins
        )

        # Credit wallet
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

        coin_val = Decimal(str(chosen_segment.reward_coins))
        wallet.balance += coin_val
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=coin_val,
            balance_after=wallet.balance,
            transaction_type='daily_spin',
            description="Daily Spin Wheel Win",
            reference_id=f"spin_{record.id}"
        )

        # Award dynamic XP and evaluate badges via integration hook
        spin_gamification = on_daily_spin(user)

        return {
            'success': True,
            'already_spun': False,
            'segment_won': {
                'id': chosen_segment.id,
                'label': chosen_segment.label,
                'reward_coins': chosen_segment.reward_coins,
                'color': chosen_segment.color,
                'order': chosen_segment.order,
                'weight': chosen_segment.weight,
            },
            'coins_won': chosen_segment.reward_coins,
            'wallet_balance': float(wallet.balance),
            'message': f"Congratulations! You won {chosen_segment.reward_coins} Coins from the Daily Spin Wheel!",
            # Legacy fields
            'segment_landed': chosen_segment.order,
            'prize_type': 'coins',
            'prize_value': str(chosen_segment.reward_coins),
            'label': chosen_segment.label,
            'xp_earned': spin_gamification['xp'].get('xp_earned', 15),
            'level_info': spin_gamification['xp'],
            'badge_info': spin_gamification['badges'],
        }


def execute_daily_spin(user) -> dict:
    """
    Alias wrapper for process_daily_spin.
    """
    return process_daily_spin(user)
