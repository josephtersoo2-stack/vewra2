"""
Phase 1.5 (Chunk 1): Tests for mobile gamification API endpoints.
Covers ClaimStreakView, SpinWheelView, and GetSpinSegmentsView.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.gamification.models import SpinWheelSegment

User = get_user_model()


class ClaimStreakViewTests(TestCase):
    """Tests for POST /api/v1/gamification/streak/claim/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='streak_mobile', email='streak@mobile.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('mobile_streak_claim')

    def test_requires_authentication(self):
        anon = APIClient()
        response = anon.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_claim_streak_returns_200_and_coins(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Must include core streak fields
        self.assertIn('already_claimed', data)
        self.assertIn('streak_count', data)
        self.assertIn('coins_awarded', data)
        self.assertIn('streak_day', data)
        self.assertFalse(data['already_claimed'])
        self.assertGreater(data['coins_awarded'], 0)

    def test_claim_streak_includes_xp_and_badge_info(self):
        """The streak claim must include XP and badge data from the integration hook."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('xp_earned', data)
        self.assertIn('level_info', data)
        self.assertIn('badge_info', data)

    def test_second_claim_same_day_returns_already_claimed(self):
        """Claiming twice in the same day must return already_claimed=True."""
        # First claim
        r1 = self.client.post(self.url)
        self.assertEqual(r1.status_code, 200)
        self.assertFalse(r1.json()['already_claimed'])

        # Second claim (same day)
        r2 = self.client.post(self.url)
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()['already_claimed'])
        self.assertEqual(r2.json()['coins_awarded'], 0)


class StreakStatusViewTests(TestCase):
    """Tests for GET /api/v1/gamification/streak/status/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='streak_status_user', email='ss@mobile.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('mobile_streak_status')

    def test_requires_authentication(self):
        anon = APIClient()
        response = anon.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_returns_streak_status_with_calendar(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('streak_count', data)
        self.assertIn('is_claimed_today', data)
        self.assertIn('calendar', data)
        self.assertEqual(len(data['calendar']), 7)

        # Each calendar entry has required keys
        day = data['calendar'][0]
        for field in ['day', 'coins', 'has_mystery_box', 'is_claimed', 'is_current']:
            self.assertIn(field, day, msg=f"Missing calendar field: {field}")


class SpinWheelViewTests(TestCase):
    """Tests for POST /api/v1/gamification/spin/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='spin_mobile', email='spin@mobile.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('mobile_spin')

    def test_requires_authentication(self):
        anon = APIClient()
        response = anon.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_spin_returns_200_and_segment_won(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('success', data)
        self.assertIn('already_spun', data)
        self.assertTrue(data['success'])
        self.assertFalse(data['already_spun'])
        self.assertIn('coins_won', data)
        self.assertIn('segment_won', data)
        self.assertIn('wallet_balance', data)
        self.assertGreater(data['coins_won'], 0)

    def test_spin_includes_xp_and_badge_info(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('xp_earned', data)
        self.assertIn('level_info', data)
        self.assertIn('badge_info', data)

    def test_second_spin_same_day_returns_already_spun(self):
        """A second spin on the same day must return already_spun=True."""
        r1 = self.client.post(self.url)
        self.assertEqual(r1.status_code, 200)
        self.assertFalse(r1.json()['already_spun'])

        r2 = self.client.post(self.url)
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()['already_spun'])
        # success must be False on second attempt
        self.assertFalse(r2.json()['success'])


class GetSpinSegmentsViewTests(TestCase):
    """Tests for GET /api/v1/gamification/spin/segments/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='segments_user', email='seg@mobile.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('mobile_spin_segments')

    def test_requires_authentication(self):
        anon = APIClient()
        response = anon.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_returns_can_spin_and_segments(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('can_spin', data)
        self.assertIn('segments', data)
        self.assertTrue(data['can_spin'])  # User hasn't spun today
        # Segments should be auto-seeded (default 12)
        self.assertGreater(len(data['segments']), 0)

    def test_segment_has_required_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        segments = response.json()['segments']
        self.assertGreater(len(segments), 0)

        seg = segments[0]
        for field in ['id', 'label', 'reward_coins', 'weight', 'color', 'order']:
            self.assertIn(field, seg, msg=f"Missing segment field: {field}")

    def test_can_spin_false_after_spinning(self):
        """After a successful spin, can_spin should return False."""
        spin_url = reverse('mobile_spin')
        spin_res = self.client.post(spin_url)
        self.assertTrue(spin_res.json()['success'])

        # Now check segments status
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['can_spin'])
