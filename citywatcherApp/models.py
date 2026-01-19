from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='reports/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title