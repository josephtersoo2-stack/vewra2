from django.db import models


class XPSettings(models.Model):
    """
    Phase 1.3: Core XP Engine Settings (Singleton).
    Configures XP rewards awarded across different platform actions.
    """
    xp_per_minute_watched = models.PositiveIntegerField(
        default=10,
        help_text="XP awarded per 1 minute of video watched"
    )
    xp_for_completing_task = models.PositiveIntegerField(
        default=50,
        help_text="Bonus XP awarded upon completing a video task"
    )
    xp_for_daily_streak = models.PositiveIntegerField(
        default=15,
        help_text="XP awarded for claiming daily login streak reward"
    )
    xp_for_daily_spin = models.PositiveIntegerField(
        default=15,
        help_text="XP awarded for completing daily spin wheel"
    )
    xp_for_referral = models.PositiveIntegerField(
        default=100,
        help_text="XP awarded for referring a new active user"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "XP Settings"
        verbose_name_plural = "XP Settings"

    def __str__(self):
        return f"XP Settings (Watch: {self.xp_per_minute_watched} XP/min, Task: {self.xp_for_completing_task} XP, Streak: {self.xp_for_daily_streak} XP)"

    def save(self, *args, **kwargs):
        if not self.pk and XPSettings.objects.exists():
            existing = XPSettings.objects.first()
            self.pk = existing.pk
            self._state.adding = False
            kwargs.pop('force_insert', None)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> 'XPSettings':
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj
