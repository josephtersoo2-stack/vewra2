from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.gamification.models import UserProfile
from apps.xp_badges.models import XPSettings
from apps.xp_badges.services.xp_engine import add_xp

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
        # Huge XP boost: 550 XP
        # L1: >= 20 -> L2
        # L2: >= 80 -> L3
        # L3: >= 180 -> L4
        # L4: >= 320 -> L5
        # L5: >= 500 -> L6
        res = add_xp(self.user, 550, source='referral_bonus')
        self.assertEqual(res['total_xp'], 550)
        self.assertEqual(res['new_level'], 6)
        self.assertTrue(res['leveled_up'])
