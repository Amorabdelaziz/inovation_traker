from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Idea, UserProfile


class LogoutFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass1234')

    def test_authenticated_user_can_logout(self):
        self.client.login(username='tester', password='pass1234')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_is_idempotent(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))


class LoginFlowTests(TestCase):
    def setUp(self):
        self.credentials = {'username': 'alice', 'password': 's3cretpass'}
        User.objects.create_user(**self.credentials)

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ideas/login.html')
        self.assertContains(response, 'Login')

    def test_valid_login_redirects_home(self):
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse('login'), {'username': 'alice', 'password': 'wrong'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertNotIn('_auth_user_id', self.client.session)


class RolePermissionsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Tech')
        self.submitter = User.objects.create_user(username='submitter', password='pass1234')
        self.idea = Idea.objects.create(
            title='Test Idea',
            description='Desc',
            category=self.category,
            submitter=self.submitter,
        )

    def test_submitter_cannot_access_review_dashboard(self):
        self.client.login(username='submitter', password='pass1234')
        response = self.client.get(reverse('review_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('home'), response.url)

    def test_reviewer_can_update_status(self):
        reviewer = User.objects.create_user(username='reviewer', password='pass1234')
        reviewer_profile = reviewer.profile
        reviewer_profile.role = UserProfile.ROLE_REVIEWER
        reviewer_profile.save()
        self.client.login(username='reviewer', password='pass1234')
        response = self.client.post(
            reverse('update_idea_status', args=[self.idea.pk]),
            {'status': 'approved'},
        )
        self.assertEqual(response.status_code, 302)
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.status, 'approved')
