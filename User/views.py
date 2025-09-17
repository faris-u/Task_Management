from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Task
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    TaskSerializer,
    TaskReportSerializer,
)


# Register
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all tasks for logged-in user
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


# Update task (status, completion report)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_task(request, pk):
    try:
        task = Task.objects.get(pk=pk, assigned_to=request.user)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    status_update = request.data.get("status")
    completion_report = request.data.get("completion_report")

    if status_update == "in_progress":
        task.status = "in_progress"
        task.started_at = timezone.now()

    elif status_update == "completed":
        if not completion_report:
            return Response(
                {"error": "Completion report required when completing a task"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.status = "completed"
        task.completion_report = completion_report
        task.completed_at = timezone.now()

        if task.started_at:
            duration = task.completed_at - task.started_at
            task.worked_hours = round(duration.total_seconds() / 3600, 2)
            task.worked_days = duration.days
        else:
            task.worked_hours = 0.0
            task.worked_days = 0

    else:
        task.status = status_update

    task.save()
    serializer = TaskSerializer(task)
    return Response(serializer.data)


# Get task report (admins & superadmins only)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_report(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role not in ["admin", "superadmin"]:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    if task.status != "completed":
        return Response(
            {"error": "Task not completed yet"}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = TaskReportSerializer(task)
    return Response(serializer.data)
