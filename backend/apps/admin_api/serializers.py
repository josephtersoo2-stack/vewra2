from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.tasks.models import VideoTask, WatchSession
from apps.ai_service.models import AISettings
from apps.gamification.models import StreakSettings, SpinWheelSegment, Badge
from apps.xp_badges.models import XPSettings
from apps.wallet.models import Wallet, WalletTransaction

User = get_user_model()


class AdminVideoTaskSerializer(serializers.ModelSerializer):
    search_keywords_list = serializers.ListField(
        child=serializers.CharField(),
        source='keywords',
        read_only=True
    )
    completion_count = serializers.SerializerMethodField()
    active_viewers_count = serializers.SerializerMethodField()
    reward_summary = serializers.CharField(read_only=True)

    class Meta:
        model = VideoTask
        fields = [
            'id', 'title', 'youtube_url', 'video_id', 'thumbnail_url',
            'reward_type', 'reward_config', 'keywords', 'search_keywords_list',
            'reward_summary', 'is_active', 'created_at', 'updated_at',
            'completion_count', 'active_viewers_count'
        ]
        read_only_fields = ['id', 'video_id', 'thumbnail_url', 'created_at', 'updated_at']

    def get_completion_count(self, obj) -> int:
        return obj.sessions.filter(is_completed=True).count()

    def get_active_viewers_count(self, obj) -> int:
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(seconds=10)
        return obj.sessions.filter(last_watched_at__gte=cutoff, is_completed=False).count()


class AdminWatchSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    video_title = serializers.CharField(source='video_task.title', read_only=True)
    video_id = serializers.CharField(source='video_task.video_id', read_only=True)

    class Meta:
        model = WatchSession
        fields = [
            'id', 'user', 'username', 'video_task', 'video_title', 'video_id',
            'total_watched_seconds', 'current_position',
            'is_completed', 'last_watched_at',
            'created_at', 'updated_at'
        ]


class AdminUserSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(source='wallet.balance', max_digits=12, decimal_places=2, read_only=True)
    tasks_completed_count = serializers.SerializerMethodField()
    total_watch_seconds = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'is_staff', 'date_joined',
            'wallet_balance', 'tasks_completed_count', 'total_watch_seconds'
        ]

    def get_tasks_completed_count(self, obj) -> int:
        return obj.watch_sessions.filter(is_completed=True).count()

    def get_total_watch_seconds(self, obj) -> float:
        from django.db.models import Sum
        return obj.watch_sessions.aggregate(Sum('total_watched_seconds'))['total_watched_seconds__sum'] or 0.0


class AdminUserBalanceAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    transaction_type = serializers.ChoiceField(
        choices=['admin_credit', 'admin_debit', 'reward', 'penalty'],
        default='admin_credit'
    )
    description = serializers.CharField(required=False, allow_blank=True, default="Admin balance adjustment")


class AdminWalletTransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='wallet.user.username', read_only=True)
    email = serializers.CharField(source='wallet.user.email', read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'username', 'email', 'transaction_type', 'amount',
            'balance_after', 'reference_id', 'description', 'created_at'
        ]


class AdminAISettingsSerializer(serializers.ModelSerializer):
    has_gemini_key = serializers.SerializerMethodField()
    has_openrouter_key = serializers.SerializerMethodField()

    class Meta:
        model = AISettings
        fields = [
            'id', 'active_provider', 'gemini_api_key', 'openrouter_api_key',
            'has_gemini_key', 'has_openrouter_key',
            'selected_model', 'custom_system_prompt', 'is_active', 'updated_at'
        ]

    def get_has_gemini_key(self, obj) -> bool:
        return bool(obj.get_effective_gemini_key())

    def get_has_openrouter_key(self, obj) -> bool:
        return bool(obj.get_effective_openrouter_key())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Return decrypted keys to authenticated admin so they can see and edit them in UI
        data['gemini_api_key'] = instance.get_effective_gemini_key()
        data['openrouter_api_key'] = instance.get_effective_openrouter_key()
        return data


class AdminTestPromptSerializer(serializers.Serializer):
    youtube_url = serializers.CharField(required=True)
    provider = serializers.ChoiceField(choices=['gemini', 'openrouter'], required=False)
    model_name = serializers.CharField(required=False, allow_blank=True)
    custom_prompt = serializers.CharField(required=False, allow_blank=True)


class AdminStreakSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakSettings
        fields = [
            'id',
            'day_1_coins',
            'day_2_coins',
            'day_3_coins',
            'day_4_coins',
            'day_5_coins',
            'day_6_coins',
            'day_7_coins',
            'mystery_box_day',
            'streak_reset_days',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class AdminSpinWheelSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinWheelSegment
        fields = [
            'id',
            'label',
            'reward_coins',
            'weight',
            'color',
            'is_active',
            'order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminXPSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPSettings
        fields = [
            'id',
            'xp_per_minute_watched',
            'xp_for_completing_task',
            'xp_for_daily_streak',
            'xp_for_daily_spin',
            'xp_for_referral',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class AdminBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            'id',
            'key',
            'name',
            'description',
            'category',
            'icon_url',
            'is_hidden',
            'target_bronze',
            'target_silver',
            'target_gold',
            'target_diamond',
        ]
        read_only_fields = ['id']
