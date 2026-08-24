"""
Phase 1.4: User-facing Mobile API for XP, Levels, and Badges.
Provides two authenticated endpoints consumed by the Flutter mobile app:
  - GET /api/v1/xp-badges/profile/  -> user's XP, level, streak data
  - GET /api/v1/xp-badges/badges/   -> full badge catalog merged with user progress
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.gamification.models import UserProfile, Badge, UserBadge


class UserProfileXPView(APIView):
    """
    GET /api/v1/xp-badges/profile/

    Returns the authenticated user's current XP, level progression,
    streak freeze inventory, and showcase badges.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'display_name': user.get_full_name() or user.username},
        )

        data = {
            'user_id': user.id,
            'username': user.username,
            'display_name': profile.display_name,
            'avatar_url': profile.avatar_url,

            # XP & Level
            'xp': profile.xp,
            'level': profile.level,
            'xp_for_next_level': profile.xp_for_next_level,
            'xp_progress_percent': profile.xp_progress_percent,

            # Streak Freeze inventory (Phase 1.6 — field exists on model)
            'streak_freeze_count': profile.streak_freeze_count,

            # Showcase: up to 3 badge keys the user has pinned to their profile
            'showcase_badges': profile.showcase_badges,

            # Aggregated lifetime stats (useful for mobile profile card)
            'lifetime_coins_earned': float(profile.lifetime_coins_earned),
            'total_watch_minutes': round(profile.total_watch_seconds / 60.0, 1),
            'tasks_completed_count': profile.tasks_completed_count,
        }

        return Response(data, status=status.HTTP_200_OK)


class UserBadgeListView(APIView):
    """
    GET /api/v1/xp-badges/badges/

    Returns the FULL badge catalog (all Badge objects including locked ones)
    merged with the requesting user's individual progress from UserBadge.
    The mobile app uses this to render the complete collection screen with
    locked/unlocked tiers and real-time progress bars.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch all badges ordered by category, name
        all_badges = Badge.objects.order_by('category', 'name')

        # Build a quick lookup of user's existing progress records
        user_badge_map = {
            ub.badge_id: ub
            for ub in UserBadge.objects.filter(user=user).select_related('badge')
        }

        results = []
        for badge in all_badges:
            ub = user_badge_map.get(badge.id)

            results.append({
                # Badge definition
                'id': badge.id,
                'key': badge.key,
                'name': badge.name,
                'description': badge.description,
                'category': badge.category,
                'icon_url': badge.icon_url,
                'is_hidden': badge.is_hidden,

                # Tier thresholds (so the app can render the progress arc)
                'target_bronze': badge.target_bronze,
                'target_silver': badge.target_silver,
                'target_gold': badge.target_gold,
                'target_diamond': badge.target_diamond,

                # User-specific progress (defaults to locked / zero if no record yet)
                'tier': ub.tier if ub else 'none',
                'progress_current': ub.progress_current if ub else 0.0,
                'progress_target': ub.progress_target if ub else badge.target_bronze,
                'is_unlocked': ub.is_unlocked if ub else False,
                'awarded_at': ub.awarded_at.isoformat() if (ub and ub.awarded_at) else None,
            })

        return Response({'count': len(results), 'badges': results}, status=status.HTTP_200_OK)
