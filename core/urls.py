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
]
