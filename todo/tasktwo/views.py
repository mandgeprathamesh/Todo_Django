# from django.http import HttpResponse, JsonResponse, QueryDict
# from django.shortcuts import get_object_or_404, render
# from .models import TodoEvent, Todos
# from django.views.decorators.csrf import csrf_exempt


# def todo_list(request):
#     if request.method == "GET":
#         todos = Todos.objects.order_by("-createdat")
#         for todo in todos:
#             print(todo.title)

#         return render(request, "index.html", {"todos": todos})


# @csrf_exempt
# def create_todo(request):
#     if request.method == "POST":
#         title = request.POST.get("title")
#         description = request.POST.get("description", "")

#         if not title:
#             return JsonResponse(
#                 data={"error": "Title is required"},
#                 status=400,
#             )

#         todo = Todos.objects.create(title=title, description=description)
#         TodoEvent.objects.create(
#             todo=todo,
#             event_type="Created",
#             details=f"Created Todo: {todo.title}",
#         )

#         return render(request, "todocard.html", {"todo": todo})


# @csrf_exempt
# def update_todo(request, todo_id):
#     print("entering in update endpoint")
#     if request.method == "PATCH":
#         try:
#             todo = Todos.objects.get(id=todo_id)
#         except Todos.DoesNotExist:
#             return JsonResponse({"error": "Todo not found"}, status=404)

#         data = QueryDict(request.body)
#         title = data.get("title", todo.title)
#         description = data.get("description", todo.description)
#         print("received titled is :-", title)
#         print("received description is :-", description)
#         todo.title = title
#         todo.description = description
#         todo.save()
#         print("after changing the  data is:-", todo.description)

#         TodoEvent.objects.create(
#             todo=todo,
#             event_type="Updated",
#             details=f"Updated Todo: {todo.title}",
#         )

#         return render(request, "todocard.html", {"todo": todo})


# @csrf_exempt
# def edit_todo_form(request, todo_id):
#     if request.method == "GET":
#         todo = get_object_or_404(Todos, id=todo_id)
#         return render(request, "editform.html", {"todo": todo})


# @csrf_exempt
# def toggle_todo(request, todo_id):
#     if request.method == "PATCH":
#         try:
#             todo = Todos.objects.get(id=todo_id)
#         except Todos.DoesNotExist:
#             return JsonResponse(data={"error": "Todo not found"}, status=404)

#         todo.completed = not todo.completed
#         todo.save()

#         event_type = "Checked" if todo.completed else "Unchecked"
#         TodoEvent.objects.create(
#             todo=todo,
#             event_type=event_type,
#             details=f"Todo: {todo.title}",
#         )

#         return render(
#             request,
#             "todocard.html",
#             {"todo": todo},
#         )


# @csrf_exempt
# def delete_todo(request, todo_id):
#     if request.method == "DELETE":
#         try:
#             todo = Todos.objects.get(id=todo_id)
#         except Todos.DoesNotExist:
#             return JsonResponse(data={"error": "Todo not found"}, status=404)

#         TodoEvent.objects.create(
#             todo=todo,
#             event_type="Deleted",
#             details=f"Deleted Todo: {todo.title}",
#         )
#         todo.delete()

#         return HttpResponse("", content_type="text/html")


# @csrf_exempt
# def todo_history(request, todo_id):
#     if request.method == "GET":
#         try:
#             todo = Todos.objects.get(id=todo_id)
#         except Todos.DoesNotExist:
#             return JsonResponse(data={"error": "Todo not found"}, status=404)

#         events = TodoEvent.objects.filter(todo=todo).order_by("-timestamp")
#         events_data = [
#             {
#                 "event_type": event.event_type,
#                 "timestamp": event.timestamp,
#                 "details": event.details,
#             }
#             for event in events
#         ]

#         return render(
#             request,
#             "historycard.html",
#             {"events": events_data},
#         )


from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import TodoEvent, Todos


@method_decorator(csrf_exempt, name="dispatch")
class TodoListView(View):
    def get(self, request):
        todos = Todos.objects.order_by("-createdat")
        for todo in todos:
            print(todo.title)

        return render(request, "index.html", {"todos": todos})


@method_decorator(csrf_exempt, name="dispatch")
class CreateTodoView(View):
    def post(self, request):
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


@method_decorator(csrf_exempt, name="dispatch")
class UpdateTodoView(View):
    def patch(self, request, todo_id):
        print("entering in update endpoint")
        try:
            todo = Todos.objects.get(id=todo_id)
        except Todos.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)

        data = QueryDict(request.body)
        title = data.get("title", todo.title)
        description = data.get("description", todo.description)
        print("received title is :-", title)
        print("received description is :-", description)
        todo.title = title
        todo.description = description
        todo.save()
        print("after changing the data is:-", todo.description)

        TodoEvent.objects.create(
            todo=todo,
            event_type="Updated",
            details=f"Updated Todo: {todo.title}",
        )

        return render(request, "todocard.html", {"todo": todo})


@method_decorator(csrf_exempt, name="dispatch")
class EditTodoFormView(View):
    def get(self, request, todo_id):
        todo = get_object_or_404(Todos, id=todo_id)
        return render(request, "editform.html", {"todo": todo})


@method_decorator(csrf_exempt, name="dispatch")
class ToggleTodoView(View):
    def patch(self, request, todo_id):
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


@method_decorator(csrf_exempt, name="dispatch")
class DeleteTodoView(View):
    def delete(self, request, todo_id):
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

        return HttpResponse("", content_type="text/html")


@method_decorator(csrf_exempt, name="dispatch")
class TodoHistoryView(View):
    def get(self, request, todo_id):
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

