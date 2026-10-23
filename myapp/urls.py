from django.urls import path
from . import views, account
urlpatterns = [
    path('profile/', account.profile, name='profile'),
    path('password/change/', account.password_change, name='password_change'),
    path('', views.course_al, name='home'),
    path('course/', views.course_al, name='course'),
    path('cr_course/', views.cr_course, name='cr_course'),
    path('up_course/<int:id>/', views.update_cr, name='up_course'),
    path('delete_course/<int:id>/', views.delete_course, name='delete_course'),
    path('cr_lesson/<int:course_id>/lesson/create/', views.cr_lesson, name='cr_lesson'),
    path('show_lesson/<int:course_id>/lessons/', views.show_lesson, name='show_lesson'),
    path('up_lesson/<int:id>/', views.update_lesson, name='up_lesson'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
