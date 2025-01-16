from django.contrib import admin
from tasks.models import Task, TaskHistory

# Register your models here.
admin.site.register(TaskHistory)
admin.site.register(Task)
