import logging
from django.db import transaction
from apps.gamification.models import UserProfile

logger = logging.getLogger('vewra.xp')


def add_xp(user, amount: int, source: str = 'unknown') -> dict:
    """
    Phase 1.3: Core XP Engine.
    Credits XP to the user's UserProfile and dynamically checks for level up
    based on the formula: required_xp = (current_level ** 2) * 20.
    """
    if amount <= 0:
        amount = 0

    with transaction.atomic():
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

        old_level = profile.level or 1
        profile.xp = (profile.xp or 0) + amount

        # Formula: XP_required(level) = level² × 20
        leveled_up = False
        while True:
            current_level = profile.level or 1
            if current_level >= 101:
                break
            required_for_next = (current_level ** 2) * 20
            if profile.xp >= required_for_next:
                profile.level = current_level + 1
                leveled_up = True
            else:
                break

        profile.save()

        if leveled_up:
            logger.info(f"User {user.username} leveled up from L{old_level} to L{profile.level}! Total XP: {profile.xp}")

        return {
            'leveled_up': leveled_up,
            'new_level': profile.level,
            'total_xp': profile.xp,
            'xp_earned': amount,
            'source': source,
        }
