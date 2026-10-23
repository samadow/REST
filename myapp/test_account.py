from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='learner', password='CurrentPass981!')
        self.other = get_user_model().objects.create_user(username='other', first_name='Unchanged')

    def test_anonymous_users_are_redirected_to_login(self):
        for name in ('profile', 'password_change'):
            response = self.client.get(reverse(name))
            self.assertRedirects(response, reverse('login') + '?next=' + reverse(name))

    def test_profile_updates_only_current_users_allowed_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile'), {'first_name': 'Ali', 'last_name': 'Sharif', 'email': 'ali@example.com', 'role': 'admin', 'is_staff': 'true', 'is_superuser': 'true', 'id': self.other.pk})
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Ali')
        self.assertEqual(self.user.email, 'ali@example.com')
        self.assertEqual(self.user.role, 'user')
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.other.first_name, 'Unchanged')

    def test_invalid_email_does_not_save_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile'), {'first_name': 'Invalid', 'email': 'not-an-email'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, '')

    def test_password_change_checks_old_password_and_keeps_session(self):
        self.client.force_login(self.user)
        self.assertTemplateUsed(self.client.get(reverse('password_change')), 'password_change.html')
        data = {'old_password': 'wrong', 'new_password1': 'NewSecurePass729!', 'new_password2': 'NewSecurePass729!'}
        response = self.client.post(reverse('password_change'), data)
        self.assertIn('old_password', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('CurrentPass981!'))
        data['old_password'] = 'CurrentPass981!'
        self.assertRedirects(self.client.post(reverse('password_change'), data), reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass729!'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_password_confirmation_must_match(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('password_change'), {'old_password': 'CurrentPass981!', 'new_password1': 'NewSecurePass729!', 'new_password2': 'DifferentPass729!'})
        self.assertTrue(response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('CurrentPass981!'))
