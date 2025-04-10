from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardTests(TestCase):
    """
    Tests for the dashboard and overall site navigation.
    """

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpassword',
            is_staff=True
        )

    def test_anonymous_redirect(self):
        """Test that anonymous users are redirected to the landing page."""
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        # Check if redirected to landing
        self.assertIn('/landing/', response.redirect_chain[0][0])

    def test_authenticated_redirect(self):
        """Test that authenticated users are redirected to the dashboard."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        # Check if redirected to dashboard
        self.assertIn('/dashboard/', response.redirect_chain[0][0])

    def test_dashboard_access(self):
        """Test that only authenticated users can access the dashboard."""
        # Anonymous user should be redirected
        response = self.client.get(reverse('dashboard:home'), follow=True)
        self.assertIn('/accounts/login/', response.redirect_chain[0][0])

        # Authenticated user should access dashboard
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_major_feature_links(self):
        """Test that all major features are accessible from the dashboard."""
        self.client.login(username='testuser', password='testpassword')

        # Test dashboard itself
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

        # Test character list
        response = self.client.get(reverse('characters:character_list'))
        self.assertEqual(response.status_code, 200)

        # Test chat rooms - updated the URL name
        response = self.client.get(reverse('messages:room_list'))
        self.assertEqual(response.status_code, 200)

        # Test friends
        response = self.client.get(reverse('accounts:friend_list'))
        self.assertEqual(response.status_code, 200)

        # Test recommendations
        response = self.client.get(reverse('recommendations:character_recommendations'))
        self.assertEqual(response.status_code, 200)

        # Test notifications - update to use notification_list
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.status_code, 200)

    def test_moderation_access(self):
        """Test that only staff users can access moderation."""
        # Regular user should be denied
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('moderation:dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Staff user should be allowed
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(reverse('moderation:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dating_feature_links(self):
        """Test that all dating features are accessible."""
        self.client.login(username='testuser', password='testpassword')

        # Test browse profiles
        response = self.client.get(reverse('accounts:browse_dating_profiles'))
        self.assertEqual(response.status_code, 200)

        # Test matches view
        response = self.client.get(reverse('accounts:view_matches'))
        self.assertEqual(response.status_code, 200)

        # Test received likes
        response = self.client.get(reverse('accounts:received_likes'))
        self.assertEqual(response.status_code, 200)

        # Test manage interests
        response = self.client.get(reverse('accounts:manage_interests'))
        self.assertEqual(response.status_code, 200)
