import logging
from django.db.models import Sum
from django.utils import timezone

from apps.gamification.models import Badge, UserBadge, UserProfile
from apps.tasks.models import WatchSession
from apps.wallet.models import WalletTransaction

logger = logging.getLogger('vewra.badges')


def evaluate_all_badges(user) -> dict:
    """
    Phase 1.3: Badge Evaluation Engine.
    Aggregates user stats across the platform and evaluates progression/tiers
    for all registered badges.
    """
    # 1. Aggregate user stats
    watch_agg = WatchSession.objects.filter(user=user).aggregate(total_sec=Sum('total_watched_seconds'))
    total_watched_seconds = float(watch_agg['total_sec'] or 0.0)
    total_watch_minutes = total_watched_seconds / 60.0

    total_tasks_completed = WatchSession.objects.filter(user=user, is_completed=True).count()

    coins_agg = WalletTransaction.objects.filter(wallet__user=user, amount__gt=0).aggregate(total_coins=Sum('amount'))
    total_coins_earned = float(coins_agg['total_coins'] or 0.0)

    # 2. Fetch all badges
    badges = list(Badge.objects.all())
    newly_unlocked = []
    unlocked_count = 0

    # 3. Evaluate each badge
    for badge in badges:
        # Determine stat to compare against thresholds
        if badge.key in ('first_steps', 'getting_started', 'marathoner'):
            stat = float(total_tasks_completed)
        elif badge.key in ('couch_potato', 'night_owl', 'binge_watcher'):
            stat = float(total_watch_minutes)
        elif badge.key in ('coin_collector', 'high_roller', 'millionaire'):
            stat = float(total_coins_earned)
        elif badge.category == 'watch':
            stat = float(total_watch_minutes)
        elif badge.category == 'earning':
            stat = float(total_coins_earned)
        elif badge.category in ('onboarding', 'tasks'):
            stat = float(total_tasks_completed)
        elif badge.category == 'special':
            profile = getattr(user, 'profile', None)
            stat = float(profile.level if profile else 1)
        else:
            stat = float(total_tasks_completed)

        # Calculate tier based on thresholds
        if stat >= badge.target_diamond:
            new_tier = 'diamond'
            progress_target = badge.target_diamond
        elif stat >= badge.target_gold:
            new_tier = 'gold'
            progress_target = badge.target_diamond
        elif stat >= badge.target_silver:
            new_tier = 'silver'
            progress_target = badge.target_gold
        elif stat >= badge.target_bronze:
            new_tier = 'bronze'
            progress_target = badge.target_silver
        else:
            new_tier = 'none'
            progress_target = badge.target_bronze

        is_unlocked = (new_tier != 'none')
        if is_unlocked:
            unlocked_count += 1

        # Get or create UserBadge record
        user_badge, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
        was_unlocked = user_badge.is_unlocked

        user_badge.tier = new_tier
        user_badge.progress_current = round(stat, 2)
        user_badge.progress_target = round(progress_target, 2)
        user_badge.is_unlocked = is_unlocked

        if is_unlocked and not was_unlocked:
            user_badge.awarded_at = timezone.now()
            newly_unlocked.append(badge.name)
            logger.info(f"Badge unlocked for {user.username}: {badge.name} ({new_tier.upper()})")
        elif not is_unlocked:
            user_badge.awarded_at = None

        user_badge.save()

    return {
        'evaluated_count': len(badges),
        'unlocked_count': unlocked_count,
        'newly_unlocked': newly_unlocked,
        'stats': {
            'total_watch_minutes': round(total_watch_minutes, 2),
            'total_tasks_completed': total_tasks_completed,
            'total_coins_earned': round(total_coins_earned, 2),
        }
    }


# Moved from legacy badge_service.py — Phase Cleanup A
DEFAULT_BADGES = [
    # Onboarding
    {'key': 'first_steps', 'name': 'First Steps', 'desc': 'Complete your very first video task.', 'cat': 'onboarding', 'b': 1, 's': 1, 'g': 1, 'd': 1},
    {'key': 'getting_started', 'name': 'Task Collector', 'desc': 'Complete video tasks.', 'cat': 'onboarding', 'b': 5, 's': 25, 'g': 100, 'd': 500},
    # Watch
    {'key': 'couch_potato', 'name': 'Couch Potato', 'desc': 'Total watch time hours on Vewra.', 'cat': 'watch', 'b': 10, 's': 50, 'g': 250, 'd': 1000},
    {'key': 'marathoner', 'name': 'Marathoner', 'desc': 'Complete a 30+ minute video task.', 'cat': 'watch', 'b': 1, 's': 5, 'g': 20, 'd': 50},
    # Earning
    {'key': 'coin_collector', 'name': 'Coin Collector', 'desc': 'Total coins accumulated in wallet.', 'cat': 'earning', 'b': 100, 's': 1000, 'g': 10000, 'd': 50000},
    {'key': 'lucky_streak', 'name': 'Streak Legend', 'desc': 'Maintain daily login streak days.', 'cat': 'earning', 'b': 7, 's': 30, 'g': 60, 'd': 100},
    # Leveling
    {'key': 'century_club', 'name': 'Century Club', 'desc': 'Reach higher account levels.', 'cat': 'special', 'b': 5, 's': 20, 'g': 50, 'd': 100},
]


def seed_default_badges():
    """Seeds the default badge catalog. Called by admin seed_defaults action."""
    for bdata in DEFAULT_BADGES:
        Badge.objects.update_or_create(
            key=bdata['key'],
            defaults={
                'name': bdata['name'],
                'description': bdata['desc'],
                'category': bdata['cat'],
                'target_bronze': bdata['b'],
                'target_silver': bdata['s'],
                'target_gold': bdata['g'],
                'target_diamond': bdata['d'],
            }
        )
