from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class FormInputs(HTMLParser):
    def __init__(self, response):
        super().__init__()
        self.values = {}
        self.action = None
        self.feed(response.content.decode())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form' and attrs.get('method', '').lower() == 'post':
            self.action = attrs.get('action')
        if tag == 'input' and attrs.get('name'):
            self.values[attrs['name']] = attrs.get('value', '')

    def filled(self, values):
        return {name: values.get(name, value) for name, value in self.values.items()}


class AuthenticationHTMLTests(TestCase):
    def test_rendered_registration_logout_and_login_forms_work_with_csrf(self):
        client = Client(enforce_csrf_checks=True)
        credentials = {'username': 'htmllearner', 'password1': 'StrongTestPass487!', 'password2': 'StrongTestPass487!'}
        form = FormInputs(client.get(reverse('register')))
        response = client.post(form.action, form.filled(credentials))
        self.assertRedirects(response, reverse('course'))
        user = get_user_model().objects.get(username='htmllearner')
        self.assertTrue(user.check_password(credentials['password1']))
        self.assertIn('_auth_user_id', client.session)

        form = FormInputs(client.get(reverse('logout')))
        self.assertIn('_auth_user_id', client.session)
        self.assertRedirects(client.post(form.action, form.values), reverse('login'))
        self.assertNotIn('_auth_user_id', client.session)

        form = FormInputs(client.get(reverse('login'), {'next': reverse('profile')}))
        data = form.filled({'username': 'htmllearner', 'password': credentials['password1']})
        self.assertRedirects(client.post(form.action, data), reverse('profile'))
        self.assertIn('_auth_user_id', client.session)

    def test_registration_displays_password_mismatch(self):
        response = self.client.post(reverse('register'), {'username': 'mismatch', 'password1': 'StrongTestPass487!', 'password2': 'DifferentTestPass598!'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password2-errors')
        self.assertContains(response, 'value="mismatch"')
        self.assertFalse(get_user_model().objects.filter(username='mismatch').exists())

    def test_login_errors_are_visible_and_keep_username(self):
        response = self.client.post(reverse('login'), {'username': 'unknown', 'password': 'WrongTestPass487!'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')
        self.assertContains(response, 'value="unknown"')
        self.assertNotContains(response, 'WrongTestPass487!')
