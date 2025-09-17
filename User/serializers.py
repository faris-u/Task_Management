from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Task


# Register User
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]  # allow role for testing

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["role"] = validated_data.get("role", "user")
        return super().create(validated_data)


# Login User
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
        }


# Tasks
class TaskSerializer(serializers.ModelSerializer):
    worked_days = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "status",
            "completion_report",
            "worked_hours",
            "worked_days",
        ]


class TaskReportSerializer(serializers.ModelSerializer):
    worked_days = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ["id", "completion_report", "worked_hours", "worked_days"]
