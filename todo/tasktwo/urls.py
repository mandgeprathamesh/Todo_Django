"""
URL configuration for todo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.todo_list, name="todo_list"),
    path("todos/", views.create_todo, name="create_todo"),
    path("todos/<int:todo_id>/", views.update_todo, name="update_todo"),
    path("todos/<int:todo_id>/toggle/", views.toggle_todo, name="toggle_todo"),
    path("todos/<int:todo_id>/delete/", views.delete_todo, name="delete_todo"),
    path("todos/<int:todo_id>/history/", views.todo_history, 
         name="todo_history"),
]
