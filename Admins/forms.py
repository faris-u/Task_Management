from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from User.models import User, Task

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2", "role"]

class LoginForm(AuthenticationForm):
    pass

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date", "status"]
