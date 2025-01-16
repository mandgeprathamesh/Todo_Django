from urllib.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from tasks.serializers import TaskSerializer
from tasks.models import Task, TaskHistory
from django.db import transaction


class TaskListCreateView(APIView):
    def get(self, request: Request) -> Response:
        try:
            tasks = Task.objects.filter(is_active=True).order_by("created_at")
            print("task are", tasks)
            return TemplateResponse(request, "index.html", {"tasks": tasks})
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Tasks not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request: Request) -> Response:
        # breakpoint()
        print(request.data)
        serializer = TaskSerializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid():
            task_data = serializer.validated_data
            try:
                with transaction.atomic():
                    task = Task.objects.create(
                        name=task_data["name"],
                        description=task_data.get("description", ""),
                        completed=task_data.get("completed", False),
                        is_active=task_data.get("is_active", True),
                    )
                    TaskHistory.objects.create(
                        task=task,
                        event_type="Created",
                        metadata=f"Created Task: {task.name}",
                    )
                return TemplateResponse(
                    request,
                    "todocard.html",
                    {"tasks": task},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return JsonResponse(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskDetailView(APIView):
    def get(self, request: Request, task_id) -> Response:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
            if request.accepted_renderer.format == "html":
                return TemplateResponse(
                    request,
                    "todocard.html",
                    {"task": task},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                    "is_active": task.is_active,
                },
                status=status.HTTP_200_OK,
            )
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request: Request, task_id) -> Response:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            try:
                with transaction.atomic():
                    task.name = validated_data.get("name", task.name)
                    task.description = validated_data.get(
                        "description", task.description
                    )
                    task.completed = validated_data.get(
                        "completed",
                        task.completed,
                    )
                    task.is_active = validated_data.get(
                        "is_active",
                        task.is_active,
                    )
                    task.save()

                    TaskHistory.objects.create(
                        task=task,
                        event_type="Updated",
                        metadata=f"Updated Task: {task.name}",
                    )

                return TemplateResponse(
                    request,
                    "todocard.html",
                    {"tasks": task},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return JsonResponse(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return JsonResponse(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, task_id) -> Response:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                task.is_active = False
                task.save()
                TaskHistory.objects.create(
                    task=task,
                    event_type="Deleted",
                    metadata=f"Soft-deleted Task: {task.name}",
                )
            return HttpResponse(
                '<div class="task">Task Deleted successfully</div>',
                content_type="text/html",
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, task_id) -> Response:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                task.completed = not task.completed
                task.save()
                event_type = "Checked" if task.completed else "Unchecked"
                TaskHistory.objects.create(
                    task=task,
                    event_type=event_type,
                    metadata=f"Tasks: {task.name}",
                )
            return TemplateResponse(request, "todocard.html", {"tasks": task})
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskHistoryView(APIView):
    def get(self, request, task_id) -> Response:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                events = TaskHistory.objects.filter(task=task).order_by(
                    "-created_at",
                )
                events_data = [
                    {
                        "event_type": event.event_type,
                        "timestamp": event.created_at,
                        "details": event.metadata,
                    }
                    for event in events
                ]
            return TemplateResponse(
                request,
                "historycard.html",
                {"events": events_data},
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TodoFormView(APIView):
    def get(self, request, task_id=None) -> Response:
        try:
            with transaction.atomic():
                task = get_object_or_404(Task, id=task_id, is_active=True)
            return TemplateResponse(request, "editform.html", {"tasks": task})
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
