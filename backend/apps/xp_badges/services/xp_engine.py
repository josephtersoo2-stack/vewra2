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


# Level milestone perks catalog (moved here from legacy xp_service.py — Phase Cleanup A)
LEVEL_PERKS = {
    1: ["Newbie Explorer Status", "Access to Standard Tasks"],
    5: ["Unlock Basic Badge Showcase Slot", "+50 Bonus Coins"],
    10: ["Unlock Coin Shop & Instant Voucher Exchange", "+100 Bonus Coins"],
    20: ["Unlock Guild Creation & Team Squads", "+1 Free Streak Freeze", "+250 Bonus Coins"],
    30: ["Unlock High-Payout Sponsor & Premium Tasks", "+500 Bonus Coins"],
    50: ["Unlock Creator Dashboard (Promote Your Own Videos)", "+1,000 Bonus Coins"],
    75: ["Unlock 2nd Badge Showcase Slot", "+2,500 Bonus Coins"],
    100: ["Prestige Master Rank Unlocked", "Lifetime 1.5x Multiplier", "+5,000 Bonus Coins"],
}


def get_level_rewards_catalog() -> list:
    """Returns milestone ladder with unlocked perks. Used by LevelRewardsCatalogView."""
    milestones = [1, 5, 10, 20, 30, 50, 75, 100]
    return [
        {
            'level': lvl,
            'xp_required': (lvl ** 2) * 20,
            'perks': LEVEL_PERKS.get(lvl, []),
        }
        for lvl in milestones
    ]
