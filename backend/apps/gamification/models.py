from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True, default='')
    
    # XP & Leveling (1.3)
    xp = models.BigIntegerField(default=0, db_index=True)
    level = models.IntegerField(default=1, db_index=True)
    
    # Streak Freezes (1.6)
    streak_freeze_count = models.IntegerField(default=0)
    
    # Showcase badges (up to 3 badge keys)
    showcase_badges = models.JSONField(default=list, blank=True)
    
    # Aggregated Stats
    lifetime_coins_earned = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_watch_seconds = models.FloatField(default=0.0)
    tasks_completed_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} | Level {self.level} ({self.xp} XP)"

    @property
    def xp_for_next_level(self) -> int:
        # Formula: XP_required(level) = level^2 * 20
        return (self.level ** 2) * 20

    @property
    def xp_progress_percent(self) -> float:
        needed = self.xp_for_next_level
        if needed <= 0:
            return 100.0
        # XP inside current level
        prev_level_xp = ((self.level - 1) ** 2) * 20 if self.level > 1 else 0
        current_span = needed - prev_level_xp
        user_span = max(0, self.xp - prev_level_xp)
        return min(100.0, round((user_span / max(1, current_span)) * 100.0, 1))


class DailyLoginStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_streak')
    streak_count = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_claimed_date = models.DateField(null=True, blank=True)
    freeze_used_this_week = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} | Streak: {self.streak_count}d (Best: {self.longest_streak}d)"

    @property
    def streak_multiplier(self) -> float:
        if self.streak_count >= 100:
            return 2.0
        elif self.streak_count >= 30:
            return 1.3
        elif self.streak_count >= 7:
            return 1.1
        return 1.0


class Badge(models.Model):
    CATEGORY_CHOICES = [
        ('onboarding', 'Onboarding'),
        ('watch', 'Watch & Retention'),
        ('social', 'Social & Referral'),
        ('earning', 'Earning & Economy'),
        ('special', 'Special & Milestones'),
    ]

    key = models.CharField(max_length=60, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='watch')
    icon_url = models.URLField(blank=True, default='')
    is_hidden = models.BooleanField(default=False)
    
    # Tier thresholds
    target_bronze = models.FloatField(default=1.0)
    target_silver = models.FloatField(default=5.0)
    target_gold = models.FloatField(default=25.0)
    target_diamond = models.FloatField(default=100.0)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"Badge: {self.name} ({self.key}) [{self.category}]"


class UserBadge(models.Model):
    TIER_CHOICES = [
        ('none', 'Locked'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
        ('legendary', 'Legendary'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='none')
    progress_current = models.FloatField(default=0.0)
    progress_target = models.FloatField(default=1.0)
    is_unlocked = models.BooleanField(default=False)
    awarded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} | {self.badge.name} [{self.tier}]"


class DailyQuest(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_quests')
    date = models.DateField(db_index=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    quest_type = models.CharField(max_length=40)  # watch_video, watch_seconds, complete_tasks, daily_spin, comment_video
    
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255)
    
    target_count = models.IntegerField(default=1)
    current_count = models.IntegerField(default=0)
    coin_reward = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    xp_reward = models.IntegerField(default=25)
    
    is_completed = models.BooleanField(default=False)
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date', 'difficulty')
        ordering = ['date', 'difficulty']

    def __str__(self):
        return f"{self.user.username} | {self.date} [{self.difficulty}] {self.title} ({self.current_count}/{self.target_count})"


class ScratchCardClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scratch_claims')
    date = models.DateField(db_index=True)
    grid_panels = models.JSONField(default=list)  # 3x3 layout of revealed symbols
    prize_type = models.CharField(max_length=50)
    prize_value = models.CharField(max_length=50)
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-claimed_at']

    def __str__(self):
        return f"{self.user.username} | Scratch on {self.date} -> {self.prize_type}: {self.prize_value}"


class StreakSettings(models.Model):
    """
    Phase 1.1: Daily Streak Calendar Settings (Singleton).
    Admin-configurable reward amounts, mystery box day, and reset rules.
    """
    day_1_coins = models.PositiveIntegerField(default=5, help_text="Coins awarded for Day 1")
    day_2_coins = models.PositiveIntegerField(default=10, help_text="Coins awarded for Day 2")
    day_3_coins = models.PositiveIntegerField(default=15, help_text="Coins awarded for Day 3")
    day_4_coins = models.PositiveIntegerField(default=20, help_text="Coins awarded for Day 4")
    day_5_coins = models.PositiveIntegerField(default=30, help_text="Coins awarded for Day 5")
    day_6_coins = models.PositiveIntegerField(default=40, help_text="Coins awarded for Day 6")
    day_7_coins = models.PositiveIntegerField(default=50, help_text="Coins awarded for Day 7")
    mystery_box_day = models.PositiveIntegerField(default=7, help_text="Day that triggers mystery box reward")
    streak_reset_days = models.PositiveIntegerField(
        default=1,
        help_text="Threshold of missed days before streak resets to Day 1"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Streak Settings"
        verbose_name_plural = "Streak Settings"

    def __str__(self):
        return f"Streak Settings (Day 1: {self.day_1_coins}c ... Day 7: {self.day_7_coins}c | Reset: {self.streak_reset_days}d)"

    def save(self, *args, **kwargs):
        if not self.pk and StreakSettings.objects.exists():
            existing = StreakSettings.objects.first()
            self.pk = existing.pk
            self._state.adding = False
            kwargs.pop('force_insert', None)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> 'StreakSettings':
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    def get_coins_map(self) -> dict:
        return {
            1: self.day_1_coins,
            2: self.day_2_coins,
            3: self.day_3_coins,
            4: self.day_4_coins,
            5: self.day_5_coins,
            6: self.day_6_coins,
            7: self.day_7_coins,
        }


class SpinWheelSegment(models.Model):
    """
    Phase 1.2: Configurable Daily Spin Wheel segment with custom label, reward coins, color, and probability weight.
    """
    label = models.CharField(max_length=100, help_text="Display label on wheel segment, e.g. '50 Coins'")
    reward_coins = models.PositiveIntegerField(default=10, help_text="Number of coins awarded when landed")
    weight = models.PositiveIntegerField(default=10, help_text="Probability weight percentage (1-100)")
    color = models.CharField(max_length=20, default="#6366F1", help_text="Hex color code for wheel segment UI")
    is_active = models.BooleanField(default=True, help_text="Whether this segment is active on the wheel")
    order = models.PositiveIntegerField(default=0, help_text="Display order on wheel (1-12)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Spin Wheel Segment"
        verbose_name_plural = "Spin Wheel Segments"

    def __str__(self):
        return f"[{self.order}] {self.label} (+{self.reward_coins}c, {self.weight}%)"


class DailySpinRecord(models.Model):
    """
    Phase 1.2: Tracks daily spins per user (1 spin per day strictly enforced).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_spin_records')
    spin_date = models.DateField(default=timezone.now, db_index=True)
    segment_won = models.ForeignKey(SpinWheelSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name='spin_wins')
    coins_won = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'spin_date')
        ordering = ['-created_at']
        verbose_name = "Daily Spin Record"
        verbose_name_plural = "Daily Spin Records"

    def __str__(self):
        return f"{self.user.username} | {self.spin_date} -> {self.segment_won.label if self.segment_won else 'Coins'} (+{self.coins_won}c)"

# Phase 1.2: SpinWheelSegment and DailySpinRecord models registered.
