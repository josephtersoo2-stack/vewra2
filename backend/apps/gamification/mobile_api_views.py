"""
Phase 1.5 (Chunk 1): Clean mobile-facing API views for Daily Streak and Spin Wheel.

These views expose the same business logic as the existing rewards views
but under cleaner, more intuitive URL paths for the Flutter mobile app:
  POST /api/v1/gamification/streak/claim/     -> ClaimStreakView
  POST /api/v1/gamification/spin/             -> SpinWheelView
  GET  /api/v1/gamification/spin/segments/    -> GetSpinSegmentsView
  GET  /api/v1/gamification/streak/status/    -> StreakStatusView (bonus)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.services.streak_service import process_daily_streak
from apps.gamification.services.streak_service import get_streak_status
from apps.gamification.services.spin_service import process_daily_spin, get_spin_status


class ClaimStreakView(APIView):
    """
    POST /api/v1/gamification/streak/claim/

    Claims the user's daily login streak reward. Returns the full streak
    result dict including coins_awarded, streak_day, xp_earned, and badge info.
    Idempotent — returns already_claimed=True if already claimed today.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = process_daily_streak(request.user)
        return Response(result, status=status.HTTP_200_OK)


class StreakStatusView(APIView):
    """
    GET /api/v1/gamification/streak/status/

    Returns the user's current streak state and 7-day calendar for the mobile
    streak UI without triggering a claim.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_streak_status(request.user)
        return Response(data, status=status.HTTP_200_OK)


class SpinWheelView(APIView):
    """
    POST /api/v1/gamification/spin/

    Executes the user's daily spin. Enforces 1-spin-per-day.
    Returns segment_won, coins_won, xp_earned, wallet_balance, badge_info.
    Returns already_spun=True (HTTP 200) if the user already spun today.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = process_daily_spin(request.user)
        # Return 200 regardless — let the client inspect already_spun flag
        return Response(result, status=status.HTTP_200_OK)


class GetSpinSegmentsView(APIView):
    """
    GET /api/v1/gamification/spin/segments/

    Returns the active wheel segments (label, reward_coins, color, weight)
    plus can_spin status so the mobile app can render the wheel before spinning.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_spin_status(request.user)
        return Response(data, status=status.HTTP_200_OK)
