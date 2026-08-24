from django.urls import path
from apps.gamification.views import (
    DailyStreakStatusView,
    DailyStreakClaimView,
    SpinWheelStatusView,
    DailySpinView,
    ScratchStatusView,
    DailyScratchView,
    UserProfileView,
    LevelRewardsCatalogView,
    BadgeListView,
    BadgeShowcaseView,
    DailyQuestListView,
    DailyQuestClaimView,
)
from apps.gamification.mobile_api_views import (
    ClaimStreakView,
    StreakStatusView,
    SpinWheelView,
    GetSpinSegmentsView,
)

urlpatterns = [
    # Rewards & Streaks (legacy paths — kept for backward compatibility)
    path('rewards/daily-status/', DailyStreakStatusView.as_view(), name='daily_streak_status'),
    path('rewards/daily-claim/', DailyStreakClaimView.as_view(), name='daily_streak_claim'),
    path('rewards/spin-status/', SpinWheelStatusView.as_view(), name='spin_wheel_status'),
    path('rewards/daily-spin/', DailySpinView.as_view(), name='daily_spin'),
    path('rewards/scratch-status/', ScratchStatusView.as_view(), name='scratch_status'),
    path('rewards/daily-scratch/', DailyScratchView.as_view(), name='daily_scratch'),

    # Phase 1.5: Clean mobile gamification paths
    path('gamification/streak/status/', StreakStatusView.as_view(), name='mobile_streak_status'),
    path('gamification/streak/claim/', ClaimStreakView.as_view(), name='mobile_streak_claim'),
    path('gamification/spin/', SpinWheelView.as_view(), name='mobile_spin'),
    path('gamification/spin/segments/', GetSpinSegmentsView.as_view(), name='mobile_spin_segments'),

    # Profile & Progression
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/level-rewards/', LevelRewardsCatalogView.as_view(), name='level_rewards_catalog'),
    path('profile/badge-showcase/', BadgeShowcaseView.as_view(), name='badge_showcase'),

    # Badges
    path('badges/', BadgeListView.as_view(), name='badge_list'),

    # Quests
    path('quests/daily/', DailyQuestListView.as_view(), name='daily_quests'),
    path('quests/daily/<int:quest_id>/claim/', DailyQuestClaimView.as_view(), name='daily_quest_claim'),
]
