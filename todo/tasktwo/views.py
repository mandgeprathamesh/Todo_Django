from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import TodoEvent, Todos
from django.views.decorators.csrf import csrf_exempt


def todo_list(request):
    if request.method == "GET":
        todos = Todos.objects.all()
        return render(request, "index.html", {"todos": todos})


@csrf_exempt
def create_todo(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")

        if not title:
            return JsonResponse(
                data={"error": "Title is required"},
                status=400,
            )

        todo = Todos.objects.create(title=title, description=description)
        TodoEvent.objects.create(
            todo=todo,
            event_type="Created",
            details=f"Created Todo: {todo.title}",
        )

        return render(request, "todocard.html", {"todo": todo})

        # return JsonResponse(
        #     data={
        #         "id": todo.id,
        #         "title": todo.title,
        #         "description": todo.description,
        #         "completed": todo.completed,
        #         "created_at": todo.createdat,
        #         "updated_at": todo.updatedat,
        #     },
        #     status=201,
        # )


@csrf_exempt
def update_todo(request, todo_id):
    print("entering in update endpoint")
    if request.method == "POST":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        title = request.POST.get("title", todo.title)
        description = request.POST.get("description", todo.description)
        todo.title = title
        todo.description = description
        todo.save()

        TodoEvent.objects.create(
            todo=todo,
            event_type="Updated",
            details=f"Updated Todo: {todo.title}",
        )

        return render(request, "todocard.html", {"todo": todo})
        # return JsonResponse(
        #     {
        #         "id": todo.id,
        #         "title": todo.title,
        #         "description": todo.description,
        #         "completed": todo.completed,
        #         "created_at": todo.createdat,
        #         "updated_at": todo.updatedat,
        #     }
        # )


@csrf_exempt
def edit_todo_form(request, todo_id):
    if request.method == "GET":
        todo = get_object_or_404(Todos, id=todo_id)
        return render(request, "editform.html", {"todo": todo})


@csrf_exempt
def toggle_todo(request, todo_id):
    if request.method == "PATCH":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse(data={"error": "Todo not found"}, status=404)

        todo.completed = not todo.completed
        todo.save()

        event_type = "Checked" if todo.completed else "Unchecked"
        TodoEvent.objects.create(
            todo=todo,
            event_type=event_type,
            details=f"Todo: {todo.title}",
        )

        return render(
            request,
            "todocard.html",
            {"todo": todo},
        )

        # return JsonResponse(
        #     data={
        #         "id": todo.id,
        #         "title": todo.title,
        #         "description": todo.description,
        #         "completed": todo.completed,
        #         "created_at": todo.createdat,
        #         "updated_at": todo.updatedat,
        #     }
        # )


@csrf_exempt
def delete_todo(request, todo_id):
    if request.method == "DELETE":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse(data={"error": "Todo not found"}, status=404)

        TodoEvent.objects.create(
            todo=todo,
            event_type="Deleted",
            details=f"Deleted Todo: {todo.title}",
        )
        todo.delete()

        return HttpResponse("<div></div>", content_type="text/html")


@csrf_exempt
def todo_history(request, todo_id):
    if request.method == "GET":
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse(data={"error": "Todo not found"}, status=404)

        events = TodoEvent.objects.filter(todo=todo).order_by("-timestamp")
        events_data = [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "details": event.details,
            }
            for event in events
        ]

        return render(
            request,
            "historycard.html",
            {"events": events_data},
        )

        # return JsonResponse(data={"history": events_data})
