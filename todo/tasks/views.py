from urllib.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator
from tasks.serializers import TaskSerializer
from tasks.models import Task, TaskHistory
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.urls import reverse
from core.constants import HISTORY_PAGE_SIZE, TASK_HISTORY_PAGE_SIZE


class TaskListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of tasks",
        responses={200: TaskSerializer(many=True), 404: "Not Found"},
    )
    def get(self, request: Request) -> Response:
        try:
            tasks = Task.objects.filter(is_active=True).order_by("created_at")
            # Pagination logic
            # paginator = Paginator(tasks, 3)  # Show 3 tasks per page
            # page_number = request.GET.get("page")
            # page_obj = paginator.get_page(page_number)

            return TemplateResponse(request, "index.html", {"tasks": tasks})
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Tasks not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new task",
        request_body=TaskSerializer,
        responses={
            201: "Created",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def post(self, request: Request) -> Response:
        serializer = TaskSerializer(data=request.data)
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
    @swagger_auto_schema(
        operation_description="Get details of a task",
        responses={200: TaskSerializer, 404: "Task not found"},
    )
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

    @swagger_auto_schema(
        operation_description="Update a task",
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            404: "Task not found",
            400: "Bad Request",
        },
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

    @swagger_auto_schema(
        operation_description="Delete a task",
        responses={200: "Task deleted", 404: "Task not found"},
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

    @swagger_auto_schema(
        operation_description="Toggle task completion status",
        responses={200: "Task updated", 404: "Task not found"},
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
    @swagger_auto_schema(
        operation_description="Get the history of a task",
        manual_parameters=[
            openapi.Parameter(
                "task_id",
                openapi.IN_PATH,
                description="ID of the task",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: "Task history retrieved successfully",
            404: "Task not found",
        },
    )
    def get(self, request, task_id) -> Response:
        try:
            # Fetch the task
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Fetch task history and order by `created_at`
        events = TaskHistory.objects.filter(task=task).order_by("-created_at")

        # Pagination logic
        paginator = Paginator(events, TASK_HISTORY_PAGE_SIZE)
        page_number = request.GET.get(
            "page"
        )  # Get the current page number from the request

        try:
            page_obj = paginator.get_page(page_number)  # Get the page object
        except PageNotAnInteger:
            page_obj = paginator.page(
                1
            )  # Return the first page if `page` is not an integer
        except EmptyPage:
            page_obj = paginator.page(
                paginator.num_pages
            )  # Return the last page if `page` is out of range

        # Prepare data for the template
        events_data = [
            {
                "event_type": event.event_type,
                "timestamp": event.created_at,
                "details": event.metadata,
            }
            for event in page_obj
        ]
        return TemplateResponse(
            request,
            "historycard.html",
            {
                "history_url": reverse(
                    "task_history",
                    kwargs={"task_id": task_id},
                ),
                "events_data": events_data,
                "page_obj": page_obj,
            },
        )


class TodoFormView(APIView):
    @swagger_auto_schema(
        operation_description="Get the form to edit a task",
        responses={200: "Edit form retrieved", 404: "Task not found"},
    )
    def get(self, request, task_id=None) -> Response:
        try:
            with transaction.atomic():
                task = get_object_or_404(Task, id=task_id, is_active=True)
            return TemplateResponse(request, "editform.html", {"tasks": task})
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LandingPageView(APIView):
    @swagger_auto_schema(
        operation_description="Get the landing page",
        responses={200: "Landing page rendered"},
    )
    def get(self, request: Request) -> Response:
        return TemplateResponse(request, "landingpage.html")


class GetEntireHistory(APIView):
    @swagger_auto_schema(
        operation_description="Get the entire task history with pagination",
        responses={
            200: "Task history retrieved successfully",
            404: "No task history found",
        },
    )
    def get(self, request: Request) -> Response:
        try:
            events = TaskHistory.objects.all().order_by("-created_at")
            print(events.values())
            # Pagination logic
            paginator = Paginator(events, HISTORY_PAGE_SIZE)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            # Return HTML response with task history wrapped in a div
            return TemplateResponse(
                request,
                "taskhistory.html",
                {
                    "history_url": reverse(
                        "entire_history",
                    ),
                    "events_data": page_obj,
                    "page_obj": page_obj,
                },
            )
        except TaskHistory.DoesNotExist:
            return JsonResponse(
                {"error": "No task history found."},
                status=404,
            )
