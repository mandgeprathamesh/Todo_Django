from django.contrib import admin
from .models import TodoEvent, Todos

# Register your models here.
admin.site.register(TodoEvent)
admin.site.register(Todos)
