from django.test import TestCase
from django.urls import reverse

from .models import Course


class CourseViewsTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username='course_tester', password='CourseTestPass985!')
        self.client.force_login(user)

    def test_course_list_page_opens(self):
        response = self.client.get(reverse('course'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course.html')

    def test_create_course_page_opens(self):
        response = self.client.get(reverse('cr_course'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cr_course.html')

    def test_course_can_be_created(self):
        response = self.client.post(
            reverse('cr_course'),
            {
                'title': 'Django course',
                'description': 'Learn Django',
                'price': '99.99',
            },
        )

        self.assertRedirects(response, reverse('course'))
        self.assertTrue(
            Course.objects.filter(
                title='Django course',
                description='Learn Django',
                price='99.99',
            ).exists()
        )

    def test_invalid_course_is_not_created(self):
        response = self.client.post(
            reverse('cr_course'),
            {'title': '', 'description': '', 'price': 'not-a-number'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Course.objects.exists())
        self.assertContains(response, 'All fields are required.')

    def test_non_numeric_price_is_rejected(self):
        response = self.client.post(
            reverse('cr_course'),
            {
                'title': 'Django course',
                'description': 'Learn Django',
                'price': 'not-a-number',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Course.objects.exists())
        self.assertContains(response, 'Price must be a number.')

    def test_update_course_page_opens(self):
        course = Course.objects.create(
            title='Old title',
            description='Old description',
            price='10.00',
        )

        response = self.client.get(reverse('up_course', args=[course.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Old title')

    def test_course_can_be_updated(self):
        course = Course.objects.create(
            title='Old title',
            description='Old description',
            price='10.00',
        )

        response = self.client.post(
            reverse('up_course', args=[course.id]),
            {
                'title': 'New title',
                'description': 'New description',
                'price': '25.50',
            },
        )
        course.refresh_from_db()

        self.assertRedirects(response, reverse('course'))
        self.assertEqual(course.title, 'New title')
        self.assertEqual(course.description, 'New description')
        self.assertEqual(str(course.price), '25.50')

    def test_delete_course_page_opens(self):
        course = Course.objects.create(
            title='Django course',
            description='Learn Django',
            price='99.99',
        )

        response = self.client.get(reverse('delete_course', args=[course.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django course')

    def test_course_can_be_deleted(self):
        course = Course.objects.create(
            title='Django course',
            description='Learn Django',
            price='99.99',
        )

        response = self.client.post(reverse('delete_course', args=[course.id]))

        self.assertRedirects(response, reverse('course'))
        self.assertFalse(Course.objects.filter(id=course.id).exists())


class LessonWorkflowTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username='lesson_tester', password='LessonTestPass985!')
        self.client.force_login(user)

        from .models import Lesson
        self.course = Course.objects.create(title='Python', description='Practical course', price='50')
        self.other = Course.objects.create(title='Design', description='Visual design', price='20')
        self.lesson = Lesson.objects.create(course=self.course, title='Introduction', content='First lesson')
        Lesson.objects.create(course=self.other, title='Other course lesson', content='Hidden here')

    def test_lessons_are_scoped_to_the_course(self):
        response = self.client.get(reverse('show_lesson', args=[self.course.id]))
        self.assertContains(response, 'Introduction')
        self.assertNotContains(response, 'Other course lesson')

    def test_lesson_create_and_update_redirect_to_parent(self):
        from .models import Lesson
        response = self.client.post(reverse('cr_lesson', args=[self.course.id]), {'title': 'Variables', 'content': 'Names and values'})
        self.assertRedirects(response, reverse('show_lesson', args=[self.course.id]))
        lesson = Lesson.objects.get(title='Variables')
        response = self.client.post(reverse('up_lesson', args=[lesson.id]), {'title': 'New variables', 'content': 'Updated content'})
        self.assertRedirects(response, reverse('show_lesson', args=[self.course.id]))
        lesson.refresh_from_db()
        self.assertEqual(lesson.content, 'Updated content')

    def test_course_delete_does_not_delete_unrelated_lessons(self):
        from .models import Lesson
        response = self.client.post(reverse('delete_course', args=[self.course.id]))
        self.assertRedirects(response, reverse('course'))
        self.assertFalse(Lesson.objects.filter(course_id=self.course.id).exists())
        self.assertTrue(Lesson.objects.filter(course=self.other).exists())

    def test_course_search_and_empty_results(self):
        response = self.client.get(reverse('course'), {'q': 'Python'})
        self.assertContains(response, 'Python')
        self.assertNotContains(response, 'Visual design')
        response = self.client.get(reverse('course'), {'q': 'missing-course'})
        self.assertEqual(list(response.context['courses']), [])

    def test_editor_pages_and_missing_objects(self):
        for name, object_id in [('cr_lesson', self.course.id), ('up_lesson', self.lesson.id)]:
            self.assertEqual(self.client.get(reverse(name, args=[object_id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('show_lesson', args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_invalid_price_preserves_existing_course(self):
        response = self.client.post(reverse('up_course', args=[self.course.id]), {'title': 'Changed', 'description': 'Changed', 'price': '-1'})
        self.assertEqual(response.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Python')


class AuthenticationRouteTests(TestCase):
    def test_authentication_forms_open(self):
        for name in ('register', 'login'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_registration_and_logout(self):
        from django.contrib.auth import get_user_model
        response = self.client.post(reverse('register'), {'username': 'testlearner', 'password1': 'LongTestPass492!', 'password2': 'LongTestPass492!'})
        self.assertRedirects(response, reverse('course'))
        self.assertEqual(get_user_model().objects.get(username='testlearner').role, 'user')
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 200)
        response = self.client.post(reverse('login'), {'username': 'testlearner', 'password': 'LongTestPass492!'})
        self.assertRedirects(response, reverse('course'))


    def test_logout_confirmation_preserves_session_until_post(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username='confirmuser', password='TestPassword472!')
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertTemplateUsed(response, 'logout.html')
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_auth_templates_and_invalid_login(self):
        for name in ('register', 'login', 'logout'):
            self.assertTemplateUsed(self.client.get(reverse(name)), name + '.html')
        response = self.client.post(reverse('login'), {'username': 'missing', 'password': 'incorrect'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_logout_requires_csrf_token(self):
        from django.test import Client
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse('logout')).status_code, 403)
