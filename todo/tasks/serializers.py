from rest_framework import serializers
from tasks.models import Task
from core.constants import TASK_EVENT_TYPE


# Serializer for Task model
class TaskSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    completed = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)

    # Field-level validation for `name`
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "The name must be at least 3 characters long."
            )
        if len(value) > 255:
            raise serializers.ValidationError(
                "The name cannot exceed 255 characters.",
            )
        return value

    # Object-level validation for Task
    def validate(self, attrs):
        # Ensure completed tasks have a description
        if attrs.get("completed") and not attrs.get("description"):
            raise serializers.ValidationError(
                "A completed task must have a description."
            )

        # Ensure `is_active` cannot be False for a new task
        if not attrs.get("is_active"):
            raise serializers.ValidationError(
                "New tasks must be active by default.",
            )
        return attrs


# Serializer for TaskHistory model
class TaskHistorySerializer(serializers.Serializer):
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all()
    )  # Links to Task model
    event_type = serializers.ChoiceField(
        choices=TASK_EVENT_TYPE
    )  # Ensures valid event_type
    created_at = serializers.DateTimeField(read_only=True)
    metadata = serializers.CharField(required=False, allow_blank=True)

    # Object-level validation for TaskHistory
    def validate(self, attrs):
        # Ensure task exists
        if not attrs.get("task"):
            raise serializers.ValidationError("Task is required.")

        # Validate event_type against defined choices
        event_type = attrs.get("event_type")
        if event_type not in dict(TASK_EVENT_TYPE):
            raise serializers.ValidationError("Invalid event type.")

        return attrs
