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


# -----------------------------------------------------------------------
# Phase 1.4: Mobile API Endpoint Tests
# -----------------------------------------------------------------------

from django.urls import reverse
from rest_framework.test import APIClient


class UserProfileXPAPITests(TestCase):
    """Tests for GET /api/v1/xp-badges/profile/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='api_hero', email='api@example.com', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        # Give the user some XP so there's real data to assert on
        add_xp(self.user, 50, source='test_setup')

    def test_requires_authentication(self):
        anon_client = APIClient()
        response = anon_client.get(reverse('xp-profile'))
        self.assertEqual(response.status_code, 401)

    def test_returns_xp_profile_for_authenticated_user(self):
        response = self.client.get(reverse('xp-profile'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['username'], 'api_hero')
        self.assertEqual(data['xp'], 50)
        self.assertGreaterEqual(data['level'], 1)
        self.assertIn('xp_for_next_level', data)
        self.assertIn('xp_progress_percent', data)
        self.assertIn('streak_freeze_count', data)
        self.assertIn('showcase_badges', data)
        self.assertIsInstance(data['showcase_badges'], list)

    def test_xp_progress_percent_is_within_range(self):
        response = self.client.get(reverse('xp-profile'))
        self.assertEqual(response.status_code, 200)
        pct = response.json()['xp_progress_percent']
        self.assertGreaterEqual(pct, 0.0)
        self.assertLessEqual(pct, 100.0)


class UserBadgeListAPITests(TestCase):
    """Tests for GET /api/v1/xp-badges/badges/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='badge_hero', email='badge@example.com', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create a couple of badges for the catalog
        self.badge_watch = Badge.objects.create(
            key='couch_potato', name='Couch Potato',
            description='10 hours total watch time', category='watch',
            target_bronze=10, target_silver=50, target_gold=250, target_diamond=1000,
        )
        self.badge_earning = Badge.objects.create(
            key='coin_collector_api', name='Coin Collector',
            description='Earn 1000 coins', category='earning',
            target_bronze=1000, target_silver=10000, target_gold=50000, target_diamond=1000000,
        )

    def test_requires_authentication(self):
        anon_client = APIClient()
        response = anon_client.get(reverse('user-badges'))
        self.assertEqual(response.status_code, 401)

    def test_returns_full_badge_catalog(self):
        response = self.client.get(reverse('user-badges'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('count', data)
        self.assertIn('badges', data)
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['badges']), 2)

    def test_badge_has_all_required_fields(self):
        response = self.client.get(reverse('user-badges'))
        badge_data = response.json()['badges'][0]

        for field in ['id', 'key', 'name', 'description', 'category',
                      'icon_url', 'is_hidden', 'target_bronze', 'target_silver',
                      'target_gold', 'target_diamond', 'tier', 'progress_current',
                      'progress_target', 'is_unlocked', 'awarded_at']:
            self.assertIn(field, badge_data, msg=f"Missing field: {field}")

    def test_locked_badges_default_to_none_tier(self):
        """Badges with no UserBadge record must appear as tier='none', is_unlocked=False."""
        response = self.client.get(reverse('user-badges'))
        badges = response.json()['badges']
        for b in badges:
            self.assertEqual(b['tier'], 'none')
            self.assertFalse(b['is_unlocked'])
            self.assertIsNone(b['awarded_at'])

    def test_unlocked_badge_shows_correct_tier(self):
        """After creating a UserBadge record, the badge list must reflect the tier."""
        UserBadge.objects.create(
            user=self.user, badge=self.badge_watch,
            tier='bronze', progress_current=12.0, progress_target=10.0,
            is_unlocked=True,
        )
        response = self.client.get(reverse('user-badges'))
        badges = {b['key']: b for b in response.json()['badges']}

        self.assertEqual(badges['couch_potato']['tier'], 'bronze')
        self.assertTrue(badges['couch_potato']['is_unlocked'])
        self.assertEqual(badges['couch_potato']['progress_current'], 12.0)

        # The earning badge should still be locked
        self.assertEqual(badges['coin_collector_api']['tier'], 'none')
        self.assertFalse(badges['coin_collector_api']['is_unlocked'])
