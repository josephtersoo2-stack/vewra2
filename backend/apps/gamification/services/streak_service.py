from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.gamification.models import DailyLoginStreak, StreakSettings, UserProfile
from apps.accounts.services.streak_service import process_daily_streak


def get_streak_status(user) -> dict:
    """
    Returns the user's daily streak calendar representation using dynamic StreakSettings.
    """
    settings = StreakSettings.load()
    coins_map = settings.get_coins_map()
    mystery_box_day = settings.mystery_box_day

    streak, _ = DailyLoginStreak.objects.get_or_create(user=user)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    is_claimed_today = streak.last_claimed_date == today
    day_in_cycle = ((streak.streak_count - 1) % 7) + 1 if streak.streak_count > 0 else 0
    next_day_reward = float(coins_map.get(((day_in_cycle) % 7) + 1, settings.day_1_coins))

    # 7-day calendar history representation
    calendar = []
    for day_idx in range(1, 8):
        calendar.append({
            'day': day_idx,
            'coins': float(coins_map.get(day_idx, 5)),
            'has_mystery_box': day_idx == mystery_box_day,
            'is_claimed': day_idx <= day_in_cycle if (streak.last_claimed_date in (today, yesterday)) else False,
            'is_current': day_idx == ((day_in_cycle % 7) + 1) if not is_claimed_today else (day_idx == day_in_cycle),
        })

    return {
        'streak_count': streak.streak_count,
        'longest_streak': streak.longest_streak,
        'day_in_cycle': day_in_cycle,
        'is_claimed_today': is_claimed_today,
        'streak_multiplier': streak.streak_multiplier,
        'next_day_reward': next_day_reward,
        'calendar': calendar,
    }


def claim_daily_streak(user) -> dict:
    """
    Wrapper around process_daily_streak for API compatibility.
    """
    return process_daily_streak(user)
