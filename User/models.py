from django.db import models
from django.contrib.auth.models import AbstractUser

# User
class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin','SuperAdmin'),
        ('admin','Admin'),
        ('user','User'),
    )

    role = models.CharField(max_length=50,choices=ROLE_CHOICES,default='user')

    def __str__(self):
        return self.username


#Task
class Task(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    )

    title = models.CharField(max_length=250)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Report & work time
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.FloatField(blank=True, null=True)
    worked_days = models.IntegerField(blank=True, null=True)

    # Tracking start & end
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title