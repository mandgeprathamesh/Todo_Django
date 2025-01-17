from django.urls import path

from tasks import views


"""
www.example.com/tasks/256?date_format=utc&time_format=24h

Do error handling in all AP
ModuleNotFoundError: No module named 'todo.tasks'Is
Show loading indicator
handle empty data on frontend

- get all tasks (paginated)
    - page = 1
    - page_size = 10

- Get all tasks: GET /tasks -> List[Task] (200)
- Create single task: POST /tasks -> Task (201)

- Get single task: GET /tasks/456 -> Task (200)
- PATCH /tasks/456 {"completed": true} ->  Task (200)
- DELETE /tasks/456 -> Task (200)

- GET /tasks/456/history -> List[TaskHistory] (200)



client -> jS validation -> API call -> view -> serializer


"""

urlpatterns = [
    path(
        "",
        views.LandingPageView.as_view(),
        name="landing_page",
    ),
    path(
        "tasks/", views.TaskListCreateView.as_view(), name="task_list_create"
    ),  # GET and POST
    path(
        "tasks/<int:task_id>/",
        views.TaskDetailView.as_view(),
        name="task_detail",
    ),  # GET, PATCH, DELETE, PUT
    path(
        "tasks/<int:task_id>/history/",
        views.TaskHistoryView.as_view(),
        name="task_history",
    ),  # GET history
    path(
        "tasks/edit/<int:task_id>/",
        views.TodoFormView.as_view(),
        name="task_edit",
    ),
]
