from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from User.models import User, Task


# ----- Admin / SuperAdmin Registration -----
def admins_register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # superadmin or admin

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            if role not in ["superadmin", "admin"]:
                messages.error(request, "Invalid role selected")
            else:
                user = User.objects.create_user(username=username, password=password, role=role)
                messages.success(request, f"{role.capitalize()} created successfully")
                return redirect("admins_login")

    return render(request, "register.html")  # template: templates/register.html


# ----- Admin / SuperAdmin Login -----
def admins_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == "superadmin":
                login(request, user)
                return redirect("superadmin_dashboard")
            elif user.role == "admin":
                login(request, user)
                return redirect("admin_dashboard")  # use URL name, not path
            else:
                messages.error(request, "You are not authorized to login here")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

# ----- Logout -----
@login_required
def logout_view(request):
    logout(request)
    return redirect("admins_login")


# ----- SuperAdmin Dashboard -----
# ----- SuperAdmin Dashboard -----
@login_required
def superadmin_dashboard(request):
    if request.user.role != "superadmin":
        return redirect("admin_dashboard")

    total_users = User.objects.filter(role="user").count()
    total_admins = User.objects.filter(role="admin").count()
    total_tasks = Task.objects.all().count()

    # Only tasks assigned to normal users
    tasks = Task.objects.filter(assigned_to__role="user")

    return render(request, "superadmin_dashboard.html", {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_tasks": total_tasks,
        "tasks": tasks,
    })

# ----- Manage Users (SuperAdmin) -----
@login_required
def manage_users(request):
    if request.user.role != "superadmin":
        return redirect("admin_dashboard")

    users = User.objects.all()
    return render(request, "manage_users.html", {"users": users})


# ----- Edit User (SuperAdmin) -----
@login_required
def edit_user(request, user_id):
    if request.user.role != "superadmin":
        return redirect("admin_dashboard")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get("username")
        role = request.POST.get("role")

        if role not in ["superadmin", "admin", "user"]:
            messages.error(request, "Invalid role")
        else:
            user.username = username
            user.role = role
            user.save()
            messages.success(request, "User updated successfully")
            return redirect("manage_users")

    return render(request, "edit_user.html", {"user": user})



# ----- Delete User (SuperAdmin) -----
@login_required
def delete_user(request, user_id):
    if request.user.role != "superadmin":
        messages.error(request, "You are not authorized to delete users")
        return redirect("admin_dashboard")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully")
        return redirect("manage_users")

    return render(request, "delete_user.html", {"user": user})




# ----- Admin Dashboard -----
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("superadmin_dashboard")

    tasks = Task.objects.filter(assigned_to__role="user")
    return render(request, "admin_dashboard.html", {"tasks": tasks})


# ----- Assign Task (Admin) -----
@login_required
def assign_task(request):
    if request.user.role != "admin":
        return redirect("superadmin_dashboard")

    users = User.objects.filter(role="user")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        assigned_user_id = request.POST.get("assigned_to")
        assigned_user = get_object_or_404(User, id=assigned_user_id)

        Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            assigned_to=assigned_user,
        )
        messages.success(request, "Task assigned successfully")
        return redirect("admin_dashboard")

    return render(request, "assign_task.html", {"users": users})


# ----- View Task Report (Admin/SuperAdmin) -----
@login_required
def view_task_report(request, task_id):
    # Get the task object
    task = get_object_or_404(Task, id=task_id)

    # Restrict Admins: they can only view reports of tasks assigned to users
    if request.user.role == "admin" and task.assigned_to.role != "user":
        messages.error(request, "You can't view this task report")
        return redirect("admin_dashboard")

    # Restrict SuperAdmin: cannot view tasks assigned to admins or other superadmins
    if request.user.role == "superadmin" and task.assigned_to.role != "user":
        messages.error(request, "You can't view this task report")
        return redirect("superadmin_dashboard")

    # Optional: track hours worked if provided via POST (for admin updating a task)
    if request.method == "POST" and request.user.role in ["admin", "superadmin"]:
        worked_hours = request.POST.get("worked_hours")
        if worked_hours:
            try:
                task.worked_hours = float(worked_hours)
                task.save()
                messages.success(request, "Worked hours updated successfully")
            except ValueError:
                messages.error(request, "Invalid hours value")

    return render(request, "task_report.html", {"task": task})

