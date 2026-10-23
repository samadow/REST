from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Course, Lesson


class SiteAccessTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(title='Python', description='Learn', price='10')
        self.lesson = Lesson.objects.create(course=self.course, title='Start', content='Hello')

    def test_every_course_and_lesson_page_requires_login(self):
        pages = [
            reverse('home'), reverse('course'), reverse('cr_course'),
            reverse('up_course', args=[self.course.pk]), reverse('delete_course', args=[self.course.pk]),
            reverse('show_lesson', args=[self.course.pk]), reverse('cr_lesson', args=[self.course.pk]),
            reverse('up_lesson', args=[self.lesson.pk]), reverse('profile'), reverse('password_change'),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertRedirects(response, reverse('login') + '?next=' + page)

    def test_anonymous_post_cannot_create_or_change_content(self):
        create_page = reverse('cr_course')
        response = self.client.post(create_page, {'title': 'Blocked', 'description': 'Should not save', 'price': '1'})
        self.assertRedirects(response, reverse('login') + '?next=' + create_page)
        self.assertFalse(Course.objects.filter(title='Blocked').exists())
        delete_page = reverse('delete_course', args=[self.course.pk])
        self.assertRedirects(self.client.post(delete_page), reverse('login') + '?next=' + delete_page)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())

    def test_login_opens_intended_page_and_logout_closes_access(self):
        user = get_user_model().objects.create_user(username='reader', password='ReaderTestPass985!')
        target = reverse('show_lesson', args=[self.course.pk])
        self.assertRedirects(self.client.get(target), reverse('login') + '?next=' + target)
        self.assertRedirects(self.client.post(reverse('login'), {
            'username': user.username, 'password': 'ReaderTestPass985!', 'next': target,
        }), target)
        self.assertEqual(self.client.get(target).status_code, 200)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))
        self.assertRedirects(self.client.get(target), reverse('login') + '?next=' + target)
