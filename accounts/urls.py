from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import register

urlpatterns = [
    path("register/", register, name="register"),
    path("", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
