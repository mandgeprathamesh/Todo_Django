from django.db import models

# from django.db import transaction

from core.constants import TASK_EVENT_TYPE


# def create():
#     with transaction.atomic():
#         task = Task.create(name="Task 1", description="Description 1")
#         TaskHistory.create(
#             task=task,
#             event_type="Created",
#             metadata="Created Task 1",
#         )


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create(cls, name, description=None):
        return cls.objects.create(
            name=name,
            description=description,
        )


class TaskHistory(models.Model):
    task = models.ForeignKey(
        to=Task,
        on_delete=models.CASCADE,
    )
    event_type = models.CharField(max_length=10, choices=TASK_EVENT_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.TextField(blank=True, null=True)

    @classmethod
    def create(cls, task, event_type, metadata=None):
        return cls.objects.create(
            task=task,
            event_type=event_type,
            metadata=metadata,
        )
