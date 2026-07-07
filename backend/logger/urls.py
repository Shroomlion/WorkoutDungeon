from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "logger"

urlpatterns = [
    path("", views.sheet, name="sheet"),
    path("log/", views.log_workout, name="log"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="logger/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
