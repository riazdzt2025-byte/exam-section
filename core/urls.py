from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("members/", views.members, name="members"),
    path("members/<int:pk>/password/", views.member_password, name="member_password"),
    path("members/<int:pk>/toggle/", views.member_toggle, name="member_toggle"),
    path("password/", views.MyPasswordChangeView.as_view(), name="password_change"),
    # সদস্যদের কাজ
    path("tasks/", views.tasks, name="tasks"),
    path("tasks/<int:owner_pk>/subjects/add/", views.subject_add, name="subject_add"),
    path(
        "tasks/subject/<int:pk>/toggle/<str:field>/",
        views.subject_toggle,
        name="subject_toggle",
    ),
    path("tasks/subject/<int:pk>/delete/", views.subject_delete, name="subject_delete"),
    path("tasks/<int:owner_pk>/todos/add/", views.todo_add, name="todo_add"),
    path("tasks/todo/<int:pk>/toggle/", views.todo_toggle, name="todo_toggle"),
    path("tasks/todo/<int:pk>/delete/", views.todo_delete, name="todo_delete"),
    # দৈনিক প্রতিবেদন
    path("report/daily/", views.daily_report, name="daily_report"),
    # এক্সেল
    path("excel/", views.excel_page, name="excel_page"),
    path("excel/export/", views.excel_export, name="excel_export"),
    path("excel/template/", views.excel_template, name="excel_template"),
    path("excel/import/", views.excel_import, name="excel_import"),
    # সেটিংস
    path("settings/", views.settings_page, name="settings_page"),
]
