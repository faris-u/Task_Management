from django.contrib import admin
from django.urls import path
from Admins import views as admin_views
from User import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---- API -----
    path("register/", user_views.register_view, name="register"),
    path("login/", user_views.login_view, name="login"),
    path("tasks/", user_views.get_tasks, name="get_tasks"),
    path("tasks/<int:pk>/", user_views.update_task, name="update_task"),
    path("tasks/<int:pk>/report/", user_views.task_report, name="task_report"),

    # ---- ADMIN -----
    path("admins_register/", admin_views.admins_register_view, name="admins_register"),
    path("admins_login/", admin_views.admins_login_view, name="admins_login"),
    path("logout/", admin_views.logout_view, name="logout"),

    # Super Admin dashboard
    path("superadmin_dashboard/", admin_views.superadmin_dashboard, name="superadmin_dashboard"),
    path("superadmin_users/", admin_views.manage_users, name="manage_users"),
    path("superadmin_users/<int:user_id>/edit/", admin_views.edit_user, name="edit_user"),
    path("superadmin/users/<int:user_id>/delete/", admin_views.delete_user, name="delete_user"),

    # Admin dashboard
    path("admin_dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("admin_assign-task/", admin_views.assign_task, name="assign_task"),

    # Admin view task reports
    path("tasks/<int:task_id>/view_task_report/", admin_views.view_task_report, name="view_task_report"),
]
