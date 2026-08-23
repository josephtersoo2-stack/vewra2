from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.gamification.models import DailyLoginStreak, StreakSettings, UserProfile
from apps.gamification.services.xp_service import add_xp
from apps.wallet.models import Wallet, WalletTransaction


def process_daily_streak(user) -> dict:
    """
    Phase 1.1: Process daily streak claim for a user using dynamic StreakSettings.
    No hardcoded business logic or reward amounts.
    """
    settings = StreakSettings.load()
    coins_map = settings.get_coins_map()
    mystery_box_day = settings.mystery_box_day
    streak_reset_days = settings.streak_reset_days

    today = timezone.now().date()

    with transaction.atomic():
        streak, _ = DailyLoginStreak.objects.select_for_update().get_or_create(user=user)
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)

        last_date = streak.last_claimed_date

        if last_date == today:
            streak_day = ((streak.streak_count - 1) % 7) + 1 if streak.streak_count > 0 else 1
            return {
                'already_claimed': True,
                'message': 'Daily streak reward already claimed today!',
                'streak_count': streak.streak_count,
                'streak_day': streak_day,
                'day_in_cycle': streak_day,
                'coins_awarded': 0,
                'coins_earned': 0.0,
                'has_mystery_box': False,
                'streak_multiplier': streak.streak_multiplier,
            }

        days_diff = (today - last_date).days if last_date else 999
        freeze_used = False

        if days_diff == 1:
            # Consecutive day login
            streak.streak_count += 1
        elif days_diff == 2 and profile.streak_freeze_count > 0 and streak.freeze_used_this_week < 3:
            # Auto-consume streak freeze
            profile.streak_freeze_count -= 1
            profile.save()
            streak.freeze_used_this_week += 1
            streak.streak_count += 1
            freeze_used = True
        elif days_diff > streak_reset_days:
            # Streak broken past threshold -> reset to Day 1
            streak.streak_count = 1
        else:
            streak.streak_count = 1

        streak_day = ((streak.streak_count - 1) % 7) + 1
        coins_awarded = coins_map.get(streak_day, settings.day_1_coins)
        has_mystery_box = (streak_day == mystery_box_day)

        streak.last_claimed_date = today
        streak.longest_streak = max(streak.longest_streak, streak.streak_count)
        streak.save()

        # Credit wallet
        coins_dec = Decimal(str(coins_awarded))
        wallet.balance += coins_dec
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=coins_dec,
            balance_after=wallet.balance,
            transaction_type='daily_streak',
            description=f"Day {streak_day} Daily Streak Bonus ({streak.streak_count}d streak)",
            reference_id=f"streak_{today.isoformat()}"
        )

        # Award XP
        xp_res = add_xp(user, 15, 'daily_streak')

        # Milestone: every 30 days grant +2 streak freezes
        if streak.streak_count > 0 and streak.streak_count % 30 == 0:
            profile.streak_freeze_count += 2
            profile.save()

        return {
            'already_claimed': False,
            'message': f"Claimed Day {streak_day} Streak Reward! (+{coins_awarded} Coins)",
            'streak_count': streak.streak_count,
            'longest_streak': streak.longest_streak,
            'streak_day': streak_day,
            'day_in_cycle': streak_day,
            'coins_awarded': coins_awarded,
            'coins_earned': float(coins_awarded),
            'has_mystery_box': has_mystery_box,
            'mystery_box_unlocked': has_mystery_box,
            'streak_multiplier': streak.streak_multiplier,
            'freeze_used': freeze_used,
            'wallet_balance': float(wallet.balance),
            'xp_earned': 15,
            'level_info': xp_res,
        }
