from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    price = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, error_messages={'required': 'All fields are required.', 'invalid': 'Price must be a number.'})
    class Meta:
        model = Course
        fields = ['title', 'description', 'price']
        error_messages = {field: {'required': 'All fields are required.'} for field in fields}

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content']

@login_required(login_url='login')
def course_al(request):
    courses = Course.objects.annotate(lesson_count=Count('lessons')).order_by('-created_at')
    query = request.GET.get('q', '').strip()
    if query:
        courses = courses.filter(title__icontains=query)
    return render(request, 'course.html', {'courses': courses, 'query': query, 'course_count': Course.objects.count(), 'lesson_count': Lesson.objects.count()})

@login_required(login_url='login')
def cr_course(request):
    form = CourseForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Курси нав илова шуд.')
        return redirect('course')
    return render(request, 'cr_course.html', {'form': form})

@login_required(login_url='login')
def update_cr(request, id):
    course = get_object_or_404(Course, id=id)
    form = CourseForm(request.POST if request.method == 'POST' else None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Тағйирот нигоҳ дошта шуд.')
        return redirect('course')
    return render(request, 'up_course.html', {'course': course, 'form': form})

@login_required(login_url='login')
def delete_course(request, id):
    course = get_object_or_404(Course, id=id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Курс ҳазф шуд.')
        return redirect('course')
    return render(request, 'delete.html', {'course': course})

@login_required(login_url='login')
def show_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'show_lesson.html', {'course': course, 'lessons': course.lessons.order_by('created_at')})

@login_required(login_url='login')
def cr_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = LessonForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        lesson = form.save(commit=False)
        lesson.course = course
        lesson.save()
        messages.success(request, 'Дарси нав илова шуд.')
        return redirect('show_lesson', course_id=course.id)
    return render(request, 'cr_lesson.html', {'course': course, 'form': form})

@login_required(login_url='login')
def update_lesson(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    form = LessonForm(request.POST if request.method == 'POST' else None, instance=lesson)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Дарс нав карда шуд.')
        return redirect('show_lesson', course_id=lesson.course_id)
    return render(request, 'up_lesson.html', {'lesson': lesson, 'course': lesson.course, 'form': form})


# Keep the authentication routes functional alongside the course workspace.
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


def register(request):
    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('course')
    return render(request, 'register.html', {'form': form})


class ConfirmLogoutView(LogoutView):
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        return render(request, 'logout.html')


login_view = LoginView.as_view(template_name='login.html', next_page='course')
logout_view = ConfirmLogoutView.as_view(next_page='login')
