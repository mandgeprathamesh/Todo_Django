from django.http import JsonResponse
from .models import TodoEvent, Todos


def create_todo(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        todo = Todos.objects.create(title=title, description=description)
        print(todo)
        TodoEvent.objects.create(
            todo=todo, event_type="Created", details=(
                "Created Todo: {todo.title}")
        )

        return JsonResponse(
            {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "created_at": todo.created_at,
                "updated_at": todo.updated_at,
            },
            status=201,
        )


def update_todo(request, todo_id):
    if request.method == "PUT":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        title = request.PUT.get("title", todo.title)
        description = request.PUT.get("description", todo.description)

        todo.title = title
        todo.description = description
        todo.save()

        TodoEvent.objects.create(
            todo=todo, event_type="Updated", details=("Updated Todo: {todo.title}")
        )

        return JsonResponse(
            {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "created_at": todo.created_at,
                "updated_at": todo.updated_at,
            }
        )


def toggle_todo(request, todo_id):
    if request.method == "PATCH":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        todo.completed = not todo.completed
        todo.save()

        event_type = "Checked" if todo.completed else "Unchecked"
        TodoEvent.objects.create(
            todo=todo, event_type=event_type, details=(
                "Todo: {todo.title}"))

        return JsonResponse(
            {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "created_at": todo.created_at,
                "updated_at": todo.updated_at,
            }
        )


def delete_todo(request, todo_id):
    if request.method == "DELETE":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        TodoEvent.objects.create(
            todo=todo, event_type="Deleted", 
            details=("Deleted Todo: {todo.title}")
        )
        todo.delete()

        return JsonResponse({"message": "Todo deleted successfully"}, status=200)


def todo_history(request, todo_id):
    if request.method == "GET":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        events = TodoEvent.objects.filter(todo=todo).order_by("-timestamp")
        events_data = [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "details": event.details,
            }
            for event in events
        ]

        return JsonResponse({"history": events_data})
