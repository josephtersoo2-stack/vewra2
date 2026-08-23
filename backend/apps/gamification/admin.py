from django.contrib import admin
from apps.gamification.models import (
    UserProfile,
    DailyLoginStreak,
    StreakSettings,
    SpinWheelClaim,
    SpinWheelSegment,
    DailySpinRecord,
    Badge,
    UserBadge,
    DailyQuest,
    ScratchCardClaim,
)

@admin.register(StreakSettings)
class StreakSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'day_1_coins', 'day_2_coins', 'day_3_coins', 'day_4_coins',
        'day_5_coins', 'day_6_coins', 'day_7_coins', 'mystery_box_day',
        'streak_reset_days', 'updated_at'
    ]

@admin.register(SpinWheelSegment)
class SpinWheelSegmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'label', 'reward_coins', 'weight', 'color', 'is_active']
    list_editable = ['label', 'reward_coins', 'weight', 'color', 'is_active']
    ordering = ['order']

@admin.register(DailySpinRecord)
class DailySpinRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'spin_date', 'segment_won', 'coins_won', 'created_at']
    search_fields = ['user__username']
    list_filter = ['spin_date']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'xp', 'streak_freeze_count', 'lifetime_coins_earned', 'created_at']
    search_fields = ['user__username', 'user__email', 'display_name']

@admin.register(DailyLoginStreak)
class DailyLoginStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'streak_count', 'longest_streak', 'last_claimed_date', 'freeze_used_this_week']
    search_fields = ['user__username']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'category', 'is_hidden']
    list_filter = ['category', 'is_hidden']

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'tier', 'is_unlocked', 'awarded_at']
    search_fields = ['user__username', 'badge__name']

@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'difficulty', 'title', 'is_completed', 'is_claimed']
    list_filter = ['difficulty', 'is_completed', 'is_claimed', 'date']
