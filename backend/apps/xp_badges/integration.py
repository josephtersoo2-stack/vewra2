import logging
from apps.xp_badges.models import XPSettings
from apps.xp_badges.services.xp_engine import add_xp
from apps.xp_badges.services.badge_engine import evaluate_all_badges

logger = logging.getLogger('vewra.xp_badges')


def on_streak_claimed(user) -> dict:
    """
    Phase 1.3 Hook: Triggered when a user claims their daily login streak.
    Awards configured streak XP and re-evaluates all user badge milestones.
    """
    settings = XPSettings.load()
    xp_amount = settings.xp_for_daily_streak
    xp_res = add_xp(user, xp_amount, source='daily_streak')
    badge_res = evaluate_all_badges(user)
    return {
        'xp': xp_res,
        'badges': badge_res,
    }


def on_daily_spin(user) -> dict:
    """
    Phase 1.3 Hook: Triggered when a user completes their daily spin wheel.
    Awards configured spin XP and re-evaluates all user badge milestones.
    """
    settings = XPSettings.load()
    xp_amount = settings.xp_for_daily_spin
    xp_res = add_xp(user, xp_amount, source='daily_spin')
    badge_res = evaluate_all_badges(user)
    return {
        'xp': xp_res,
        'badges': badge_res,
    }
