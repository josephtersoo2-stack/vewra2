from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.gamification.models import UserProfile, Badge, UserBadge
from apps.tasks.models import VideoTask, WatchSession
from apps.wallet.models import Wallet, WalletTransaction
from apps.xp_badges.models import XPSettings
from apps.xp_badges.services.xp_engine import add_xp
from apps.xp_badges.services.badge_engine import evaluate_all_badges

User = get_user_model()


class XPEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='xp_hero', email='hero@example.com', password='password123')

    def test_xp_settings_singleton(self):
        s1 = XPSettings.load()
        self.assertEqual(s1.xp_per_minute_watched, 10)
        self.assertEqual(s1.xp_for_completing_task, 50)
        self.assertEqual(s1.xp_for_daily_streak, 15)
        self.assertEqual(s1.xp_for_daily_spin, 15)
        self.assertEqual(s1.xp_for_referral, 100)

        # Update and ensure singleton
        s1.xp_for_completing_task = 75
        s1.save()

        s2 = XPSettings.objects.create(xp_for_completing_task=99)
        self.assertEqual(XPSettings.objects.count(), 1)
        self.assertEqual(XPSettings.load().xp_for_completing_task, 99)

    def test_add_xp_and_level_up(self):
        # Level 1 needs 20 XP to reach Level 2 (1² * 20 = 20)
        res1 = add_xp(self.user, 15, source='watch_minute')
        self.assertEqual(res1['total_xp'], 15)
        self.assertEqual(res1['new_level'], 1)
        self.assertFalse(res1['leveled_up'])

        # Add 10 XP -> total 25 XP >= 20 -> Leveled up to Level 2
        res2 = add_xp(self.user, 10, source='task_complete')
        self.assertEqual(res2['total_xp'], 25)
        self.assertEqual(res2['new_level'], 2)
        self.assertTrue(res2['leveled_up'])

        # Level 2 needs 80 XP (2² * 20 = 80) to reach Level 3
        # Add 60 XP -> total 85 XP >= 80 -> Leveled up to Level 3
        res3 = add_xp(self.user, 60, source='quest')
        self.assertEqual(res3['total_xp'], 85)
        self.assertEqual(res3['new_level'], 3)
        self.assertTrue(res3['leveled_up'])

    def test_multi_level_jump(self):
        # Huge XP boost: 550 XP -> L6
        res = add_xp(self.user, 550, source='referral_bonus')
        self.assertEqual(res['total_xp'], 550)
        self.assertEqual(res['new_level'], 6)
        self.assertTrue(res['leveled_up'])

    def test_badge_engine_awards_tiers(self):
        # 1. Create a watch badge with thresholds: Bronze=10 min, Silver=50 min, Gold=250 min, Diamond=1000 min
        watch_badge = Badge.objects.create(
            key='couch_potato',
            name='Couch Potato',
            description='Total watch time in minutes on Vewra.',
            category='watch',
            target_bronze=10.0,
            target_silver=50.0,
            target_gold=250.0,
            target_diamond=1000.0,
        )

        task_badge = Badge.objects.create(
            key='getting_started',
            name='Task Collector',
            description='Completed video tasks.',
            category='onboarding',
            target_bronze=1.0,
            target_silver=5.0,
            target_gold=25.0,
            target_diamond=100.0,
        )

        earning_badge = Badge.objects.create(
            key='coin_collector',
            name='Coin Collector',
            description='Total coins earned.',
            category='earning',
            target_bronze=50.0,
            target_silver=200.0,
            target_gold=1000.0,
            target_diamond=5000.0,
        )

        # 2. Generate fake WatchSession data: 100 minutes watched (6000 seconds) across 2 completed tasks
        task1 = VideoTask.objects.create(
            video_id='vid_01',
            youtube_url='https://youtu.be/vid_01',
            title='Task 1',
            keywords=['music'],
        )
        task2 = VideoTask.objects.create(
            video_id='vid_02',
            youtube_url='https://youtu.be/vid_02',
            title='Task 2',
            keywords=['gaming'],
        )

        WatchSession.objects.create(
            user=self.user,
            video_task=task1,
            total_watched_seconds=3600.0,  # 60 minutes
            is_completed=True,
        )
        WatchSession.objects.create(
            user=self.user,
            video_task=task2,
            total_watched_seconds=2400.0,  # 40 minutes (Total = 100 min)
            is_completed=True,
        )

        # 3. Create wallet transactions (e.g. 150 coins)
        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        wallet.balance = Decimal('150.00')
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=Decimal('150.00'),
            balance_after=Decimal('150.00'),
            transaction_type='watch_reward',
            description='Task watch reward',
        )

        # 4. Run badge evaluation
        summary = evaluate_all_badges(self.user)

        self.assertEqual(summary['evaluated_count'], 3)
        self.assertEqual(summary['unlocked_count'], 3)
        self.assertIn('Couch Potato', summary['newly_unlocked'])
        self.assertIn('Task Collector', summary['newly_unlocked'])
        self.assertIn('Coin Collector', summary['newly_unlocked'])

        # 5. Assert tiers
        # Watch badge: 100 minutes >= 50 (Silver) but < 250 (Gold) -> Tier 'silver'
        user_watch_badge = UserBadge.objects.get(user=self.user, badge=watch_badge)
        self.assertTrue(user_watch_badge.is_unlocked)
        self.assertEqual(user_watch_badge.tier, 'silver')
        self.assertEqual(user_watch_badge.progress_current, 100.0)
        self.assertEqual(user_watch_badge.progress_target, 250.0)
        self.assertIsNotNone(user_watch_badge.awarded_at)

        # Task badge: 2 completed >= 1 (Bronze) but < 5 (Silver) -> Tier 'bronze'
        user_task_badge = UserBadge.objects.get(user=self.user, badge=task_badge)
        self.assertTrue(user_task_badge.is_unlocked)
        self.assertEqual(user_task_badge.tier, 'bronze')
        self.assertEqual(user_task_badge.progress_current, 2.0)

        # Earning badge: 150 coins >= 50 (Bronze) but < 200 (Silver) -> Tier 'bronze'
        user_earning_badge = UserBadge.objects.get(user=self.user, badge=earning_badge)
        self.assertTrue(user_earning_badge.is_unlocked)
        self.assertEqual(user_earning_badge.tier, 'bronze')
        self.assertEqual(user_earning_badge.progress_current, 150.0)
