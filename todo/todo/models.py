from django.db import models
from django.utils import timezone


class Todos(models.Model):
    title = models.CharField()
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField()
    createdat = models.DateTimeField(default=timezone.now)
    updatedat = models.DateTimeField(default=timezone.now)


class TodoEvent(models.Model):
    EVENT_TYPES = [
        ("Created", "Created"),
        ("Updated", "Updated"),
        ("Checked", "Checked"),
        ("Unchecked", "Unchecked"),
        ("Deleted", "Deleted"),
    ]
    todo = models.ForeignKey(
        "app.Model", verbose_name=("todoname"), on_delete=models.CASCADE
    )
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(null=True, blank=True)
