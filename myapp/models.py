from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    Role = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('editor', 'editor'),
        ('user', 'user'),
    )

    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(choices=Role,max_length=50,default='user')
    

    def __str__(self):
        return self.username


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='lessons')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments')
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]